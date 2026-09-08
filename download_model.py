"""
Download and setup AI models
"""

import subprocess
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def check_ollama():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("❌ Ollama not found")
        return False


def download_model(model_name='mistral'):
    """
    Download AI model using Ollama
    
    Args:
        model_name (str): Model to download (mistral, phi, orca-mini)
    """
    print(f"\n📥 Downloading {model_name} model...")
    print("This may take several minutes depending on your internet speed.\n")
    
    try:
        subprocess.run(['ollama', 'pull', model_name], check=True)
        print(f"\n✅ Model {model_name} downloaded successfully!")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to download {model_name}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("  🤖 TUF PC Assistant - Model Setup")
    print("="*60 + "\n")
    
    # Check Ollama
    if not check_ollama():
        print("\n📥 Please install Ollama from: https://ollama.ai")
        print("Then run this script again.")
        sys.exit(1)
    
    # Select model
    print("\n🎯 Available models:")
    print("  1. mistral (7B, 4GB) - Recommended - Balanced speed/quality")
    print("  2. phi (2.7B, 1.6GB) - Fastest - Lightweight")
    print("  3. orca-mini (3.3B, 2GB) - Good quality")
    print("  4. tinyllama (1.1B, 1GB) - Minimal")
    
    try:
        choice = input("\nSelect model (1-4) [default: 1]: ").strip() or "1"
        
        models = {
            '1': 'mistral',
            '2': 'phi',
            '3': 'orca-mini',
            '4': 'tinyllama',
        }
        
        model_name = models.get(choice, 'mistral')
        
        # Download model
        if download_model(model_name):
            print("\n✅ Setup complete! You can now run: python main.py")
        else:
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
