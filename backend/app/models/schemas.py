from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

class DatasetUploadResponse(BaseModel):
    dataset_id: int
    filename: str
    row_count: int
    column_count: int
    status: str

class QualityMetrics(BaseModel):
    completeness_score: float
    consistency_score: float
    accuracy_score: float
    uniqueness_score: float
    overall_score: float

class AnomalyDetectionResult(BaseModel):
    anomaly_count: int
    anomaly_percentage: float
    anomaly_indices: List[int]
    feature_importance: Dict[str, Any]

class CleaningStrategy(BaseModel):
    issue_type: str
    affected_columns: List[str]
    root_cause: str
    recommended_approach: Dict[str, Any]
    expected_improvement: str
    risks: List[str]

class CleaningRecommendationResponse(BaseModel):
    priority_ranking: List[Dict[str, Any]]
    strategies: List[CleaningStrategy]
    implementation_order: List[str]
    success_metrics: Dict[str, Any]
