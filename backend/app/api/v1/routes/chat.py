from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.models.database_models import ChatSession, ChatMessage
from app.services.llm_engine.ollama_client import OllamaClient
import json

router = APIRouter()

class ChatMessageSchema(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    chat_session_id: Optional[int] = None
    message: str
    system_prompt: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    chat_session_id: int

class ChatSessionResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

class ChatHistoryResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    
ollama_client = OllamaClient()

@router.post("/sessions/create")
async def create_empty_session(db: Session = Depends(get_db)):
    """Create empty chat session instantly"""
    chat_session = ChatSession(name=f"New Chat")
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)
    
    return {
        "id": chat_session.id,
        "name": chat_session.name,
        "created_at": chat_session.created_at,
        "updated_at": chat_session.updated_at
    }

@router.post("/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """Stream chat response token by token"""
    
    # Get or create chat session
    if request.chat_session_id:
        chat_session = db.query(ChatSession).filter(
            ChatSession.id == request.chat_session_id
        ).first()
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        chat_session = ChatSession(name=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
    
    # Save user message
    user_message = ChatMessage(
        chat_session_id=chat_session.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()
    
    # Get conversation history
    messages = db.query(ChatMessage).filter(
        ChatMessage.chat_session_id == chat_session.id
    ).order_by(ChatMessage.created_at).all()
    
    conversation = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])
    
    system_prompt = request.system_prompt or """You are a helpful AI assistant specializing in data quality, 
    data science, and analytics. Provide clear, concise, and accurate responses. Use markdown formatting for better readability."""
    
    async def generate_stream():
        full_response = ""
        
        try:
            # Send session ID first
            yield f"data: {json.dumps({'type': 'session_id', 'session_id': chat_session.id})}\n\n"
            
            # Stream response from Ollama
            result = await ollama_client.generate(
                prompt=conversation,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            
            response_text = result.get('response', '')
            
            # Simulate streaming by sending chunks
            chunk_size = 5  # characters per chunk
            for i in range(0, len(response_text), chunk_size):
                chunk = response_text[i:i+chunk_size]
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            
            # Save AI response
            ai_message = ChatMessage(
                chat_session_id=chat_session.id,
                role="assistant",
                content=full_response
            )
            db.add(ai_message)
            chat_session.updated_at = datetime.utcnow()
            db.commit()
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done', 'message_id': ai_message.id})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@router.post("/", response_model=ChatResponse)
async def chat_with_gemma(request: ChatRequest, db: Session = Depends(get_db)):
    """Regular chat endpoint (non-streaming)"""
    
    if request.chat_session_id:
        chat_session = db.query(ChatSession).filter(
            ChatSession.id == request.chat_session_id
        ).first()
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        chat_session = ChatSession(name=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
    
    user_message = ChatMessage(
        chat_session_id=chat_session.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.chat_session_id == chat_session.id
    ).order_by(ChatMessage.created_at).all()
    
    conversation = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])
    
    system_prompt = request.system_prompt or """You are a helpful AI assistant specializing in data quality, 
    data science, and analytics. Provide clear, concise, and accurate responses. Use markdown formatting for better readability."""
    
    try:
        result = await ollama_client.generate(
            prompt=conversation,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        ai_response = result.get('response', 'Sorry, I could not generate a response.')
        
        ai_message = ChatMessage(
            chat_session_id=chat_session.id,
            role="assistant",
            content=ai_response
        )
        db.add(ai_message)
        chat_session.updated_at = datetime.utcnow()
        db.commit()
        
        return ChatResponse(response=ai_response, chat_session_id=chat_session.id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(db: Session = Depends(get_db)):
    """Get all chat sessions"""
    sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
    return sessions

@router.get("/sessions/{session_id}/messages", response_model=List[ChatHistoryResponse])
async def get_chat_history(session_id: int, db: Session = Depends(get_db)):
    """Get chat history for a session"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.chat_session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    return messages

@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a chat session and all its messages"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    db.query(ChatMessage).filter(ChatMessage.chat_session_id == session_id).delete()
    db.delete(session)
    db.commit()
    
    return {"message": "Chat session deleted successfully"}

@router.put("/sessions/{session_id}/rename")
async def rename_chat_session(session_id: int, name: str, db: Session = Depends(get_db)):
    """Rename a chat session"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    session.name = name
    db.commit()
    
    return {"message": "Chat session renamed successfully"}
