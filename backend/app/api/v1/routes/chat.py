from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.models.database_models import ChatSession, ChatMessage
from app.services.llm_engine.ollama_client import OllamaClient
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

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
async def create_chat_session(db: Session = Depends(get_db)):
    """Create a new empty chat session"""
    
    try:
        chat_session = ChatSession(name=f"New Chat")
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
        
        logger.info(f"Created new chat session: {chat_session.id}")
        
        return {
            "id": chat_session.id,
            "name": chat_session.name,
            "created_at": chat_session.created_at.isoformat(),
            "updated_at": chat_session.updated_at.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create chat session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")

@router.post("/", response_model=ChatResponse)
async def chat_with_gemma(request: ChatRequest, db: Session = Depends(get_db)):
    """Chat with Gemma 2:2b model and save to database"""
    
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
    
    # Build conversation context
    conversation = "\n".join([
        f"{msg.role}: {msg.content}" for msg in messages
    ])
    
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
        
        # Save AI response
        ai_message = ChatMessage(
            chat_session_id=chat_session.id,
            role="assistant",
            content=ai_response
        )
        db.add(ai_message)
        
        # Update session timestamp
        chat_session.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Chat completed for session {chat_session.id}")
        
        return ChatResponse(response=ai_response, chat_session_id=chat_session.id)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Chat failed: {str(e)}")
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
    
    try:
        # Delete all messages first
        messages_deleted = db.query(ChatMessage).filter(
            ChatMessage.chat_session_id == session_id
        ).delete()
        
        # Delete session
        db.delete(session)
        db.commit()
        
        logger.info(f"Deleted chat session {session_id} with {messages_deleted} messages")
        
        return {
            "message": "Chat session deleted successfully",
            "session_id": session_id,
            "messages_deleted": messages_deleted
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete chat session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete chat session: {str(e)}")

@router.put("/sessions/{session_id}/rename")
async def rename_chat_session(session_id: int, name: str, db: Session = Depends(get_db)):
    """Rename a chat session"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    try:
        session.name = name
        session.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Renamed chat session {session_id} to '{name}'")
        
        return {"message": "Chat session renamed successfully", "name": name}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to rename chat session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to rename chat session: {str(e)}")