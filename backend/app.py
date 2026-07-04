from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
import logging
from typing import Dict
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="YouTube Transcript RAG API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store transcript data in memory (for production, use database)
transcript_cache: Dict[str, dict] = {}

# Pydantic Models
class TranscriptRequest(BaseModel):
    video_id: str
    api_token: str

class QuestionRequest(BaseModel):
    video_id: str
    question: str
    api_token: str

class TranscriptResponse(BaseModel):
    video_id: str
    transcript: str
    chunks_count: int

class AnswerResponse(BaseModel):
    video_id: str
    question: str
    answer: str

# Utility Functions
# def get_youtube_transcript(video_id: str) -> str:
#     """Fetch transcript from YouTube video"""
#     try:
#         ytt_api = YouTubeTranscriptApi()
#         transcript_list = ytt_api.list(video_id)
#         transcript_obj = transcript_list.find_transcript(['en'])
#         fetched_transcript = transcript_obj.fetch()
#         transcript_text = " ".join(chunk["text"] for chunk in fetched_transcript)
#         return transcript_text
#     except TranscriptsDisabled:
#         raise HTTPException(status_code=400, detail="Transcripts are disabled for this video")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Failed to fetch transcript: {str(e)}")
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# def get_youtube_transcript(video_id: str) -> str:
#     try:
#         transcript = YouTubeTranscriptApi.get_transcript(video_id)

#         transcript_text = " ".join(
#             chunk["text"] for chunk in transcript
#         )

#         return transcript_text

#     except TranscriptsDisabled:
#         raise HTTPException(
#             status_code=400,
#             detail="Transcripts are disabled for this video"
#         )

#     except Exception as e:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Failed to fetch transcript: {str(e)}"
        # )


def get_youtube_transcript(video_id: str) -> str:
    try:
        logger.info(f"Fetching transcript for: {video_id}")

        ytt_api = YouTubeTranscriptApi()

        transcript_list = ytt_api.list(video_id)

        # Try English first
        try:
            transcript_obj = transcript_list.find_transcript(["en"])
        except NoTranscriptFound:
            # Otherwise translate the first translatable transcript
            transcript_obj = None
            for transcript in transcript_list:
                if transcript.is_translatable:
                    transcript_obj = transcript.translate("en")
                    break

            if transcript_obj is None:
                raise NoTranscriptFound(video_id)

        fetched_transcript = transcript_obj.fetch()

        transcript_text = " ".join(
            chunk.text for chunk in fetched_transcript
        )

        return transcript_text

    except TranscriptsDisabled:
        raise HTTPException(
            status_code=400,
            detail="Transcripts are disabled for this video."
        )

    except NoTranscriptFound:
        raise HTTPException(
            status_code=400,
            detail="No transcript available."
        )

    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )



def create_rag_chain(chunks, api_token: str):
    """Create RAG chain for question answering"""
    try:
        # Create embeddings
        embedding = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5"
        )
        
        # Create vector store
        vector_store = FAISS.from_documents(chunks, embedding)
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        
        # Setup LLM
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_token
        llm = HuggingFaceEndpoint(
            repo_id="Qwen/Qwen2.5-7B-Instruct",
            task="conversational",
            temperature=0.7,
        )
        llm = ChatHuggingFace(llm=llm)
        
        # Create prompt
        prompt = PromptTemplate(
            template="""You are a helpful assistant.
Answer ONLY from the provided transcript context.
If the context is insufficient, just say you don't know.

Context:
{context}

Question: {question}
Answer:""",
            input_variables=['context', 'question']
        )
        
        # Format documents function
        def format_docs(retrieved_docs):
            return "\n\n".join(doc.page_content for doc in retrieved_docs)
        
        # Build chain
        chain = (
            RunnableParallel({
                'context': retriever | RunnableLambda(format_docs),
                'question': RunnablePassthrough()
            })
            | prompt
            | llm
            | StrOutputParser()
        )
        
        return chain
    except Exception as e:
        logger.error(f"Error creating RAG chain: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create RAG chain: {str(e)}")

# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "YouTube Transcript RAG API"}

@app.post("/api/load-transcript", response_model=TranscriptResponse)
async def load_transcript(request: TranscriptRequest):
    """Load and process YouTube transcript"""
    try:
        logger.info(f"Loading transcript for video: {request.video_id}")
        
        # Check cache first
        if request.video_id in transcript_cache:
            cached = transcript_cache[request.video_id]
            logger.info(f"Using cached transcript for {request.video_id}")
            return TranscriptResponse(
                video_id=request.video_id,
                transcript=cached['transcript'],
                chunks_count=cached['chunks_count']
            )
        
        # Fetch transcript
        transcript_text = get_youtube_transcript(request.video_id)
        
        # Split transcript
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.create_documents([transcript_text])
        
        # Cache the data
        transcript_cache[request.video_id] = {
            'transcript': transcript_text,
            'chunks': chunks,
            'chunks_count': len(chunks),
            'api_token': request.api_token,
            'chain': None  # Will be created on demand
        }
        
        logger.info(f"Successfully loaded transcript for {request.video_id}: {len(chunks)} chunks")
        
        return TranscriptResponse(
            video_id=request.video_id,
            transcript=transcript_text,
            chunks_count=len(chunks)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ask-question", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Answer a question based on transcript"""
    try:
        logger.info(f"Answering question for video {request.video_id}: {request.question}")
        
        # Check if transcript is cached
        if request.video_id not in transcript_cache:
            raise HTTPException(status_code=400, detail="Transcript not loaded. Please load it first.")
        
        cached = transcript_cache[request.video_id]
        
        # Create chain if not already created
        if cached['chain'] is None:
            logger.info(f"Creating RAG chain for {request.video_id}")
            cached['chain'] = create_rag_chain(cached['chunks'], request.api_token)
        
        # Get answer
        chain = cached['chain']
        answer = chain.invoke(request.question)
        
        logger.info(f"Generated answer for {request.video_id}")
        
        return AnswerResponse(
            video_id=request.video_id,
            question=request.question,
            answer=answer
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear-cache")
async def clear_cache():
    """Clear transcript cache"""
    global transcript_cache
    count = len(transcript_cache)
    transcript_cache = {}
    logger.info(f"Cleared cache with {count} entries")
    return {"message": f"Cache cleared. Removed {count} entries"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
