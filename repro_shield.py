import requests
from io import BytesIO
from PIL import Image
import numpy as np
import os

# Create a dummy image
img = Image.new('RGB', (100, 100), color = 'red')
img_byte_arr = BytesIO()
img.save(img_byte_arr, format='PNG')
img_byte_arr.seek(0)

url = 'http://127.0.0.1:8000/protect/process'
files = {'file': ('test.png', img_byte_arr, 'image/png')}
data = {'strength': '80'} # High strength

print(f"Sending request to {url}...")
try:
    response = requests.post(url, files=files, data=data)
    
    print(f"Status Code: {response.status_code}")
    print("Headers:", response.headers)
    
    if 'X-Robustness-Score' in response.headers:
        print(f"Success! Score: {response.headers['X-Robustness-Score']}")
    else:
        print("FAILURE: X-Robustness-Score header missing")
        
    if response.status_code == 200:
        # Check if image has noise
        out_img = Image.open(BytesIO(response.content))
        in_arr = np.array(img)
        out_arr = np.array(out_img)
        
        diff = np.abs(in_arr.astype(int) - out_arr.astype(int))
        print(f"Mean pixel difference: {np.mean(diff)}")
        if np.mean(diff) > 0:
            print("Visible noise detected (pixels changed)")
        else:
            print("No noise detected (image identical)")
            
except Exception as e:
    print(f"Error: {e}")
