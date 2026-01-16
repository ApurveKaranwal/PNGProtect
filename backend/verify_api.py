import requests
import os

def test_protection(url="http://127.0.0.1:8000/protect/process"):
    # We are running from backend dir, so image is in parent dir
    image_path = "../test_image.png"
    if not os.path.exists(image_path):
        # Fallback create in current dir
        image_path = "temp_test.png"
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image_path)

    print(f"Testing {url} with {image_path}...")
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        # send strength as string
        data = {"strength": "50"}
        try:
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                print("✅ Success! Response 200 OK")
                print(f"Headers: {response.headers}")
                robustness = response.headers.get("X-Robustness-Score")
                print(f"Robustness Score: {robustness}")
                
                with open("protected_result.png", "wb") as f_out:
                    f_out.write(response.content)
                print("Saved protected_result.png")
            else:
                print(f"❌ Failed! Status: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    test_protection()
