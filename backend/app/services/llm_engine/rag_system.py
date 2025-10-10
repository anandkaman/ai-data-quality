from sentence_transformers import SentenceTransformer
from typing import List, Dict
import json
import numpy as np
from app.core.config import settings

class RAGSystem:
    """Retrieval Augmented Generation for data quality knowledge - Simplified"""
    
    def __init__(self, persist_directory: str = None):
        # Initialize embedding model (runs locally)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize in-memory knowledge base
        self.knowledge_base = []
        self.embeddings = []
        
        # Initialize with domain knowledge
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize with curated data quality knowledge"""
        
        knowledge_items = [
            {
                "id": "completeness_1",
                "pattern": "High missing rate in single column",
                "diagnosis": "Column may be optional or recently added",
                "solution": "Impute using median/mode or create indicator variable",
                "risk": "Medium - may lose information if dropped"
            },
            {
                "id": "completeness_2",
                "pattern": "Correlated missing values across multiple columns",
                "diagnosis": "Systematic data collection issue or conditional logic",
                "solution": "Investigate data source, consider multivariate imputation",
                "risk": "High - indicates structural problem"
            },
            {
                "id": "consistency_1",
                "pattern": "Multiple formats for same data type",
                "diagnosis": "Inconsistent data entry or multiple data sources",
                "solution": "Standardize format using regex/parsing rules",
                "risk": "Low - can be automated safely"
            },
            {
                "id": "outlier_1",
                "pattern": "Extreme values in bounded field",
                "diagnosis": "Data entry error or measurement error",
                "solution": "Cap/floor values, investigate source",
                "risk": "Medium - may be legitimate extreme cases"
            },
            {
                "id": "uniqueness_1",
                "pattern": "Duplicate records with minor variations",
                "diagnosis": "Fuzzy duplicates from data entry or merging",
                "solution": "Use fuzzy matching (Levenshtein distance) for deduplication",
                "risk": "High - incorrect merging loses data"
            },
            {
                "id": "accuracy_1",
                "pattern": "Values outside expected range",
                "diagnosis": "Data entry errors or system glitches",
                "solution": "Apply range validation and outlier detection",
                "risk": "Medium - some outliers may be valid"
            },
            {
                "id": "timeliness_1",
                "pattern": "Outdated or stale data",
                "diagnosis": "Delayed data pipeline or collection issues",
                "solution": "Implement automated data refresh schedules",
                "risk": "Low - straightforward fix"
            }
        ]
        
        for item in knowledge_items:
            text = f"{item['pattern']} | {item['diagnosis']} | {item['solution']}"
            self.add_knowledge(item['id'], text, item)
    
    def add_knowledge(self, id: str, text: str, metadata: Dict):
        """Add knowledge to RAG system"""
        embedding = self.embedding_model.encode(text)
        
        self.knowledge_base.append({
            'id': id,
            'text': text,
            'metadata': metadata
        })
        self.embeddings.append(embedding)
    
    def retrieve_relevant_knowledge(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict]:
        """Retrieve relevant knowledge for a query using cosine similarity"""
        
        if not self.knowledge_base:
            return []
        
        query_embedding = self.embedding_model.encode(query)
        
        # Calculate cosine similarities
        similarities = []
        for i, emb in enumerate(self.embeddings):
            similarity = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb)
            )
            similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top n results
        results = []
        for idx, sim in similarities[:n_results]:
            item = self.knowledge_base[idx].copy()
            item['similarity'] = float(sim)
            results.append(item)
        
        return results
