# AI Data Quality Guardian - Architecture Documentation

## System Overview

AI Data Quality Guardian is a **microservices-inspired monolithic application** that combines modern web technologies with AI capabilities to provide intelligent data quality management.

---

## High-Level Architecture

```
             ┌─────────────────────────────────────────────────────────────┐
             │                         Frontend Layer                      │
             │  (React 18 + Tailwind CSS + Zustand + React Query)          │
             └────────────────────────┬────────────────────────────────────┘
                                      │ HTTP/REST
                                      │ JSON
             ┌────────────────────────▼────────────────────────────────────┐
             │                      API Gateway Layer                      │
             │              (FastAPI + CORS + Authentication)              │
             └────────────────────────┬────────────────────────────────────┘
                                      │
                     ┌────────────────┼────────────────┐
                     │                │                │
             ┌───────▼──────┐  ┌──────▼──────┐  ┌──────▼───────┐
             │   Business   │  │   AI/LLM    │  │   Data       │
             │   Logic      │  │   Services  │  │   Layer      │
             │   Layer      │  │             │  │              │
             └───────┬──────┘  └──────┬──────┘  └──────┬───────┘
                     │                │                │
                     │         ┌──────▼──────┐         │
                     │         │   Ollama    │         │
                     │         │   Server    │         │
                     │         │ (Gemma 2:2b)│         │
                     │         └─────────────┘         │
                     │                                 │
                     └─────────────────┬───────────────┘
                                       │
                                ┌──────▼──────┐
                                │  PostgreSQL │
                                │  / SQLite   │
                                │  Database   │
                                └─────────────┘
```

---

## Component Architecture

### 1. Frontend Architecture

**Technology Stack:**
- React 18.3 (Component library)
- Tailwind CSS 3.4 (Styling)
- Zustand (State management)
- React Query (Server state)
- Axios (HTTP client)
- Plotly.js (Visualizations)
- React Markdown (Content rendering)

**Directory Structure:**
```
frontend/src/
├── components/
│   └── layout/
│       ├── Header.jsx          # App header with navigation
│       ├── Sidebar.jsx         # Navigation sidebar
│       └── Layout.jsx          # Main layout wrapper
├── features/
│   ├── auth/
│   │   ├── Login.jsx           # Login page
│   │   └── Register.jsx        # Registration page
│   ├── upload/
│   │   ├── components/
│   │   │   ├── FileUploader.jsx    # Drag-drop upload
│   │   │   └── DataPreview.jsx     # Dataset preview
│   ├── dashboard/
│   │   ├── components/
│   │   │   ├── QualityMetricsCard.jsx
│   │   │   ├── AnomalyVisualization.jsx
│   │   │   └── ProgressTracker.jsx
│   │   └── AIDashboard.jsx     # AI-generated dashboard
│   ├── recommendations/
│   │   └── components/
│   │       └── StrategyList.jsx
│   └── chat/
│       ├── ChatInterface.jsx   # Main chat UI
│       └── ModelSwitcher.jsx   # Model selection
├── services/
│   └── api.js                  # API client functions
├── store/
│   └── useAppStore.js          # Zustand global state
└── App.jsx                     # Root component
```

**State Management Flow:**
```
// Zustand Store (Single Source of Truth)
useAppStore {
  currentDataset,      // Active dataset metadata
  qualityMetrics,      // Assessment results
  anomalyResults,      // Detected anomalies
  recommendations,     // AI suggestions
  dashboardData,       // Dashboard config
  loading,             // Global loading state
  
  // Actions
  setCurrentDataset(),
  setQualityMetrics(),
  setAnomalyResults(),
  setRecommendations(),
  reset()
}

// Component Usage
const MyComponent = () => {
  const { currentDataset, setCurrentDataset } = useAppStore();
  // Access state and actions
};
```

---

### 2. Backend Architecture

**Technology Stack:**
- FastAPI 0.115 (Web framework)
- SQLAlchemy 2.0 (ORM)
- Pydantic 2.0 (Data validation)
- Pandas 2.2 (Data processing)
- Scikit-learn 1.5 (ML models)
- Plotly 5.24 (Visualizations)
- Httpx (Async HTTP)
- Python-Jose (JWT)

