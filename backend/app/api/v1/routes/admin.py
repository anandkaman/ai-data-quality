from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.database_models import DatasetMetadata
from app.services.cleanup_service import CleanupService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/cleanup/datasets")
def cleanup_old_datasets(days_old: int = 1):
    """Manually trigger dataset cleanup"""
    stats = CleanupService.cleanup_old_datasets(days_old=days_old)
    return {
        "message": f"Cleanup completed for datasets older than {days_old} day(s)",
        "stats": stats
    }

@router.post("/cleanup/orphaned")
def cleanup_orphaned_files():
    """Manually trigger orphaned files cleanup"""
    stats = CleanupService.cleanup_orphaned_files()
    return {
        "message": "Orphaned files cleanup completed",
        "stats": stats
    }

@router.post("/cleanup/empty-chats")
def cleanup_empty_chats(days_old: int = 7):
    """Manually trigger empty chats cleanup"""
    stats = CleanupService.cleanup_empty_chats(days_old=days_old)
    return {
        "message": f"Empty chats cleanup completed for chats older than {days_old} day(s)",
        "stats": stats
    }

@router.post("/cleanup/all")
def run_all_cleanups():
    """Run all cleanup operations"""
    stats = CleanupService.run_all_cleanups()
    return {
        "message": "All cleanups completed",
        "stats": stats
    }

@router.get("/datasets/old")
def list_old_datasets(days_old: int = 1, db: Session = Depends(get_db)):
    """List datasets older than specified days (for testing)"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    old_datasets = db.query(DatasetMetadata).filter(
        DatasetMetadata.upload_timestamp < cutoff_date
    ).all()
    
    return {
        "cutoff_date": cutoff_date.isoformat(),
        "count": len(old_datasets),
        "datasets": [
            {
                "id": ds.id,
                "filename": ds.filename,
                "uploaded": ds.upload_timestamp.isoformat(),
                "age_days": (datetime.utcnow() - ds.upload_timestamp).days
            }
            for ds in old_datasets
        ]
    }
