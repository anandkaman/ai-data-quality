import subprocess
import asyncio
import logging
from typing import Optional, List, Dict
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelManager:
    """Manage Ollama model switching and status"""
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        self.ollama_base_url = ollama_base_url
        self.current_process: Optional[subprocess.Popen] = None
        self.current_model: str = "gemma2:2b"
    
    async def get_available_models(self) -> List[Dict]:
        """Get list of available Ollama models"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [
                        {
                            "name": model["name"],
                            "size": model.get("size", 0),
                            "modified": model.get("modified_at", ""),
                            "digest": model.get("digest", "")
                        }
                        for model in data.get("models", [])
                    ]
                return []
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    async def check_model_exists(self, model_name: str) -> bool:
        """Check if model is already pulled"""
        models = await self.get_available_models()
        return any(m["name"] == model_name for m in models)
    
    async def pull_model_stream(self, model_name: str):
        """Pull model with streaming progress"""
        cmd = ["ollama", "pull", model_name]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                text=True
            )
            
            async for line in process.stdout:
                line = line.strip()
                if line:
                    yield {
                        "type": "log",
                        "content": line,
                        "timestamp": datetime.now().isoformat()
                    }
            
            await process.wait()
            
            if process.returncode == 0:
                yield {
                    "type": "success",
                    "content": f"Model {model_name} pulled successfully",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                yield {
                    "type": "error",
                    "content": f"Failed to pull model {model_name}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            yield {
                "type": "error",
                "content": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def stop_current_model(self):
        """Stop currently running model"""
        try:
            # Ollama automatically manages model lifecycle
            # We just need to unload the current model from memory
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={"model": self.current_model, "keep_alive": 0}
                )
            logger.info(f"Stopped model: {self.current_model}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop model: {e}")
            return False
    
    async def switch_model(self, new_model: str):
        """Switch to a different model"""
        try:
            # Stop current model
            await self.stop_current_model()
            
            # Update current model
            self.current_model = new_model
            
            # Warm up new model
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": new_model,
                        "prompt": "Hello",
                        "stream": False
                    }
                )
            
            logger.info(f"Switched to model: {new_model}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch model: {e}")
            return False
    
    def get_current_model(self) -> str:
        """Get currently active model"""
        return self.current_model

# Global instance
model_manager = ModelManager()