from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import os
import json
from app.core.database import get_db
from app.core.config import settings
from app.models.database_models import DatasetMetadata, QualityAssessment, CleaningRecommendation
from app.models.schemas import CleaningRecommendationResponse
from app.services.llm_engine.ollama_client import OllamaClient
from app.services.llm_engine.rag_system import RAGSystem

router = APIRouter()

@router.post("/{dataset_id}")
async def generate_recommendations(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(DatasetMetadata).filter(DatasetMetadata.id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    assessment = db.query(QualityAssessment).filter(
        QualityAssessment.dataset_id == dataset_id
    ).order_by(QualityAssessment.assessment_timestamp.desc()).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Quality assessment not found. Run assessment first.")
    
    file_path = os.path.join(settings.UPLOAD_DIR, dataset.filename)
    
    if dataset.filename.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    data_profile = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'columns': df.columns.tolist(),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'missing_summary': df.isnull().sum().to_dict(),
        'numeric_summary': df.describe().to_dict() if not df.select_dtypes(include=['number']).empty else {}
    }
    
    quality_issues = []
    report = assessment.quality_report
    
    if report.get('completeness'):
        for col, stats in report['completeness'].get('column_completeness', {}).items():
            if stats['missing_percentage'] > 10:
                quality_issues.append({
                    'type': 'completeness',
                    'column': col,
                    'severity': 'high' if stats['missing_percentage'] > 50 else 'medium',
                    'details': stats
                })
    
    if report.get('consistency', {}).get('format_consistency'):
        for col in report['consistency']['format_consistency'].keys():
            quality_issues.append({
                'type': 'consistency',
                'column': col,
                'severity': 'medium',
                'details': 'Format inconsistency detected'
            })
    
    rag_system = RAGSystem()
    issue_query = ' '.join([issue['type'] for issue in quality_issues[:3]])
    relevant_knowledge = rag_system.retrieve_relevant_knowledge(issue_query, n_results=3)
    
    ollama_client = OllamaClient()
    llm_response = await ollama_client.generate_cleaning_strategy(
        data_profile=data_profile,
        quality_issues=quality_issues
    )
    
    context = f"\n\nRelevant Best Practices:\n"
    for knowledge in relevant_knowledge:
        context += f"- {knowledge['metadata'].get('solution', '')}\n"
    
    if not llm_response.get('parsed'):
        llm_response = {
            'priority_ranking': [{'issue': issue['type'], 'severity': issue['severity'], 'impact': 'medium'} for issue in quality_issues],
            'strategies': [],
            'implementation_order': [issue['column'] for issue in quality_issues if 'column' in issue],
            'success_metrics': {'data_quality_score': 'improved'}
        }
    
    recommendation = CleaningRecommendation(
        dataset_id=dataset_id,
        strategies=llm_response,
        impact_analysis={'estimated_improvement': '20-30%'},
        llm_reasoning=json.dumps(llm_response) + context
    )
    
    db.add(recommendation)
    dataset.status = 'recommendations_generated'
    db.commit()
    
    return llm_response

@router.get("/{dataset_id}")
async def get_recommendations(dataset_id: int, db: Session = Depends(get_db)):
    recommendation = db.query(CleaningRecommendation).filter(
        CleaningRecommendation.dataset_id == dataset_id
    ).order_by(CleaningRecommendation.recommendation_timestamp.desc()).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendations not found")
    
    return recommendation.strategies
