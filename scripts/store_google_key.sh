
#!/bin/bash
# scripts/store_google_key.sh

KV_NAME="secai-radar-kv"

echo "SecAI Radar - Store Google API Key"
echo "=================================="
echo "Target Key Vault: $KV_NAME"
echo ""

# Check if logged in
az account show > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ You need to login to Azure first. Run 'az login'."
    exit 1
fi

# Input key
read -s -p "Enter Google API Key (hidden input): " GOOGLE_KEY
echo ""

if [ -n "$GOOGLE_KEY" ]; then
    echo "Storing secret 'google-api-key'..."
    az keyvault secret set \
        --vault-name "$KV_NAME" \
        --name "google-api-key" \
        --value "$GOOGLE_KEY" > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Google API Key stored successfully!"
        echo "You can now run the RAG test: python3 test_rag_simple.py"
    else
        echo "❌ Failed to store secret."
    fi
else
    echo "⚠️  No key entered. Operation cancelled."
fi
