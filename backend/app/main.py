from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.routes import upload, assessment, anomaly, recommendations, auth, chat, ai_dashboard
from app.services.cleanup_service import CleanupService
from app.api.v1.routes import upload, assessment, anomaly, recommendations, auth, chat, ai_dashboard, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler()

def scheduled_cleanup():
    """Run scheduled cleanup task"""
    logger.info("Running scheduled cleanup...")
    stats = CleanupService.run_all_cleanups()
    logger.info(f"Cleanup completed: {stats}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    
    # Startup
    logger.info("Starting up application...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Start scheduler for automatic cleanup
    # Run every day at 2 AM
    scheduler.add_job(
        scheduled_cleanup,
        CronTrigger(hour=2, minute=0),
        id='daily_cleanup',
        name='Daily cleanup of old datasets',
        replace_existing=True
    )
    
    # Also run cleanup on startup
    scheduler.add_job(
        scheduled_cleanup,
        'date',
        run_date=None,
        id='startup_cleanup',
        name='Cleanup on startup'
    )
    
    scheduler.start()
    logger.info("Cleanup scheduler started (runs daily at 2 AM)")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    scheduler.shutdown()
    logger.info("Cleanup scheduler stopped")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(upload.router, prefix=f"{settings.API_V1_STR}/upload", tags=["upload"])
app.include_router(assessment.router, prefix=f"{settings.API_V1_STR}/assessment", tags=["assessment"])
app.include_router(anomaly.router, prefix=f"{settings.API_V1_STR}/anomaly", tags=["anomaly"])
app.include_router(recommendations.router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["recommendations"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(ai_dashboard.router, prefix=f"{settings.API_V1_STR}/ai-dashboard", tags=["ai-dashboard"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {
        "message": "AI Data Quality Guardian API",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Manual cleanup endpoint (admin use)
@app.post(f"{settings.API_V1_STR}/admin/cleanup")
def manual_cleanup():
    """Manually trigger cleanup (for testing/admin)"""
    stats = CleanupService.run_all_cleanups()
    return {
        "message": "Cleanup executed",
        "stats": stats
    }
