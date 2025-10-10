import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.database_models import DatasetMetadata, ChatSession, ChatMessage
import logging

logger = logging.getLogger(__name__)

class CleanupService:
    """Service for cleaning up old files and database records"""
    
    @staticmethod
    def cleanup_old_datasets(days_old: int = 1) -> dict:
        """
        Delete dataset files and database records older than specified days
        
        Args:
            days_old: Number of days after which to delete datasets (default: 1)
        
        Returns:
            dict with cleanup statistics
        """
        db = SessionLocal()
        stats = {
            'files_deleted': 0,
            'db_records_deleted': 0,
            'errors': []
        }
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Find old datasets in database
            old_datasets = db.query(DatasetMetadata).filter(
                DatasetMetadata.upload_timestamp < cutoff_date
            ).all()
            
            logger.info(f"Found {len(old_datasets)} datasets older than {days_old} day(s)")
            
            for dataset in old_datasets:
                try:
                    # Delete physical file
                    file_path = os.path.join(settings.UPLOAD_DIR, dataset.filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        stats['files_deleted'] += 1
                        logger.info(f"Deleted file: {dataset.filename}")
                    
                    # Delete database record
                    db.delete(dataset)
                    stats['db_records_deleted'] += 1
                    
                except Exception as e:
                    error_msg = f"Error deleting dataset {dataset.id}: {str(e)}"
                    stats['errors'].append(error_msg)
                    logger.error(error_msg)
            
            db.commit()
            logger.info(f"Cleanup completed: {stats}")
            
        except Exception as e:
            db.rollback()
            error_msg = f"Cleanup failed: {str(e)}"
            stats['errors'].append(error_msg)
            logger.error(error_msg)
        
        finally:
            db.close()
        
        return stats
    
    @staticmethod
    def cleanup_orphaned_files() -> dict:
        """
        Delete files in upload directory that have no database record
        
        Returns:
            dict with cleanup statistics
        """
        db = SessionLocal()
        stats = {
            'orphaned_files_deleted': 0,
            'errors': []
        }
        
        try:
            # Get all filenames from database
            db_filenames = {dataset.filename for dataset in db.query(DatasetMetadata).all()}
            
            # Get all files in upload directory
            upload_dir = Path(settings.UPLOAD_DIR)
            if upload_dir.exists():
                for file_path in upload_dir.iterdir():
                    if file_path.is_file() and file_path.name not in db_filenames and file_path.name != '.gitkeep':
                        try:
                            file_path.unlink()
                            stats['orphaned_files_deleted'] += 1
                            logger.info(f"Deleted orphaned file: {file_path.name}")
                        except Exception as e:
                            error_msg = f"Error deleting orphaned file {file_path.name}: {str(e)}"
                            stats['errors'].append(error_msg)
                            logger.error(error_msg)
            
            logger.info(f"Orphaned files cleanup completed: {stats}")
            
        except Exception as e:
            error_msg = f"Orphaned files cleanup failed: {str(e)}"
            stats['errors'].append(error_msg)
            logger.error(error_msg)
        
        finally:
            db.close()
        
        return stats
    
    @staticmethod
    def cleanup_empty_chats(days_old: int = 7) -> dict:
        """
        Delete empty chat sessions older than specified days
        
        Args:
            days_old: Number of days after which to delete empty chats (default: 7)
        
        Returns:
            dict with cleanup statistics
        """
        db = SessionLocal()
        stats = {
            'empty_chats_deleted': 0,
            'errors': []
        }
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Find chat sessions with no messages and older than cutoff
            empty_chats = db.query(ChatSession).filter(
                ChatSession.created_at < cutoff_date
            ).all()
            
            for chat in empty_chats:
                # Check if chat has no messages
                message_count = db.query(ChatMessage).filter(
                    ChatMessage.chat_session_id == chat.id
                ).count()
                
                if message_count == 0:
                    try:
                        db.delete(chat)
                        stats['empty_chats_deleted'] += 1
                        logger.info(f"Deleted empty chat: {chat.id}")
                    except Exception as e:
                        error_msg = f"Error deleting empty chat {chat.id}: {str(e)}"
                        stats['errors'].append(error_msg)
                        logger.error(error_msg)
            
            db.commit()
            logger.info(f"Empty chats cleanup completed: {stats}")
            
        except Exception as e:
            db.rollback()
            error_msg = f"Empty chats cleanup failed: {str(e)}"
            stats['errors'].append(error_msg)
            logger.error(error_msg)
        
        finally:
            db.close()
        
        return stats

    @staticmethod
    def run_all_cleanups() -> dict:
        """Run all cleanup operations"""
        
        logger.info("Starting automatic cleanup...")
        
        all_stats = {
            'datasets': CleanupService.cleanup_old_datasets(days_old=1),
            'orphaned_files': CleanupService.cleanup_orphaned_files(),
            'empty_chats': CleanupService.cleanup_empty_chats(days_old=7),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"All cleanups completed: {all_stats}")
        
        return all_stats
