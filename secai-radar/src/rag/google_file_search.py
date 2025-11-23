"""
Google File Search Retriever

Implementation using Google Gemini API File Search for RAG.
This is a fully managed RAG system that handles embeddings and retrieval automatically.
"""

import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from .base_retriever import BaseRetriever


class GoogleFileSearchRetriever(BaseRetriever):
    """
    Google File Search retriever using Gemini API.
    
    This uses Google's managed File Search service which handles:
    - Document storage
    - Chunking
    - Embeddings
    - Vector search
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        file_store_id: Optional[str] = None
    ):
        """
        Initialize Google File Search retriever.
        
        Args:
            api_key: Google API key (or set GOOGLE_API_KEY env var)
            file_store_id: Not used in this implementation (kept for compatibility)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            # Try to get from Key Vault if not in env
            try:
                from shared.key_vault import get_secret_from_key_vault_or_env
                self.api_key = get_secret_from_key_vault_or_env("google-api-key", "GOOGLE_API_KEY")
            except ImportError:
                pass
                
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable or api_key parameter required")
        
        genai.configure(api_key=self.api_key)
        self.client = genai
        
        # Track uploaded files
        self.uploaded_files = []
        self.model_name = "gemini-flash-latest"
    
    async def retrieve(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> Optional[str]:
        """
        Retrieve relevant context using Google Gemini Long Context.
        
        Args:
            query: Search query
            context: Additional context
            top_k: Not used
            
        Returns:
            Retrieved context as string
        """
        try:
            if not self.uploaded_files:
                print("Warning: No files uploaded for retrieval")
                return None
                
            # Get file handles
            file_handles = []
            for file_name in self.uploaded_files:
                try:
                    file_obj = self.client.get_file(file_name)
                    file_handles.append(file_obj)
                except Exception as e:
                    print(f"Error getting file {file_name}: {e}")
            
            if not file_handles:
                return None
                
            # Create model
            model = self.client.GenerativeModel(model_name=self.model_name)
            
            # Build prompt
            prompt = f"Answer the following query based on the provided documents: {query}\n\n"
            if context:
                prompt += f"Context: {context}\n\n"
            prompt += "Provide relevant information from the documents."
            
            # Generate content with files in context
            content = [prompt] + file_handles
            response = model.generate_content(content)
            
            if response and response.text:
                return response.text
            
            return None
        except Exception as e:
            print(f"Error retrieving from Google: {e}")
            return None
    
    async def upload_document(
        self,
        document_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Upload a document to Google.
        
        Args:
            document_path: Path to document file
            metadata: Document metadata
            
        Returns:
            True if successful
        """
        try:
            display_name = metadata.get("display_name", os.path.basename(document_path)) if metadata else os.path.basename(document_path)
            
            uploaded_file = self.client.upload_file(
                path=document_path,
                display_name=display_name
            )
            
            # Wait for processing
            import time
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(1)
                uploaded_file = self.client.get_file(uploaded_file.name)
                
            if uploaded_file.state.name == "FAILED":
                print(f"File upload failed: {uploaded_file.state.name}")
                return False
                
            self.uploaded_files.append(uploaded_file.name)
            return True
        except Exception as e:
            print(f"Error uploading document: {e}")
            return False
    
    async def upload_text(
        self,
        text: str,
        display_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Upload text content directly.
        
        Args:
            text: Text content
            display_name: Display name for the document
            metadata: Document metadata
            
        Returns:
            True if successful
        """
        try:
            # Create a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text)
                temp_path = f.name
            
            # Upload the file
            result = await self.upload_document(temp_path, {
                "display_name": display_name,
                **(metadata or {})
            })
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return result
        except Exception as e:
            print(f"Error uploading text: {e}")
            return False


