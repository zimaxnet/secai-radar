
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Load env vars (including KEY_VAULT_URL if needed, but we'll use the exported key)
load_dotenv()

def test_upload_and_query():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return

    print(f"Using API Key: {api_key[:5]}...")
    genai.configure(api_key=api_key)

    # Create a dummy file
    with open("test_doc.txt", "w") as f:
        f.write("SecAI Radar is a specialized security tool for Azure environments. It uses multiple AI agents to assess security posture.")

    try:
        print("Uploading file...")
        sample_file = genai.upload_file(path="test_doc.txt", display_name="SecAI Test Doc")
        print(f"File uploaded: {sample_file.name}")
        
        # Wait for processing
        print("Waiting for file processing...")
        while sample_file.state.name == "PROCESSING":
            time.sleep(2)
            sample_file = genai.get_file(sample_file.name)
            print(f"State: {sample_file.state.name}")
            
        if sample_file.state.name == "FAILED":
            print("❌ File processing failed")
            return

        print("File ready. Querying model...")
        model = genai.GenerativeModel(model_name="gemini-flash-latest")
        
        response = model.generate_content([
            "What is SecAI Radar?",
            sample_file
        ])
        
        print(f"Response: {response.text}")
        print("✅ Test successful")
        
        # Cleanup
        print("Deleting file...")
        genai.delete_file(sample_file.name)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists("test_doc.txt"):
            os.remove("test_doc.txt")

if __name__ == "__main__":
    test_upload_and_query()
