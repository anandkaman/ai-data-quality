from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.database_models import ChatSession, ChatMessage
from app.services.llm_engine.ollama_client import OllamaClient
import logging

router = APIRouter()
ollama_client = OllamaClient()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    chat_session_id: Optional[int] = None
    message: str
    system_prompt: Optional[str] = None

class ChatResponse(BaseModel):
    chat_session_id: int
    user_message_id: int
    assistant_message_id: int
    response: str

@router.post("/", response_model=ChatResponse)
async def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    """Send message to AI with conversation context (ONLY from active chat)"""
    
    try:
        # Create or get chat session
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
        
        # Get ONLY the conversation history for THIS chat session
        previous_messages = db.query(ChatMessage).filter(
            ChatMessage.chat_session_id == chat_session.id
        ).order_by(ChatMessage.created_at.asc()).limit(20).all()  # Last 20 messages only
        
        # Build conversation context for the model
        conversation_context = ""
        for msg in previous_messages:
            if msg.role == "user":
                conversation_context += f"User: {msg.content}\n"
            else:
                conversation_context += f"Assistant: {msg.content}\n"
        
        # Add current message
        conversation_context += f"User: {request.message}\n"
        
        # Save user message BEFORE sending to model
        user_message = ChatMessage(
            chat_session_id=chat_session.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # Send ONLY this chat's conversation to the model
        system_prompt = request.system_prompt or """You are a helpful AI assistant specializing in data quality and data science. 
Use markdown formatting. Answer based on the conversation history provided."""
        
        logger.info(f"Sending conversation with {len(previous_messages)} previous messages to model")
        
        ai_response = await ollama_client.generate(
            prompt=conversation_context,  # Sends ONLY this chat's history
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        # Save assistant message
        assistant_message = ChatMessage(
            chat_session_id=chat_session.id,
            role="assistant",
            content=ai_response.get('response', '')
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        # Update chat session timestamp
        chat_session.updated_at = datetime.utcnow()
        db.commit()
        
        return ChatResponse(
            chat_session_id=chat_session.id,
            user_message_id=user_message.id,
            assistant_message_id=assistant_message.id,
            response=ai_response.get('response', '')
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

@router.get("/sessions")
async def get_chat_sessions(db: Session = Depends(get_db)):
    """Get all chat sessions"""
    
    sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
    
    return [
        {
            "id": session.id,
            "name": session.name,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
        for session in sessions
    ]

@router.get("/sessions/{session_id}/messages")
async def get_chat_messages(session_id: int, db: Session = Depends(get_db)):
    """Get all messages for a chat session"""
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.chat_session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return [
        {
            "id": msg.id,
            "chat_session_id": msg.chat_session_id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in messages
    ]

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
        
        return {
            "message": "Chat session renamed successfully",
            "session_id": session_id,
            "new_name": name
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to rename chat session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to rename chat session: {str(e)}")

@router.delete("/messages/{message_id}")
async def delete_message(message_id: int, db: Session = Depends(get_db)):
    """Delete a specific message"""
    
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    try:
        db.delete(message)
        db.commit()
        
        logger.info(f"Deleted message {message_id}")
        
        return {
            "message": "Message deleted successfully",
            "message_id": message_id
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete message {message_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")
