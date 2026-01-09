import io
import numpy as np
from PIL import Image

def load_image_from_bytes(raw_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(raw_bytes)).convert("RGB")

def save_image_to_bytes(image: Image.Image, format_hint: str = "png") -> io.BytesIO:
    buf = io.BytesIO()
    # LSB requires lossless (PNG). If JPEG is passed, we force PNG for the watermark to survive
    save_format = "PNG" if "png" in format_hint.lower() or "jpg" in format_hint.lower() or "jpeg" in format_hint.lower() else "PNG"
    image.save(buf, format=save_format)
    buf.seek(0)
    return buf

def embed_watermark_lsb(image: Image.Image, watermark_text: str, strength: int = 5):
    """Embeds text into LSB. 'strength' here acts as a redundancy multiplier."""
    # Ensure image is in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    data = watermark_text + "@@@@"
    binary_data = ''.join(format(ord(i), '08b') for i in data)
    
    # Simple redundancy based on strength
    binary_data = binary_data * strength 
    
    pixels = np.array(image, dtype=np.uint16)  # Use uint16 to avoid overflow
    original_shape = pixels.shape
    flat = pixels.flatten()
    
    if len(binary_data) > len(flat):
        raise ValueError(f"Image too small for this strength/text. Need {len(binary_data)} bits but only have {len(flat)} pixels.")

    for i in range(len(binary_data)):
        # Clear the LSB and set it to the watermark bit
        flat[i] = (int(flat[i]) & 0xFE) | int(binary_data[i])
    
    # Convert back to uint8 and reshape
    modified_pixels = (flat.reshape(original_shape) & 0xFF).astype(np.uint8)
    watermarked_image = Image.fromarray(modified_pixels, mode='RGB')
    
    return watermarked_image, binary_data

def extract_watermark_lsb(image: Image.Image):
    """Extracts bits and looks for the @@@@ delimiter."""
    # Ensure image is in RGB mode (same as embedding)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    pixels = np.array(image, dtype=np.uint8)
    flat = pixels.flatten()
    
    binary_data = "".join([str(int(flat[i]) & 1) for i in range(min(len(flat), 16000))])
    
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded = ""
    for b in all_bytes:
        try:
            char = chr(int(b, 2))
            decoded += char
            if "@@@@" in decoded:
                final_text = decoded.split("@@@@")[0]
                return final_text, 1.0 # Match ratio 1.0 for found
        except:
            continue
            
    return "Unknown", 0.1 # Match ratio 0.1 for not found

def strip_metadata_from_image(image: Image.Image) -> Image.Image:
    """
    Removes all metadata and EXIF data from the image.
    Returns a clean image with only pixel data preserved.
    Preserves image format and converts to RGB if needed.
    """
    # Create a new image with only pixel data
    # This removes all metadata, EXIF, encoding information, etc.
    data = list(image.getdata())
    image_without_metadata = Image.new(image.mode, image.size)
    image_without_metadata.putdata(data)
    
    return image_without_metadata