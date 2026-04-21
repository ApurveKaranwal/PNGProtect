"""
Debug test for trap endpoint
"""

import requests
import io
from PIL import Image

# Test configuration
API_BASE = "http://localhost:8000"
TRAP_ENDPOINT = f"{API_BASE}/trap"

def create_sample_image(width=256, height=256) -> bytes:
    """Create a sample RGB image for testing."""
    img = Image.new('RGB', (width, height), color='red')
    # Add some variation
    pixels = img.load()
    for i in range(0, width, 10):
        for j in range(0, height, 10):
            pixels[i, j] = (100 + (i % 155), 100 + (j % 155), 100 + ((i+j) % 155))
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()

def test_generate_json():
    """Test generate endpoint"""
    image_bytes = create_sample_image()
    
    files = {'file': ('test_image.png', image_bytes, 'image/png')}
    data = {
        'variants': 20,
        'intensity': 50,
        'format': 'json'
    }
    
    response = requests.post(f"{TRAP_ENDPOINT}/generate", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Response: {response.text[:500]}")

if __name__ == "__main__":
    test_generate_json()
