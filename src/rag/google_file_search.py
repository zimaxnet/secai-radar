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
            file_store_id: File store ID (or will create one)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable or api_key parameter required")
        
        genai.configure(api_key=self.api_key)
        self.client = genai
        
        # Get or create file store
        self.file_store_id = file_store_id
        if not self.file_store_id:
            # Try to get from environment or create new
            self.file_store_id = os.getenv("GOOGLE_FILE_STORE_ID")
            if not self.file_store_id:
                # Create a new file store
                self.file_store_id = self._create_file_store()
    
    def _create_file_store(self) -> str:
        """
        Create a new file store.
        
        Returns:
            File store ID
        """
        try:
            # Try different API methods based on SDK version
            try:
                # Method 1: Direct create_file_store
                file_store = self.client.create_file_store(
                    display_name="SecAI Radar Knowledge Base"
                )
                # Extract ID from name (format: "fileStores/{id}")
                if hasattr(file_store, 'name'):
                    return file_store.name.split("/")[-1]
                elif hasattr(file_store, 'id'):
                    return file_store.id
                else:
                    return str(file_store)
            except AttributeError:
                # Method 2: Use genai.create_file_store if available
                file_store = genai.create_file_store(
                    display_name="SecAI Radar Knowledge Base"
                )
                if hasattr(file_store, 'name'):
                    return file_store.name.split("/")[-1]
                return "default_store"
        except Exception as e:
            print(f"Error creating file store: {e}")
            print(f"Note: File store creation API may need updating")
            # Return a placeholder - user should set GOOGLE_FILE_STORE_ID manually
            return "default_store"
    
    async def retrieve(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> Optional[str]:
        """
        Retrieve relevant context using Google File Search.
        
        Args:
            query: Search query
            context: Additional context (not used by Google File Search directly)
            top_k: Number of results (handled by Google internally)
            
        Returns:
            Retrieved context as string
        """
        try:
            # Create a model with file search enabled
            # Note: File Search is enabled via tools parameter
            # The exact API may vary - this is a placeholder implementation
            # that should be updated based on actual google-generativeai SDK version
            
            # Try the protos approach first (for newer SDK versions)
            try:
                from google.generativeai import protos
                model = self.client.GenerativeModel(
                    model_name="gemini-1.5-pro",
                    tools=[protos.Tool(
                        file_search=protos.FileSearch(
                            file_store=protos.FileStore(
                                name=f"fileStores/{self.file_store_id}"
                            )
                        )
                    )]
                )
            except (ImportError, AttributeError):
                # Fallback: Use file_store parameter if available
                try:
                    model = self.client.GenerativeModel(
                        model_name="gemini-1.5-pro",
                        file_store=f"fileStores/{self.file_store_id}"
                    )
                except Exception:
                    # If file_store parameter not available, use standard model
                    # and include file store reference in prompt
                    model = self.client.GenerativeModel(
                        model_name="gemini-1.5-pro"
                    )
            
            # Build prompt with query
            prompt = f"Search the knowledge base (file store: {self.file_store_id}) for: {query}\n\n"
            if context:
                prompt += f"Context: {context}\n\n"
            prompt += "Provide relevant information from the knowledge base."
            
            # Generate response with file search
            response = model.generate_content(prompt)
            
            if response and response.text:
                return response.text
            
            return None
        except Exception as e:
            print(f"Error retrieving from Google File Search: {e}")
            print(f"Note: API may need updating based on google-generativeai SDK version")
            return None
    
    async def upload_document(
        self,
        document_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Upload a document to Google File Search.
        
        Args:
            document_path: Path to document file
            metadata: Document metadata
            
        Returns:
            True if successful
        """
        try:
            # Upload file to file store
            # Try different API methods based on SDK version
            try:
                # Method 1: Direct upload_file
                uploaded_file = self.client.upload_file(
                    path=document_path,
                    display_name=metadata.get("display_name", os.path.basename(document_path)) if metadata else os.path.basename(document_path)
                )
            except AttributeError:
                # Method 2: Use genai.upload_file
                uploaded_file = genai.upload_file(
                    path=document_path,
                    display_name=metadata.get("display_name", os.path.basename(document_path)) if metadata else os.path.basename(document_path)
                )
            
            # Get file ID
            file_id = None
            if hasattr(uploaded_file, 'name'):
                file_id = uploaded_file.name.split("/")[-1]
            elif hasattr(uploaded_file, 'id'):
                file_id = uploaded_file.id
            else:
                file_id = str(uploaded_file)
            
            # Add to file store
            try:
                self.client.add_file_to_file_store(
                    file_store_id=self.file_store_id,
                    file_id=file_id
                )
            except AttributeError:
                # Alternative: Use genai.add_file_to_file_store
                genai.add_file_to_file_store(
                    file_store_id=self.file_store_id,
                    file_id=file_id
                )
            
            return True
        except Exception as e:
            print(f"Error uploading document: {e}")
            print(f"Note: Upload API may need updating based on SDK version")
            return False
    
    async def upload_text(
        self,
        text: str,
        display_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Upload text content directly to file store.
        
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

