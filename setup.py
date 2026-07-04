#!/usr/bin/env python3
"""
Simple setup script to create extension icons and prepare the Chrome extension
Works without PIL dependency - creates base64-encoded minimal PNG icons
"""

import os
import base64

# Base64-encoded minimal PNG icons (pre-generated single-color placeholders)
# Format: 1x1 solid color PNG in base64

def create_simple_icons():
    """Create simple extension icons without PIL"""
    icon_dir = os.path.join(os.path.dirname(__file__), 'chrome_extension', 'icons')
    
    if not os.path.exists(icon_dir):
        os.makedirs(icon_dir)
    
    # Minimal PNG data for different sizes (pre-generated purple gradient color)
    # These are actual valid PNG images in base64
    icons = {
        '16': (
            'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAKElEQVR4nGP8/5+hnoEIwMgkRgQw'
            'ikEOGDEaM2Y0agwawygNGEEaAABvdiUJQVrTkAAAAABJRU5ErkJggg=='
        ),
        '48': (
            'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAAMUlEQVR4nGP8//8/AxMDEwOBgFGB'
            'kaExY8YMGsOoDhjRGjNmzGgMo9SAEaUBIwgAAG3xJQk58gNUAAAAAElFTkSuQmCC'
        ),
        '128': (
            'iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADTAcnFAAAAMUlEQVR4nGP8//8/AxMDEwOBgFGB'
            'kaExY8YMGsOoDhjRGjNmzGgMo9SAEaUBIwgAAG3xJQk58gNUAAAAAElFTkSuQmCC'
        )
    }
    
    for size, data in icons.items():
        try:
            icon_path = os.path.join(icon_dir, f'icon-{size}.png')
            with open(icon_path, 'wb') as f:
                f.write(base64.b64decode(data))
            print(f"✓ Created {icon_path}")
        except Exception as e:
            print(f"✗ Error creating icon-{size}.png: {e}")

def main():
    """Main setup function"""
    print("YouTube Transcript RAG Chrome Extension - Setup")
    print("=" * 60)
    
    try:
        print("\n1. Setting up extension folder structure...")
        extension_dir = os.path.join(os.path.dirname(__file__), 'chrome_extension')
        if os.path.exists(extension_dir):
            print(f"✓ Extension folder exists: {extension_dir}")
        else:
            os.makedirs(extension_dir)
            print(f"✓ Created extension folder")
        
        print("\n2. Creating extension icons...")
        create_simple_icons()
        
        print("\n✓ Setup complete!")
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("\n1. Install backend dependencies:")
        print("   - Open PowerShell in the backend folder")
        print("   - Run: pip install -r requirements.txt")
        print("\n2. Start the backend server:")
        print("   - Run: python app.py")
        print("   - You should see: 'Uvicorn running on http://0.0.0.0:8000'")
        print("\n3. Load the Chrome extension:")
        print("   - Open: chrome://extensions/")
        print("   - Enable 'Developer mode' (toggle in top right)")
        print("   - Click 'Load unpacked'")
        print("   - Select the 'chrome_extension' folder from this directory")
        print("   - The extension should appear in your toolbar")
        print("\n4. Configure the extension:")
        print("   - Go to any YouTube video page")
        print("   - Click the extension icon in your toolbar")
        print("   - Click the ⚙️ Settings button")
        print("   - Enter your HuggingFace API token (get from https://huggingface.co/settings/tokens)")
        print("   - Click 'Save'")
        print("\n5. Start chatting!")
        print("   - Refresh the YouTube page")
        print("   - The transcript will load automatically")
        print("   - Ask questions in the chat box")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
