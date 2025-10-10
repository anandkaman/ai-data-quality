from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import os
from app.core.database import get_db
from app.core.config import settings
from app.models.database_models import DatasetMetadata, AnomalyDetection
from app.models.schemas import AnomalyDetectionResult
from app.services.ml_engine import AnomalyEnsemble
from app.services.explainability import SHAPExplainer

router = APIRouter()

@router.post("/{dataset_id}", response_model=AnomalyDetectionResult)
async def detect_anomalies(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(DatasetMetadata).filter(DatasetMetadata.id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    file_path = os.path.join(settings.UPLOAD_DIR, dataset.filename)
    
    if dataset.filename.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    ensemble = AnomalyEnsemble()
    result = ensemble.detect_anomalies(df)
    
    anomaly_indices = result['ensemble_anomalies']
    anomaly_count = len(anomaly_indices)
    anomaly_percentage = (anomaly_count / len(df)) * 100 if len(df) > 0 else 0.0
    
    explainer = SHAPExplainer()
    explanations = explainer.explain_anomalies(
        df,
        ensemble.models['isolation_forest'].model,
        anomaly_indices
    )
    
    anomaly_record = AnomalyDetection(
        dataset_id=dataset_id,
        model_used='ensemble',
        anomaly_count=anomaly_count,
        anomaly_indices=anomaly_indices,
        anomaly_scores=result['scores'].tolist() if hasattr(result['scores'], 'tolist') else [],
        feature_contributions=explanations
    )
    
    db.add(anomaly_record)
    dataset.status = 'anomaly_detected'
    db.commit()
    
    return AnomalyDetectionResult(
        anomaly_count=anomaly_count,
        anomaly_percentage=round(anomaly_percentage, 2),
        anomaly_indices=anomaly_indices,
        feature_importance=explanations.get('global_feature_importance', {})
    )

@router.get("/{dataset_id}/details")
async def get_anomaly_details(dataset_id: int, db: Session = Depends(get_db)):
    anomaly = db.query(AnomalyDetection).filter(
        AnomalyDetection.dataset_id == dataset_id
    ).order_by(AnomalyDetection.detection_timestamp.desc()).first()
    
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly detection not found")
    
    return {
        'anomaly_count': anomaly.anomaly_count,
        'anomaly_indices': anomaly.anomaly_indices,
        'feature_contributions': anomaly.feature_contributions,
        'detection_timestamp': anomaly.detection_timestamp
    }