**Directory Structure:**
```
backend/app/
├── api/
│   └── v1/
│       └── routes/
│           ├── auth.py              # Authentication
│           ├── upload.py            # File upload
│           ├── assessment.py        # Quality assessment
│           ├── anomaly.py           # Anomaly detection
│           ├── recommendations.py   # AI recommendations
│           ├── chat.py              # Chat interface
│           ├── ai_dashboard.py      # Dashboard generation
│           ├── models.py            # Model management
│           └── admin.py             # Admin operations
├── core/
│   ├── config.py                    # Configuration
│   ├── database.py                  # Database setup
│   └── security.py                  # Auth utilities
├── models/
│   ├── database_models.py           # SQLAlchemy models
│   └── schemas.py                   # Pydantic schemas
├── services/
│   ├── quality_engine/
│   │   ├── completeness.py
│   │   ├── consistency.py
│   │   ├── accuracy.py
│   │   └── uniqueness.py
│   ├── anomaly_engine/
│   │   ├── isolation_forest.py
│   │   ├── lof.py
│   │   └── ensemble.py
│   ├── llm_engine/
│   │   ├── ollama_client.py         # LLM client
│   │   └── model_manager.py         # Model switching
│   └── cleanup_service.py           # Auto cleanup
└── main.py                          # Application entry
```

---

### 3. Database Schema

**Entity Relationship Diagram:**
```
┌─────────────────┐
│     Users       │
├─────────────────┤
│ id (PK)         │
│ username        │
│ email           │
│ hashed_password │
│ created_at      │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────────┐
│ DatasetMetadata     │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK)        │
│ filename            │
│ file_size           │
│ row_count           │
│ column_count        │
│ columns (JSON)      │
│ upload_timestamp    │
└─────────────────────┘

┌─────────────────┐       ┌──────────────────┐
│ ChatSession     │ 1   N │ ChatMessage      │
├─────────────────┤───────├──────────────────┤
│ id (PK)         │       │ id (PK)          │
│ name            │       │ chat_session_id  │
│ created_at      │       │ role             │
│ updated_at      │       │ content          │
└─────────────────┘       │ created_at       │
                          └──────────────────┘
```

**Table Definitions:**

```
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dataset metadata
CREATE TABLE dataset_metadata (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    row_count INTEGER NOT NULL,
    column_count INTEGER NOT NULL,
    columns JSON NOT NULL,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat sessions
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL DEFAULT 'New Chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat messages
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    chat_session_id INTEGER REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_dataset_user ON dataset_metadata(user_id);
CREATE INDEX idx_dataset_timestamp ON dataset_metadata(upload_timestamp);
CREATE INDEX idx_chat_messages_session ON chat_messages(chat_session_id);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(created_at);
```

---

### 4. AI/LLM Integration Architecture

```
┌──────────────────────────────────────────────────┐
│              Application Layer                   │
│  (chat.py, recommendations.py, ai_dashboard.py)  │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│           LLM Abstraction Layer                  │
│            (ollama_client.py)                    │
│  -  Request formatting                           │
│  -  Response parsing                             │
│  -  Error handling                               │
│  -  Timeout management                           │
└──────────────────┬───────────────────────────────┘
                   │ HTTP/JSON
                   ▼
┌──────────────────────────────────────────────────┐
│              Ollama Server                       │
│          (localhost:11434)                       │
│  -  Model management                             │
│  -  GPU/CPU orchestration                        │
│  -  Context window handling                      │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│              LLM Model                           │
│            (Gemma 2:2b)                          │
│  -  Text generation                              │
│  -  Context understanding                        │
│  -  Response generation                          │
└──────────────────────────────────────────────────┘
```

**LLM Client Design Pattern:**

