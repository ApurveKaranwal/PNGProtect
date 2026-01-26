import requests
import base64
from PIL import Image
import io
import sys

# URL
url = "http://localhost:8000/analyze/ai-vision"

# Create a simple dummy image
print("Creating dummy image...")
img = Image.new('RGB', (224, 224), color = 'red')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# Send Request
print(f"Sending request to {url}...")
try:
    files = {'file': ('test.png', img_bytes, 'image/png')}
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        print("Success!")
        print(f"Model: {data['model']}")
        print(f"Original Prediction: {data['original_prediction']}")
        print(f"Protected Prediction: {data['protected_prediction']}")
        print(f"Confusion Score: {data['confusion_score']}")
        
        # Check heatmap
        heatmap_b64 = data['heatmap_base64']
        if heatmap_b64.startswith("data:image/png;base64,"):
            print("Heatmap received (base64).")
            # Optional: Save it
            # b64_data = heatmap_b64.split(",")[1]
            # with open("heatmap_test.png", "wb") as f:
            #     f.write(base64.b64decode(b64_data))
        else:
            print("Warning: Heatmap format unexpected.")
            
    else:
        print(f"Failed with status {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Error: {e}")
    # If connection refused, maybe server isn't running.
    print("Ensure the server is running on localhost:8000")
