
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src and api to path
sys.path.append(os.path.join(os.getcwd(), "src"))
sys.path.append(os.path.join(os.getcwd(), "api"))

# Load env vars
load_dotenv()

async def test_rag():
    print("Testing Google File Search RAG...")
    
    # Try to get API key from Key Vault
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        try:
            print("Attempting to retrieve GOOGLE_API_KEY from Azure Key Vault...")
            from shared.key_vault import get_secret_from_key_vault_or_env
            google_api_key = get_secret_from_key_vault_or_env("google-api-key")
            if google_api_key:
                print("✅ Retrieved API key from Key Vault")
                # Set env var for the retriever to pick up
                os.environ["GOOGLE_API_KEY"] = google_api_key
            else:
                print("⚠️  Could not find 'google-api-key' in Key Vault")
        except Exception as e:
            print(f"⚠️  Error accessing Key Vault: {e}")
            print("Ensure you are logged in via 'az login' and have access to the Key Vault.")

    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found in environment or Key Vault.")
        print("Please set it or add 'google-api-key' to your Azure Key Vault.")
        return

    try:
        from rag.google_file_search import GoogleFileSearchRetriever
        
        # Initialize
        print("Initializing retriever...")
        retriever = GoogleFileSearchRetriever()
        # print(f"Retriever initialized with File Store ID: {retriever.file_store_id}")
        
        # Upload test content
        print("Uploading test content...")
        test_content = "SecAI Radar is a multi-agent security assessment tool for Azure."
        success = await retriever.upload_text(
            text=test_content,
            display_name="Test Document",
            metadata={"type": "test"}
        )
        
        if success:
            print("✅ Upload successful")
        else:
            print("❌ Upload failed")
            return
            
        # Wait a moment for processing
        await asyncio.sleep(2)
        
        # Test retrieval
        print("Testing retrieval...")
        query = "What is SecAI Radar?"
        result = await retriever.retrieve(query)
        
        if result:
            print(f"✅ Retrieval successful. Result:\n{result}")
        else:
            print("❌ Retrieval returned no results")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_rag())
