#!/usr/bin/env python3
"""
Gemini Client - Sử dụng google-genai SDK mới
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client cho Gemini API sử dụng google-genai SDK"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-pro"):
        self.api_key = api_key
        self.model = model
        self.client = None
        self.initialized = False
        
        if not GEMINI_AVAILABLE:
            logger.error("❌ google-genai package not available")
            logger.error("   Run: pip install google-genai>=1.0.0")
            return
        
        try:
            self.client = genai.Client(api_key=api_key)
            self.initialized = True
            logger.info("✅ Gemini client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
    
    async def generate_response(self, 
                              prompt: str, 
                              system_message: str = None,
                              response_format: str = "text/plain",
                              use_thinking: bool = True) -> Optional[str]:
        """Generate response từ Gemini"""
        if not self.initialized:
            logger.error("❌ Gemini client not initialized")
            return None
        
        try:
            # Prepare content
            parts = []
            
            # Add system message if provided
            if system_message:
                parts.append(types.Part.from_text(text=f"System: {system_message}\n\n"))
            
            # Add main prompt
            parts.append(types.Part.from_text(text=prompt))
            
            contents = [
                types.Content(
                    role="user",
                    parts=parts,
                ),
            ]
            
            # Configure generation
            config = types.GenerateContentConfig(
                response_mime_type=response_format,
            )
            
            # Add thinking config if enabled (for complex reasoning)
            if use_thinking:
                config.thinking_config = types.ThinkingConfig(
                    thinking_budget=-1,  # Unlimited thinking budget
                )
            
            # Generate response
            logger.info("🤖 Sending request to Gemini...")
            
            # Use streaming for better performance
            response_text = ""
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=config,
            ):
                if chunk.text:
                    response_text += chunk.text
            
            logger.info(f"✅ Gemini response received ({len(response_text)} chars)")
            return response_text.strip()
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                logger.warning(f"⚠️ Gemini quota exceeded, will retry later: {e}")
            else:
                logger.error(f"❌ Gemini API error: {e}")
            return None
    
    async def generate_json_response(self, 
                                   prompt: str, 
                                   system_message: str = None,
                                   use_thinking: bool = True) -> Optional[Dict[str, Any]]:
        """Generate JSON response từ Gemini"""
        response = await self.generate_response(
            prompt=prompt,
            system_message=system_message,
            response_format="application/json",
            use_thinking=use_thinking
        )
        
        if not response:
            return None
        
        try:
            # Parse JSON response
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response[:200]}...")
            return None
    
    def is_available(self) -> bool:
        """Check if Gemini client is available and initialized"""
        return GEMINI_AVAILABLE and self.initialized

class GeminiManager:
    """Manager for multiple Gemini clients với failover"""
    
    def __init__(self, config_path: str = "ai/gemini_config.json"):
        self.config_path = config_path
        self.clients = {}
        self.current_client_key = None
        self.request_count = {}
        self.config = {}
        
        self.load_config()
        self.initialize_clients()
    
    def load_config(self):
        """Load configuration từ file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info("✅ Gemini config loaded")
            else:
                # Create default config
                self.create_default_config()
        except Exception as e:
            logger.error(f"Error loading Gemini config: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        # Ưu tiên environment variables, fallback to default
        self.config = {
            "gemini_apis": {
                "primary": {
                    "api_key": os.environ.get("GEMINI_API_KEY", "your_api_key_here"),
                    "enabled": True,
                    "daily_limit": 1500,
                    "model": "gemini-2.5-pro"
                },
                "secondary": {
                    "api_key": os.environ.get("GEMINI_API_KEY_2", "your_secondary_key"),
                    "enabled": False,
                    "daily_limit": 1500,
                    "model": "gemini-2.5-pro"
                },
                "backup": {
                    "api_key": os.environ.get("GEMINI_API_KEY_3", "your_backup_key"),
                    "enabled": False,
                    "daily_limit": 1000,
                    "model": "gemini-2.5-flash"
                }
            },
            "rotation": {
                "enabled": True,
                "threshold": 100,
                "reset_hour": 0
            },
            "retry": {
                "max_attempts": 3,
                "delay": 1.0
            }
        }
        
        # Save default config
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("✅ Default Gemini config created")
        except Exception as e:
            logger.error(f"Error saving default config: {e}")
    
    def initialize_clients(self):
        """Initialize Gemini clients"""
        if not self.config.get("gemini_apis"):
            logger.warning("⚠️ No Gemini API config found")
            return
        
        for key, api_config in self.config["gemini_apis"].items():
            if not api_config.get("enabled", True):  # Default enabled = True
                logger.info(f"⏸️ Gemini client '{key}' disabled in config")
                continue
            
            api_key = api_config.get("api_key", "")
            if not api_key or api_key in ["your_api_key_here", "your_secondary_key", "your_backup_key"]:
                logger.warning(f"⚠️ Invalid API key for '{key}': {api_key[:10] if api_key else 'None'}...")
                continue
                
            model = api_config.get("model", "gemini-2.5-pro")
            logger.info(f"🔧 Initializing Gemini client '{key}' with model '{model}'...")
            
            client = GeminiClient(api_key, model)
            
            if client.is_available():
                self.clients[key] = client
                self.request_count[key] = 0
                
                if not self.current_client_key:
                    self.current_client_key = key
                
                logger.info(f"✅ Gemini client '{key}' initialized successfully")
            else:
                logger.error(f"❌ Failed to initialize client '{key}' - SDK not available")
        
        if not self.clients:
            logger.error("❌ No Gemini clients available - check API keys and SDK installation")
        else:
            logger.info(f"🚀 {len(self.clients)} Gemini client(s) ready: {list(self.clients.keys())}")
    
    def get_current_client(self) -> Optional[GeminiClient]:
        """Get current active client"""
        if not self.current_client_key or self.current_client_key not in self.clients:
            self._select_best_client()
        
        return self.clients.get(self.current_client_key)
    
    def _select_best_client(self):
        """Select best available client"""
        if not self.clients:
            return
        
        # Find client with lowest usage
        best_key = min(self.clients.keys(), 
                      key=lambda k: self.request_count.get(k, 0))
        self.current_client_key = best_key
        logger.info(f"🔄 Switched to client: {best_key}")
    
    async def generate_response(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate response với auto-failover"""
        max_attempts = self.config.get("retry", {}).get("max_attempts", 3)
        delay = self.config.get("retry", {}).get("delay", 1.0)
        
        for attempt in range(max_attempts):
            client = self.get_current_client()
            if not client:
                logger.error("❌ No Gemini clients available")
                return None
            
            try:
                response = await client.generate_response(prompt, **kwargs)
                if response:
                    # Track usage
                    self.request_count[self.current_client_key] += 1
                    return response
                
            except Exception as e:
                logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
                
                # Try next client on failure
                self._rotate_client()
                
                if attempt < max_attempts - 1:
                    await asyncio.sleep(delay)
        
        logger.error("❌ All Gemini clients failed")
        return None
    
    async def generate_json_response(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Generate JSON response với auto-failover"""
        max_attempts = self.config.get("retry", {}).get("max_attempts", 3)
        delay = self.config.get("retry", {}).get("delay", 1.0)
        
        for attempt in range(max_attempts):
            client = self.get_current_client()
            if not client:
                logger.error("❌ No Gemini clients available")
                return None
            
            try:
                response = await client.generate_json_response(prompt, **kwargs)
                if response:
                    # Track usage
                    self.request_count[self.current_client_key] += 1
                    return response
                
            except Exception as e:
                logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
                
                # Try next client on failure
                self._rotate_client()
                
                if attempt < max_attempts - 1:
                    await asyncio.sleep(delay)
        
        logger.error("❌ All Gemini clients failed")
        return None
    
    def _rotate_client(self):
        """Rotate to next available client"""
        if len(self.clients) <= 1:
            return
        
        keys = list(self.clients.keys())
        current_index = keys.index(self.current_client_key) if self.current_client_key in keys else 0
        next_index = (current_index + 1) % len(keys)
        
        self.current_client_key = keys[next_index]
        logger.info(f"🔄 Rotated to client: {self.current_client_key}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get manager status"""
        return {
            "available_clients": len(self.clients),
            "current_client": self.current_client_key,
            "request_counts": self.request_count.copy(),
            "gemini_sdk_available": GEMINI_AVAILABLE
        }

# Global instance
_gemini_manager = None

def get_gemini_manager() -> GeminiManager:
    """Get global Gemini manager instance"""
    global _gemini_manager
    if _gemini_manager is None:
        _gemini_manager = GeminiManager()
    return _gemini_manager