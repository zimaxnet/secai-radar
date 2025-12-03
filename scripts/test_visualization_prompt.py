import sys
import os
import json
import logging

# Add api directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../api'))

# Load environment variables from local.settings.json
try:
    with open(os.path.join(os.path.dirname(__file__), '../api/local.settings.json'), 'r') as f:
        settings = json.load(f)
        for key, value in settings.get('Values', {}).items():
            if key not in os.environ:
                os.environ[key] = value
    
    # Ensure KEY_VAULT_URL is set
    if "KEY_VAULT_URL" not in os.environ:
        os.environ["KEY_VAULT_URL"] = "https://secai-radar-kv.vault.azure.net/"
except Exception as e:
    print(f"Warning: Could not load local.settings.json: {e}")

# Import AI service
try:
    from shared.ai_service import get_ai_service
except ImportError as e:
    print(f"Error importing AI service: {e}")
    sys.exit(1)

def test_visualization_prompt():
    print("Initializing AI Service...")
    try:
        ai_service = get_ai_service()
    except Exception as e:
        print(f"Failed to initialize AI service: {e}")
        return

    print("\n--- Testing Visualization Prompt (Elena Bridges) ---")
    
    # Test case 1: Executive Dashboard
    intent = "Show me an executive dashboard of our current security posture"
    style = "infographic"
    context_type = "assessment"
    assessment_data = {
        "summary": {
            "totalControls": 50,
            "totalGaps": 12,
            "criticalGaps": 3,
            "byDomain": [
                {"domain": "Identity", "complete": 8, "total": 10},
                {"domain": "Network", "complete": 15, "total": 20},
                {"domain": "Data", "complete": 15, "total": 20}
            ]
        }
    }
    
    print(f"\nIntent: {intent}")
    print(f"Style: {style}")
    
    try:
        result = ai_service.craft_visualization_prompt(
            user_intent=intent,
            context_type=context_type,
            assessment_data=assessment_data,
            style=style
        )
        
        print("\nResult:")
        print(json.dumps(result, indent=2))
        
        if result.get("agent") == "elena_bridges":
            print("\nSUCCESS: Elena Bridges agent successfully crafted the prompt.")
        else:
            print("\nFAILURE: Agent identity mismatch.")
            
    except Exception as e:
        print(f"\nError during prompt generation: {e}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    test_visualization_prompt()
