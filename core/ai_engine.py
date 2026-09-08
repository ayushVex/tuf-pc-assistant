"""
AI Engine Module
Handles LLM inference for natural language processing
"""

import logging
import subprocess
import requests
import json
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class AIEngine:
    """Handle AI/LLM inference using Ollama"""
    
    def __init__(self, config):
        """
        Initialize AI engine
        
        Args:
            config (ConfigManager): Configuration object
        """
        self.config = config
        self.model_name = config.get('ai.model_name', 'mistral')
        self.model_type = config.get('ai.model_type', 'ollama')
        self.temperature = config.get('ai.temperature', 0.7)
        self.max_tokens = config.get('ai.max_tokens', 256)
        self.conversation_history = []
        self.ollama_ready = False
        
        logger.info(f"🤖 AI Engine initialized (model: {self.model_name})")
        
        # Initialize based on model type
        if self.model_type == 'ollama':
            self._init_ollama()
    
    def _init_ollama(self):
        """Initialize Ollama"""
        logger.info("🔄 Checking Ollama installation...")
        
        try:
            # Check if Ollama is installed
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Ollama found: {result.stdout.strip()}")
            
            # Start Ollama server in background
            self._start_ollama_server()
            
            # Wait for server to be ready
            self.ollama_ready = self._wait_for_ollama(timeout=30)
            
            if self.ollama_ready:
                logger.info("✅ Ollama server ready")
                self._ensure_model_loaded()
        
        except FileNotFoundError:
            logger.error("❌ Ollama not found. Please install from https://ollama.ai")
            logger.info("📥 Download and install Ollama, then run: ollama pull mistral")
        except Exception as e:
            logger.error(f"❌ Ollama initialization error: {e}")
    
    def _start_ollama_server(self):
        """Start Ollama server"""
        try:
            # Check if already running
            try:
                requests.get('http://localhost:11434/api/tags', timeout=2)
                logger.info("✅ Ollama server already running")
                return
            except:
                pass
            
            logger.info("🚀 Starting Ollama server...")
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            logger.info("🔄 Ollama server starting...")
        
        except Exception as e:
            logger.error(f"❌ Could not start Ollama: {e}")
    
    def _wait_for_ollama(self, timeout=30):
        """Wait for Ollama server to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=2)
                if response.status_code == 200:
                    return True
            except:
                pass
            
            time.sleep(1)
        
        return False
    
    def _ensure_model_loaded(self):
        """Ensure the required model is loaded"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            models = response.json().get('models', [])
            model_names = [m.get('name', '').split(':')[0] for m in models]
            
            if self.model_name in model_names:
                logger.info(f"✅ Model {self.model_name} is available")
            else:
                logger.warning(f"⚠️ Model {self.model_name} not found")
                logger.info(f"📥 To download, run: ollama pull {self.model_name}")
        
        except Exception as e:
            logger.error(f"❌ Error checking models: {e}")
    
    def generate_response(self, prompt, use_history=True):
        """
        Generate response using LLM
        
        Args:
            prompt (str): User input/question
            use_history (bool): Include conversation history
        
        Returns:
            str: Generated response
        """
        if not self.ollama_ready:
            logger.error("❌ Ollama not ready")
            return "I'm having trouble connecting to my AI. Please check your internet and Ollama installation."
        
        try:
            # Build context with history
            messages = []
            
            if use_history:
                messages.extend(self.conversation_history[-6:])  # Last 3 exchanges
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            logger.info(f"🤖 Generating response for: {prompt[:50]}...")
            
            # Call Ollama API
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.model_name,
                    'prompt': prompt,
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens,
                    'stream': False,
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('response', '').strip()
                
                if text:
                    logger.info(f"✅ Generated: {text[:50]}...")
                    
                    # Add to history
                    self.conversation_history.append({"role": "user", "content": prompt})
                    self.conversation_history.append({"role": "assistant", "content": text})
                    
                    return text
            
            logger.error(f"❌ API error: {response.status_code}")
            return "Sorry, I couldn't generate a response. Please try again."
        
        except requests.exceptions.Timeout:
            logger.error("❌ Request timeout - model response took too long")
            return "That's taking too long. Try a simpler question."
        except requests.exceptions.ConnectionError:
            logger.error("❌ Connection error - Ollama server not responding")
            return "I can't connect to my AI. Is Ollama running?"
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            return f"Error: {str(e)}"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("✅ Conversation history cleared")
    
    def get_summary(self):
        """Get summary of conversation"""
        if not self.conversation_history:
            return "No conversation yet"
        
        return f"{len(self.conversation_history)//2} messages"
    
    def cleanup(self):
        """Cleanup AI engine"""
        try:
            self.clear_history()
            logger.info("✅ AI engine cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")