```
class OllamaClient:
    """Abstraction layer for LLM communication"""
    
    def __init__(self, base_url, model):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=120)
    
    async def generate(self, prompt, system_prompt, **params):
        """
        Unified interface for text generation
        
        Flow:
        1. Format request
        2. Send to Ollama
        3. Parse response
        4. Handle errors
        5. Return structured data
        """
        request = self._format_request(prompt, system_prompt, params)
        response = await self._send_request(request)
        parsed = self._parse_response(response)
        return parsed
    
    def _format_request(self, prompt, system_prompt, params):
        """Prepare request payload"""
        return {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{prompt}",
            "temperature": params.get('temperature', 0.7),
            "max_tokens": params.get('max_tokens', 2000),
            "stream": params.get('stream', False)
        }
    
    async def _send_request(self, request):
        """Send HTTP request with retry logic"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=request,
                timeout=self.timeout
            )
            return response.json()
        except httpx.TimeoutException:
            raise LLMTimeoutError("Model took too long to respond")
        except httpx.HTTPError as e:
            raise LLMConnectionError(f"Failed to connect: {e}")
```

---

### 5. Quality Assessment Architecture

**Modular Assessment Engine:**

```
┌─────────────────────────────────────────┐
│      Quality Assessment Orchestrator    │
│         (assessment.py)                 │
└──────────┬──────────────────────────────┘
           │
           ├──────────────────────────────┐
           │                              │
    ┌──────▼───────┐            ┌────────▼────────┐
    │ Completeness │            │  Consistency    │
    │   Analyzer   │            │   Checker       │
    └──────┬───────┘            └────────┬────────┘
           │                             │
    ┌──────▼───────┐            ┌────────▼────────┐
    │   Accuracy   │            │  Uniqueness     │
    │  Validator   │            │   Scorer        │
    └──────┬───────┘            └────────┬────────┘
           │                             │
           └────────────┬─────────────────┘
                        │
                ┌───────▼────────┐
                │  Score         │
                │  Aggregator    │
                └────────────────┘
```

**Assessment Flow:**

```
class QualityAssessmentEngine:
    """
    Orchestrates multiple quality checks
    
    Pattern: Strategy Pattern
    Each analyzer implements same interface:
    - analyze(df) -> dict
    """
    
    def __init__(self):
        self.analyzers = {
            'completeness': CompletenessAnalyzer(),
            'consistency': ConsistencyChecker(),
            'accuracy': AccuracyValidator(),
            'uniqueness': UniquenessScorer()
        }
    
    def assess(self, df):
        """
        Run all assessments in parallel
        
        Returns:
        {
            'overall_score': 87.5,
            'completeness': {...},
            'consistency': {...},
            'accuracy': {...},
            'uniqueness': {...}
        }
        """
        results = {}
        
        # Run assessments
        for name, analyzer in self.analyzers.items():
            results[name] = analyzer.analyze(df)
        
        # Calculate overall score
        results['overall_score'] = self._calculate_overall(results)
        
        return results
```

---

### 6. Anomaly Detection Architecture

**Ensemble Model Pattern:**

```
                   Input Data
                        │
                ┌───────┴────────┐
                │  Preprocessing │
                │  -  Scaling    │
                │  -  Encoding   │
                └───────┬────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼────────┐ ┌───▼────────┐ ┌───▼──────────┐
│ Isolation      │ │ Local      │ │ One-Class    │
│ Forest         │ │ Outlier    │ │ SVM          │
│                │ │ Factor     │ │              │
│ Predictions    │ │ Predictions│ │ Predictions  │
└───────┬────────┘ └────┬───────┘ └──────┬───────┘
        │               │                │
        └───────────────┼────────────────┘
                        │
                ┌───────▼────────┐
                │ Voting         │
                │ Mechanism      │
                │ (Majority)     │
                └───────┬────────┘
                        │
                   Final Results
```

**Implementation:**

```
class AnomalyDetectionEnsemble:
    """
    Ensemble of ML models for robust anomaly detection
    
    Pattern: Ensemble Learning
    Multiple models vote on anomalies
    """
    
    def __init__(self):
        self.models = {
            'isolation_forest': IsolationForest(contamination=0.1),
            'lof': LocalOutlierFactor(contamination=0.1),
            'svm': OneClassSVM(nu=0.1)
        }
    
    def detect(self, df):
        """
        Run ensemble detection
        
        Process:
        1. Preprocess data
        2. Run each model
        3. Aggregate predictions
        4. Return consensus anomalies
        """
        X = self.preprocess(df)
        
        predictions = {}
        for name, model in self.models.items():
            predictions[name] = model.fit_predict(X)
        
        # Voting: anomaly if 2+ models agree
        ensemble_pred = self.majority_vote(predictions)
        
        return {
            'anomaly_indices': np.where(ensemble_pred == -1),
            'individual_results': predictions,
            'ensemble_result': ensemble_pred
        }
```

