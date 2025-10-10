import requests
import json
import logging
from typing import Dict, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
        self._session_counter = 0  # Track number of requests
        logger.info(f"Initialized OllamaClient with model: {self.model}")
    
    async def clear_context(self):
        """Force clear model context to free memory"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "keep_alive": 0  # Unload model immediately
                },
                timeout=10
            )
            logger.info("Cleared Ollama context - memory freed")
            return True
        except Exception as e:
            logger.warning(f"Failed to clear context: {e}")
            return False
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000  # Reduced from 2000 for 8GB RAM
    ) -> Dict:
        """Generate completion from Ollama Gemma 2:2b with memory management"""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            # Increment request counter
            self._session_counter += 1
            logger.info(f"Request #{self._session_counter} to Ollama")
            
            # Make request
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=settings.OLLAMA_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            
            # Clear context every 3 requests to prevent memory buildup
            if self._session_counter >= 3:
                logger.warning(f" Reached {self._session_counter} requests - clearing context")
                await self.clear_context()
                self._session_counter = 0  # Reset counter
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return {
                "response": "Request timed out. Model may be overloaded. Try again.",
                "error": True
            }
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to Ollama")
            return {
                "response": "Cannot connect to Ollama. Ensure it's running on port 11434.",
                "error": True
            }
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return {
                "response": f"Error generating response: {str(e)}",
                "error": True
            }
    
    async def generate_cleaning_strategy(
        self,
        data_profile: Dict,
        quality_issues: List[Dict]
    ) -> Dict:
        """Generate data cleaning recommendations using Gemma 2:2b"""
        
        system_prompt = """You are an expert data scientist specializing in data quality.
Analyze the provided data profile and quality issues, then recommend specific
cleaning strategies with detailed reasoning. Respond in valid JSON format only."""
        
        # Limit prompt size for 8GB RAM
        # Only include essential info
        prompt = f"""Data Profile Summary:
- Rows: {data_profile.get('row_count', 'N/A')}
- Columns: {data_profile.get('column_count', 'N/A')}
- Data Types: {data_profile.get('data_types', 'N/A')}

Quality Issues (Top 5):
{json.dumps(quality_issues[:5], indent=2)}

Provide concise recommendations in JSON:
{{
  "priority_ranking": [
    {{"issue": "...", "severity": "high/medium/low", "impact": "..."}}
  ],
  "strategies": [
    {{
      "issue_type": "...",
      "affected_columns": [...],
      "root_cause": "...",
      "recommended_approach": {{
        "method": "...",
        "steps": [...]
      }},
      "expected_improvement": "...",
      "risks": [...]
    }}
  ],
  "implementation_order": [...],
  "success_metrics": {{}}
}}"""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=2000  # Allow more tokens for this specific use case
        )
        
        return self._parse_response(response.get('response', ''))
    
    def _parse_response(self, response: str) -> Dict:
        """Parse LLM response into structured format"""
        try:
            # Find JSON in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    "raw_response": response,
                    "parsed": False
                }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {
                "raw_response": response,
                "parsed": False,
                "error": str(e)
            }
    
    def reset_counter(self):
        """Manually reset request counter"""
        self._session_counter = 0
        logger.info("Request counter reset")
    
    def get_request_count(self) -> int:
        """Get current request count"""
        return self._session_counter
