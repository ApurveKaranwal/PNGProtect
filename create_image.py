from PIL import Image
import os

# Create a dummy image
img = Image.new('RGB', (100, 100), color = 'blue')
img.save('test_image.png')
print(f"Created test_image.png at {os.path.abspath('test_image.png')}")
