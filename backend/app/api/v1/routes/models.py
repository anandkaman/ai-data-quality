from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
import json
from app.services.llm_engine.model_manager import model_manager

router = APIRouter()

class ModelSwitchRequest(BaseModel):
    model_name: str

class ModelResponse(BaseModel):
    models: List[Dict]
    current_model: str

@router.get("/available", response_model=ModelResponse)
async def get_available_models():
    """Get list of available models"""
    try:
        models = await model_manager.get_available_models()
        current = model_manager.get_current_model()
        
        return ModelResponse(
            models=models,
            current_model=current
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current")
async def get_current_model():
    """Get currently active model"""
    return {
        "model": model_manager.get_current_model()
    }

@router.post("/pull/{model_name}")
async def pull_model(model_name: str):
    """Pull a new model with streaming progress"""
    
    async def event_generator():
        try:
            async for event in model_manager.pull_model_stream(model_name):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.post("/switch")
async def switch_model(request: ModelSwitchRequest):
    """Switch to a different model"""
    
    try:
        # Check if model exists
        model_exists = await model_manager.check_model_exists(request.model_name)
        
        if not model_exists:
            return {
                "success": False,
                "message": f"Model {request.model_name} not found. Please pull it first.",
                "requires_pull": True
            }
        
        # Switch model
        success = await model_manager.switch_model(request.model_name)
        
        if success:
            return {
                "success": True,
                "message": f"Switched to {request.model_name}",
                "current_model": request.model_name
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to switch model")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_model():
    """Stop current model"""
    try:
        success = await model_manager.stop_current_model()
        if success:
            return {"message": "Model stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop model")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))