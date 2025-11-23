
import google.generativeai as genai
from google.generativeai import protos

print("Checking protos for FileStore...")
if hasattr(protos, 'FileStore'):
    print("Found protos.FileStore")
else:
    print("protos.FileStore NOT found")

if hasattr(protos, 'Tool'):
    print("Found protos.Tool")

if hasattr(protos, 'FileSearch'):
    print("Found protos.FileSearch")
    
print("\nChecking genai for other file methods...")
# Check if there is a beta module
try:
    from google.generativeai import beta
    print("Found google.generativeai.beta")
    print(dir(beta))
except ImportError:
    print("No google.generativeai.beta")