---

### 7. Security Architecture

**Authentication Flow:**

```
1. User Registration
   ↓
   Hash password (bcrypt)
   ↓
   Store in database
   
2. User Login
   ↓
   Verify password
   ↓
   Generate JWT token
   ↓
   Return token to client
   
3. Authenticated Request
   ↓
   Extract token from header
   ↓
   Verify JWT signature
   ↓
   Decode user info
   ↓
   Allow/Deny access
```

**Implementation:**

```
# Security utilities
class SecurityManager:
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
    
    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(
            plain.encode('utf-8'),
            hashed.encode('utf-8')
        )
    
    @staticmethod
    def create_access_token(data: dict) -> str:
        """Create JWT token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        
        return jose.jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
```

---

### 8. Data Flow Architecture

**Complete Request Flow Example:**

```
1. User uploads CSV file
   ↓
2. Frontend: FileUploader.jsx
   - FormData with file
   - POST /api/v1/upload
   ↓
3. Backend: upload.py
   - Validate file type/size
   - Save to uploads/
   - Parse with pandas
   - Extract metadata
   - Save to database
   - Return DatasetMetadata
   ↓
4. Frontend: Store in Zustand
   - setCurrentDataset(metadata)
   ↓
5. User clicks "Run Assessment"
   ↓
6. Frontend: POST /api/v1/assessment/assess/{id}
   ↓
7. Backend: assessment.py
   - Load dataset from file
   - Run quality engines
   - Calculate scores
   - Return QualityMetrics
   ↓
8. Frontend: Display results
   - QualityMetricsCard.jsx
   - Update Zustand store
```

---

### 9. Performance Optimizations

**Caching Strategy:**

```
# LRU Cache for expensive operations
from functools import lru_cache

@lru_cache(maxsize=100)
def calculate_statistics(df_hash):
    """Cache statistical calculations"""
    return df.describe().to_dict()

# Dashboard cache
dashboards_cache = {}  # In-memory cache
# TTL: 1 hour or until server restart

# Model keep-alive
# Ollama keeps model in memory for quick responses
```

**Async Operations:**

```
# Parallel LLM requests
async def generate_multiple_recommendations(issues):
    """Generate recommendations in parallel"""
    tasks = [
        ollama_client.generate(f"Fix {issue}")
        for issue in issues
    ]
    return await asyncio.gather(*tasks)
```

**Database Optimization:**

```
-- Indexes on frequently queried columns
CREATE INDEX idx_dataset_user ON dataset_metadata(user_id);
CREATE INDEX idx_chat_timestamp ON chat_messages(created_at);

-- Cleanup old records
DELETE FROM dataset_metadata 
WHERE upload_timestamp < NOW() - INTERVAL '1 day';
```

---

### 10. Deployment Architecture

**Development:**
```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   React     │     │   FastAPI    │     │   Ollama     │
│ localhost:  │────▶│ localhost:   │────▶│ localhost:  │
│   5173      │     │   8000       │     │   11434      │
└─────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   SQLite     │
                    │ data_quality │
                    │    .db       │
                    └──────────────┘
```

**Production (Recommended):**
```
┌──────────────┐
│   Nginx      │ ← HTTPS (443)
│   Reverse    │
│   Proxy      │
└──────┬───────┘
       │
       ├────────────────────────┐
       │                        │
┌──────▼───────┐       ┌────────▼────────┐
│   React      │       │   FastAPI       │
│   (Static)   │       │   (Gunicorn)    │
│   Build      │       │   Workers: 4    │
└──────────────┘       └────────┬────────┘
                                │
                        ┌───────┼────────┐
                        │                │
                ┌───────▼──────┐  ┌──────▼──────┐
                │  PostgreSQL  │  │   Ollama    │
                │   Database   │  │   Server    │
                └──────────────┘  └─────────────┘
```

