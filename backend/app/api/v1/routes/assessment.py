from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import os
import asyncio
import json
from app.core.database import get_db
from app.core.config import settings
from app.models.database_models import DatasetMetadata, QualityAssessment
from app.models.schemas import QualityMetrics
from app.services.quality_engine import (
    CompletenessAnalyzer,
    ConsistencyAnalyzer,
    AccuracyAnalyzer,
    UniquenessAnalyzer
)

router = APIRouter()

async def progress_generator(dataset_id: int):
    """Generator for progress updates"""
    steps = [
        {"step": "Loading dataset", "progress": 10},
        {"step": "Analyzing completeness", "progress": 30},
        {"step": "Checking consistency", "progress": 50},
        {"step": "Validating accuracy", "progress": 70},
        {"step": "Computing uniqueness", "progress": 90},
        {"step": "Finalizing report", "progress": 100}
    ]
    
    for step_data in steps:
        yield f"data: {json.dumps(step_data)}\n\n"
        await asyncio.sleep(0.5)

@router.get("/{dataset_id}/progress")
async def get_assessment_progress(dataset_id: int):
    """Stream progress updates for assessment"""
    return StreamingResponse(
        progress_generator(dataset_id),
        media_type="text/event-stream"
    )

@router.post("/{dataset_id}", response_model=QualityMetrics)
async def assess_quality(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(DatasetMetadata).filter(DatasetMetadata.id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    file_path = os.path.join(settings.UPLOAD_DIR, dataset.filename)
    
    if dataset.filename.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    completeness = CompletenessAnalyzer().analyze(df)
    consistency = ConsistencyAnalyzer().analyze(df)
    accuracy = AccuracyAnalyzer().analyze(df)
    uniqueness = UniquenessAnalyzer().analyze(df)
    
    completeness_score = completeness['overall_completeness']
    consistency_score = 100 - (len(consistency['format_consistency']) * 10)
    accuracy_score = 100 - (len(accuracy['range_violations']) * 15)
    uniqueness_score = uniqueness['duplicate_rows']['uniqueness_score']
    
    overall_score = (completeness_score + consistency_score + accuracy_score + uniqueness_score) / 4
    
    quality_report = {
        'completeness': completeness,
        'consistency': consistency,
        'accuracy': accuracy,
        'uniqueness': uniqueness
    }
    
    assessment = QualityAssessment(
        dataset_id=dataset_id,
        completeness_score=completeness_score,
        consistency_score=max(0, consistency_score),
        accuracy_score=max(0, accuracy_score),
        uniqueness_score=uniqueness_score,
        overall_score=overall_score,
        quality_report=quality_report
    )
    
    db.add(assessment)
    dataset.status = 'assessed'
    db.commit()
    db.refresh(assessment)
    
    return QualityMetrics(
        completeness_score=completeness_score,
        consistency_score=max(0, consistency_score),
        accuracy_score=max(0, accuracy_score),
        uniqueness_score=uniqueness_score,
        overall_score=overall_score
    )

@router.get("/{dataset_id}/report")
async def get_quality_report(dataset_id: int, db: Session = Depends(get_db)):
    assessment = db.query(QualityAssessment).filter(
        QualityAssessment.dataset_id == dataset_id
    ).order_by(QualityAssessment.assessment_timestamp.desc()).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return assessment.quality_report
