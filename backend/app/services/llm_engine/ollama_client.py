import requests
import json
from typing import Dict, List, Optional
from app.core.config import settings

class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict:
        """Generate completion from Ollama Gemma 2:2b"""
        
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
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
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
        
        prompt = f"""Data Profile:
{json.dumps(data_profile, indent=2)}

Quality Issues Detected:
{json.dumps(quality_issues, indent=2)}

Provide:
1. Root cause analysis for each issue
2. Recommended cleaning strategies with specific steps
3. Expected impact of each strategy
4. Risk assessment and precautions

Format your response as valid JSON with this structure:
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
            max_tokens=3000
        )
        
        return self._parse_response(response.get('response', ''))
    
    def _parse_response(self, response: str) -> Dict:
        """Parse LLM response into structured format"""
        try:
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
        except json.JSONDecodeError:
            return {
                "raw_response": response,
                "parsed": False
            }