---

### 11. Error Handling Strategy

**Layered Error Handling:**

```
# Layer 1: API Route Level
@router.post("/assess/{dataset_id}")
async def assess_quality(dataset_id: int):
    try:
        result = await quality_engine.assess(dataset_id)
        return result
    except DatasetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")

# Layer 2: Service Level
class QualityEngine:
    def assess(self, dataset_id):
        try:
            df = self.load_dataset(dataset_id)
            return self.analyze(df)
        except FileNotFoundError:
            raise DatasetNotFoundError(f"Dataset {dataset_id} not found")
        except pd.errors.ParserError:
            raise InvalidDatasetError("Failed to parse dataset")

# Layer 3: Frontend Level
try {
  const result = await assessQuality(datasetId);
  setQualityMetrics(result);
} catch (error) {
  if (error.response?.status === 404) {
    alert('Dataset not found');
  } else {
    alert('Failed to assess quality');
  }
}
```

---

## Design Patterns Used

1. **Strategy Pattern** - Quality analyzers
2. **Factory Pattern** - Model instantiation
3. **Singleton Pattern** - Ollama client
4. **Observer Pattern** - React state updates
5. **Repository Pattern** - Database access
6. **Facade Pattern** - LLM abstraction
7. **Decorator Pattern** - Authentication
8. **Template Method** - Assessment flow

---

## Technology Choices Rationale

| Technology | Why Chosen | Alternatives Considered |
|------------|-----------|------------------------|
| FastAPI | Async support, auto docs, fast | Flask, Django |
| React | Component reusability, ecosystem | Vue, Angular |
| Ollama | Local LLM, privacy, free | OpenAI API, Azure AI |
| SQLite | Zero config, portable | PostgreSQL only |
| Pandas | Industry standard, powerful | Polars, Dask |
| Plotly | Interactive charts, React support | D3.js, Chart.js |
| Zustand | Simple, no boilerplate | Redux, Context API |

---

## Scalability Considerations

### Current Limitations:
- Single-threaded Ollama (one request at a time)
- In-memory dashboard cache (lost on restart)
- File-based storage (not distributed)
- No load balancing

### Future Scaling:
- Multiple Ollama instances with load balancer
- Redis for distributed caching
- S3/MinIO for file storage
- Kubernetes deployment
- Database read replicas
- CDN for static assets

---

## Monitoring & Observability

```
# Logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Metrics (Future)
# - Request latency
# - LLM response time
# - Cache hit rate
# - Database query time
# - Error rate

# Tracing (Future)
# - OpenTelemetry integration
# - Distributed tracing
# - Performance profiling
```

---

## Security Considerations

1. **Authentication**: JWT tokens
2. **Password Hashing**: Bcrypt
3. **SQL Injection**: SQLAlchemy ORM
4. **XSS**: React auto-escaping
5. **CSRF**: Not needed (JWT + CORS)
6. **File Upload**: Size limits, type validation
7. **Rate Limiting**: Future (nginx/middleware)

---

## Testing Strategy

```
# Unit Tests
def test_completeness_analyzer():
    analyzer = CompletenessAnalyzer()
    result = analyzer.analyze(sample_df)
    assert 'missing_percentage' in result

# Integration Tests
async def test_quality_assessment_endpoint():
    response = await client.post("/api/v1/assessment/assess/1")
    assert response.status_code == 200
    assert 'overall_score' in response.json()

# E2E Tests (Future)
# - Selenium/Playwright
# - Full user workflows
```

---

## Conclusion

This architecture is designed for:
-  **Modularity**: Easy to extend
-  **Maintainability**: Clear separation of concerns
-  **Scalability**: Can grow to production scale
-  **Testability**: Components can be tested independently
-  **Performance**: Async operations, caching
-  **Security**: Industry-standard practices

The "AI as Brain" pattern is implemented through clean abstractions that allow swapping components without affecting the entire system.
```

***
