
import asyncio
import sys
import os
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

async def test_rag_mock():
    print("Testing Google File Search RAG (Mocked)...")
    
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "mock-key", "GOOGLE_FILE_STORE_ID": "mock-store"}):
        with patch('google.generativeai.configure') as mock_config:
            with patch('google.generativeai.GenerativeModel') as mock_model_cls:
                # Setup mock model
                mock_model = MagicMock()
                mock_response = MagicMock()
                mock_response.text = "This is a mocked response from the knowledge base."
                mock_model.generate_content.return_value = mock_response
                mock_model_cls.return_value = mock_model
                
                try:
                    from rag.google_file_search import GoogleFileSearchRetriever
                    
                    # Initialize
                    print("Initializing retriever...")
                    retriever = GoogleFileSearchRetriever()
                    print(f"Retriever initialized with File Store ID: {retriever.file_store_id}")
                    
                    # Test retrieval
                    print("Testing retrieval...")
                    query = "What is SecAI Radar?"
                    result = await retriever.retrieve(query)
                    
                    if result == "This is a mocked response from the knowledge base.":
                        print(f"✅ Retrieval successful (Mocked). Result: {result}")
                    else:
                        print(f"❌ Retrieval returned unexpected result: {result}")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
                    import traceback
                    traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_rag_mock())
