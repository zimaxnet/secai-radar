
import google.generativeai as genai
import inspect

print("genai attributes:")
print(dir(genai))

try:
    from google.generativeai import files
    print("\ngoogle.generativeai.files attributes:")
    print(dir(files))
except ImportError:
    print("\nCould not import google.generativeai.files")

try:
    print("\nChecking for create_file_store in genai:")
    if hasattr(genai, 'create_file_store'):
        print("Found create_file_store in genai")
    else:
        print("create_file_store NOT found in genai")
except Exception as e:
    print(f"Error checking genai: {e}")
