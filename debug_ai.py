import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.ai.parameter_extractor import ParameterExtractor
from config import config

# Mock config if needed, but it should load from env/file
# config.OPENAI_API_KEY = "..." 

def debug_ai():
    print("Initializing Extractor...")
    try:
        extractor = ParameterExtractor()
    except Exception as e:
        print(f"Failed to init extractor: {e}")
        return

    test_input = "streamname soll test123 sein"
    print(f"\nTesting input: '{test_input}'")
    
    try:
        result = extractor.extract(test_input)
        print("\n--- Result ---")
        print(f"Job Type: {result.job_type}")
        print(f"Extracted Params: {result.model_dump(exclude_none=True)}")
    except Exception as e:
        print(f"Extraction failed: {e}")

if __name__ == "__main__":
    debug_ai()
