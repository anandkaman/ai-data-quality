```markdown
# AI Data Quality  - API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except auth) require JWT token in header:
```
Authorization: Bearer <your_token>
```

---

## 1. Authentication Endpoints

### Register User
**POST** `/auth/register`

**Request Body:**
```
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

**Response:** `200 OK`
```
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "created_at": "2025-10-10T12:00:00"
}
```

### Login
**POST** `/auth/login`

**Request Body:**
```
{
  "username": "string",
  "password": "string"
}
```

**Response:** `200 OK`
```
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 2. Dataset Upload Endpoints

### Upload Dataset
**POST** `/upload`

**Content-Type:** `multipart/form-data`

**Request:**
- File: CSV or Excel file (max 100MB)

**Response:** `200 OK`
```
{
  "dataset_id": 1,
  "filename": "sales_data.csv",
  "file_size": 2048576,
  "row_count": 1000,
  "column_count": 15,
  "columns": ["id", "date", "amount", "category"],
  "upload_timestamp": "2025-10-10T12:00:00"
}
```

### Get Dataset Preview
**GET** `/upload/{dataset_id}/preview?rows=100`

**Response:** `200 OK`
```
{
  "dataset_id": 1,
  "filename": "sales_data.csv",
  "total_rows": 1000,
  "preview_rows": 100,
  "columns": [...],
  "data": [...]
}
```

---

## 3. Quality Assessment Endpoints

### Run Quality Assessment
**POST** `/assessment/assess/{dataset_id}`

**Response:** `200 OK`
```
{
  "dataset_id": 1,
  "overall_score": 87.5,
  "completeness_score": 95.2,
  "consistency_score": 88.1,
  "accuracy_score": 82.3,
  "uniqueness_score": 85.0,
  "timestamp": "2025-10-10T12:00:00",
  "details": {
    "completeness": {
      "missing_values": 48,
      "missing_percentage": 4.8,
      "column_completeness": {...}
    },
    "consistency": {...},
    "accuracy": {...},
    "uniqueness": {...}
  }
}
```

### Get Quality Metrics
**GET** `/assessment/{dataset_id}`

Returns same structure as assessment endpoint.

---

## 4. Anomaly Detection Endpoints

### Detect Anomalies
**POST** `/anomaly/detect/{dataset_id}`

**Request Body (Optional):**
```
{
  "contamination": 0.1,
  "n_estimators": 100
}
```

**Response:** `200 OK`
```
{
  "dataset_id": 1,
  "total_anomalies": 52,
  "anomaly_percentage": 5.2,
  "models_used": ["isolation_forest", "lof", "one_class_svm"],
  "ensemble_results": {
    "anomaly_indices": [12, 45, 67, ...],
    "anomaly_scores": [0.85, 0.92, 0.78, ...]
  },
  "model_results": {
    "isolation_forest": {...},
    "lof": {...},
    "one_class_svm": {...}
  }
}
```

---

## 5. Recommendations Endpoints

### Generate Recommendations
**POST** `/recommendations/generate/{dataset_id}`

**Response:** `200 OK`
```
{
  "dataset_id": 1,
  "recommendations": [
    {
      "priority": "high",
      "category": "missing_values",
      "issue": "Column 'age' has 15% missing values",
      "recommendation": "Use median imputation for age column",
      "code_example": "df['age'].fillna(df['age'].median(), inplace=True)",
      "impact": "high"
    }
  ],
  "generated_by": "gemma2:2b",
  "timestamp": "2025-10-10T12:00:00"
}
```

---

## 6. Chat Endpoints

### Create Chat Session
**POST** `/chat/sessions/create`

**Response:** `200 OK`
```
{
  "id": 1,
  "name": "New Chat",
  "created_at": "2025-10-10T12:00:00",
  "updated_at": "2025-10-10T12:00:00"
}
```

### Get All Chat Sessions
**GET** `/chat/sessions`

**Response:** `200 OK`
```
[
  {
    "id": 1,
    "name": "Data Quality Discussion",
    "created_at": "2025-10-10T12:00:00",
    "updated_at": "2025-10-10T12:05:00"
  }
]
```

### Get Chat Messages
**GET** `/chat/sessions/{session_id}/messages`

**Response:** `200 OK`
```
[
  {
    "id": 1,
    "chat_session_id": 1,
    "role": "user",
    "content": "How do I handle missing values?",
    "created_at": "2025-10-10T12:00:00"
  },
  {
    "id": 2,
    "chat_session_id": 1,
    "role": "assistant",
    "content": "Here are several methods...",
    "created_at": "2025-10-10T12:00:05"
  }
]
```

### Send Message
**POST** `/chat`

**Request Body:**
```
{
  "chat_session_id": 1,
  "message": "What is data quality?",
  "system_prompt": "You are a data quality expert..."
}
```

**Response:** `200 OK`
```
{
  "chat_session_id": 1,
  "user_message_id": 3,
  "assistant_message_id": 4,
  "response": "Data quality refers to..."
}
```

### Rename Chat Session
**PUT** `/chat/sessions/{session_id}/rename?name=NewName`

### Delete Chat Session
**DELETE** `/chat/sessions/{session_id}`

---

## 7. AI Dashboard Endpoints

### Generate Dashboard
**POST** `/ai-dashboard/generate`

**Request Body:**
```
{
  "dataset_id": 1,
  "num_columns": 2,
  "prompt": "Show key metrics and sales trends"
}
```

**Response:** `200 OK`
```
{
  "items": [
    {
      "type": "metric_card",
      "title": "Total Sales",
      "plotly_json": null,
      "description": "Sum of all sales",
      "metric_card": {
        "metric_type": "sum",
        "column": "amount",
        "value": "1.25M",
        "title": "Total Sales",
        "description": "..."
      }
    },
    {
      "type": "scatter",
      "title": "Sales vs Profit",
      "plotly_json": "{...}",
      "description": "Correlation analysis",
      "color_scheme": "blues"
    }
  ],
  "num_columns": 2,
  "analysis": "The dataset shows...",
  "dashboard_id": "dashboard_1_20251010120000"
}
```

---

## 8. Model Management Endpoints

### Get Available Models
**GET** `/models/available`

**Response:** `200 OK`
```
{
  "models": [
    {
      "name": "gemma2:2b",
      "size": 1600000000,
      "modified": "2025-10-01T10:00:00",
      "digest": "sha256:abc123..."
    }
  ],
  "current_model": "gemma2:2b"
}
```

### Pull Model (Server-Sent Events)
**POST** `/models/pull/{model_name}`

**Response:** `text/event-stream`
```
data: {"type":"log","content":"pulling manifest","timestamp":"..."}
data: {"type":"log","content":"downloading...","timestamp":"..."}
data: {"type":"success","content":"Model pulled","timestamp":"..."}
```

### Switch Model
**POST** `/models/switch`

**Request Body:**
```
{
  "model_name": "llama3.2"
}
```

**Response:** `200 OK`
```
{
  "success": true,
  "message": "Switched to llama3.2",
  "current_model": "llama3.2"
}
```

---

## 9. Admin Endpoints

### Manual Cleanup - Datasets
**POST** `/admin/cleanup/datasets?days_old=1`

**Response:** `200 OK`
```
{
  "message": "Cleanup completed",
  "stats": {
    "files_deleted": 5,
    "db_records_deleted": 5,
    "errors": []
  }
}
```

### List Old Datasets
**GET** `/admin/datasets/old?days_old=1`

**Response:** `200 OK`
```
{
  "cutoff_date": "2025-10-09T12:00:00",
  "count": 3,
  "datasets": [
    {
      "id": 1,
      "filename": "old_data.csv",
      "uploaded": "2025-10-08T10:00:00",
      "age_days": 2
    }
  ]
}
```

---

## Error Responses

All endpoints return standard error format:

**4xx Client Errors:**
```
{
  "detail": "Dataset not found"
}
```

**5xx Server Errors:**
```
{
  "detail": "Internal server error: ..."
}
```

---

## Rate Limits

- No rate limits currently implemented
- Recommended: Max 100 requests/minute per user

## Interactive Documentation

Access Swagger UI:
```
http://localhost:8000/docs
```

Access ReDoc:
```
http://localhost:8000/redoc
```

---

## Notes

1. **File Size Limits:** 100MB for dataset uploads
2. **Supported Formats:** CSV, XLS, XLSX
3. **Token Expiration:** JWT tokens expire after 30 days
4. **Auto Cleanup:** Datasets older than 1 day deleted daily at 2 AM
5. **Ollama Models:** Must be running on `localhost:11434`
```
