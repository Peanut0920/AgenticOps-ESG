"""
Database connectors for persistent storage and vector retrieval.
Includes a mock RAG (Retrieval-Augmented Generation) database for regulatory texts.
"""

import os
from typing import List, Dict, Any, Optional

class Document:
    """Simple document container for RAG search results."""
    def __init__(self, text: str, metadata: Dict[str, Any]):
        self.text = text
        self.metadata = metadata

class VectorDatabase:
    """
    Mock vector database for regulatory RAG (Bursa, MCMC, GRI, SASB).
    In production, this would be backed by ChromaDB or Pinecone with embeddings.
    """

    def __init__(self, persist_directory: str = "./data/rag_db"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Embedded regulatory knowledge base (simulated)
        self._knowledge_base = {
            "dell_r760": {
                "text": "Dell R760 server. Embodied carbon: 850 kg CO2e per unit (manufacturing + logistics).",
                "metadata": {"embodied_kg_co2": 850, "sku": "Dell_R760"}
            },
            "mcmc_data_sovereignty": {
                "text": "MCMC Technical Code Section 5.2: All personally identifiable and critical infrastructure data must remain within Malaysia's geographical borders (MY-01 region).",
                "metadata": {"clause": "5.2", "jurisdiction": "Malaysia"}
            },
            "bursa_tcfd_risk": {
                "text": "Bursa Malaysia Sustainability Guide, Appendix 4C: Companies must disclose climate-related transition risks, including operational resilience to power grid volatility and hardware failure.",
                "metadata": {"clause": "4C", "jurisdiction": "Malaysia"}
            },
            "gri_305": {
                "text": "GRI 305-2: Scope 2 emissions (location-based) must be reported in tCO2e, calculated using grid-average emission factors.",
                "metadata": {"standard": "GRI", "code": "305-2"}
            },
            "sasb_tc_hw": {
                "text": "SASB TC-HW-130a.1: Disclose total energy consumed, percentage grid electricity, percentage renewable, and Power Usage Effectiveness (PUE) for data centers.",
                "metadata": {"standard": "SASB", "code": "TC-HW-130a.1"}
            }
        }

    def similarity_search(self, query: str, k: int = 1) -> List[Document]:
        """
        Performs a keyword-based similarity search (mock) against the regulatory knowledge base.

        Args:
            query: The search string (e.g., "MCMC data sovereignty").
            k: Number of top results to return.

        Returns:
            List of Document objects containing text and metadata.
        """
        results = []
        query_lower = query.lower()
        
        for key, value in self._knowledge_base.items():
            # Simple substring matching for mock
            if key in query_lower or any(word in key for word in query_lower.split()):
                results.append(Document(value["text"], value["metadata"]))
        
        # If no match, return a generic fallback
        if not results:
            results.append(Document(
                "General compliance: All operations must adhere to local data protection and sustainability laws.",
                {"source": "fallback", "embodied_kg_co2": 900}
            ))
        
        return results[:k]

    def ingest_pdf(self, file_path: str, metadata: Dict[str, Any]) -> "VectorDatabase":
        """
        Mock PDF ingestion. In production, this would parse, chunk, embed, and index PDFs.

        Args:
            file_path: Path to the regulatory PDF.
            metadata: Additional metadata to store with the document.

        Returns:
            Self for method chaining.
        """
        print(f"[RAG] Simulating ingestion of PDF: {file_path} with metadata {metadata}")
        # In a real implementation, you would:
        # 1. Extract text via pdfplumber
        # 2. Chunk text into segments
        # 3. Generate embeddings via sentence-transformers
        # 4. Store in ChromaDB
        return self