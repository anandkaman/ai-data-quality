from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import os
import shutil
from datetime import datetime
from app.core.database import get_db
from app.core.config import settings
from app.models.database_models import DatasetMetadata
from app.models.schemas import DatasetUploadResponse

router = APIRouter()

@router.post("/", response_model=DatasetUploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a dataset for quality assessment"""
    
    # Validate file type
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Load and analyze file
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
        else:
            df = pd.read_excel(file_path)
        
        # Create metadata
        metadata = DatasetMetadata(
            filename=filename,
            upload_timestamp=datetime.utcnow(),
            row_count=len(df),
            column_count=len(df.columns),
            file_size_bytes=os.path.getsize(file_path),
            schema_info={
                "columns": df.columns.tolist(),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
            },
            status="uploaded"
        )
        
        db.add(metadata)
        db.commit()
        db.refresh(metadata)
        
        return DatasetUploadResponse(
            dataset_id=metadata.id,
            filename=metadata.filename,
            row_count=metadata.row_count,
            column_count=metadata.column_count,
            status=metadata.status
        )
    
    except Exception as e:
        # Clean up the uploaded file if processing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
