from deepface import DeepFace
import numpy as np

try:
    print("Testing DeepFace...")
    # Just a small test with a blank image or something
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    # This might fail if no models are downloaded, but it checks if import works
    print("DeepFace imported successfully.")
except Exception as e:
    print(f"DeepFace test failed: {e}")
