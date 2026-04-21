# AI Trap Quick Start Guide

## Installation & Setup

### 1. Backend Server

```bash
cd c:\PNG_Protect\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will start with AI Trap endpoints registered at `/trap`:
- `POST /trap/generate` - Generate poisoned variants
- `POST /trap/analyze` - Quick poisoning potential analysis
- `GET /trap/info` - System information

---

## Usage Examples

### Python

```python
import requests
import json

# Quick analysis
response = requests.post(
    'http://localhost:8000/trap/analyze',
    files={'file': open('image.png', 'rb')}
)
analysis = response.json()
print(f"Poison Score: {analysis['poison_potential_score']}")

# Generate variants (JSON)
response = requests.post(
    'http://localhost:8000/trap/generate',
    files={'file': open('image.png', 'rb')},
    data={
        'variants': 20,
        'intensity': 50,
        'format': 'json'
    }
)
package = response.json()
print(f"Generated {len(package['poisoned_images'])} variants")
print(f"Poison Strength: {package['poison_strength_score']}")

# Generate variants (ZIP download)
response = requests.post(
    'http://localhost:8000/trap/generate',
    files={'file': open('image.png', 'rb')},
    data={
        'variants': 50,
        'intensity': 75,
        'format': 'zip'
    }
)
with open('trap_package.zip', 'wb') as f:
    f.write(response.content)
```

### cURL

```bash
# Quick analysis
curl -X POST http://localhost:8000/trap/analyze \
  -F "file=@image.png"

# Generate JSON package
curl -X POST http://localhost:8000/trap/generate \
  -F "file=@image.png" \
  -F "variants=20" \
  -F "intensity=50" \
  -F "format=json" > package.json

# Generate ZIP package
curl -X POST http://localhost:8000/trap/generate \
  -F "file=@image.png" \
  -F "variants=50" \
  -F "intensity=75" \
  -F "format=zip" -o package.zip
```

### JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function generateTrap() {
  const form = new FormData();
  form.append('file', fs.createReadStream('image.png'));
  form.append('variants', '20');
  form.append('intensity', '50');
  form.append('format', 'json');

  try {
    const response = await axios.post(
      'http://localhost:8000/trap/generate',
      form,
      { headers: form.getHeaders() }
    );
    console.log(`Poison Score: ${response.data.poison_strength_score}`);
  } catch (error) {
    console.error(error);
  }
}
```

---

## Parameters Explained

### `variants` (20-100)

Number of poisoned variants to generate.

| Value | Effect | Time |
|-------|--------|------|
| 20 | Minimum (quick) | 8-10s |
| 50 | Balanced | 20-25s |
| 100 | Maximum (thorough) | 40-45s |

**Recommendation**: Start with 20, increase if poison score is low.

### `intensity` (1-100)

Poison intensity / perturbation magnitude.

| Value | Effect | Imperceptibility |
|-------|--------|------------------|
| 1-25 | Subtle | Imperceptible |
| 26-75 | Moderate | Imperceptible |
| 76-100 | Aggressive | Barely visible noise |

**Recommendation**: Use 50 for balanced attack, 75-100 for maximum damage.

### `format` (json or zip)

Output format.

**json**:
- Base64 encoded images in JSON response
- Suitable for API consumption
- Returns metadata and scores inline

**zip**:
- Traditional ZIP file download
- All variants + metadata as separate files
- Suitable for distribution

---

## Output Interpretation

### Poison Strength Score (0-100)

- **0-15**: Low - image not very poisonable
- **15-40**: Moderate - decent attack potential
- **40-70**: High - effective poisoning
- **70+**: Very High - extremely effective

### Embedding Drift (%)

- **0-0.5%**: Minimal deviation from original
- **0.5-1.5%**: Good separation
- **1.5%+**: Strong representation shift

### Confidence Drop (%)

- **0-30%**: Model still confident
- **30-60%**: Moderate uncertainty
- **60%+**: Model highly confused

### Recommendation

- **Low potential**: Increase intensity or repeat with different image
- **Moderate**: Good tradeoff between imperceptibility and attack
- **High**: Strong attack, ready for deployment

---

## Integration Patterns

### Pattern 1: Watermark + Trap

```python
# Protect image with both watermark and trap
watermark_response = requests.post(
    'http://localhost:8000/watermark/add_watermark',
    files={'file': open('image.png', 'rb')}
)
protected_image = watermark_response.content

# Generate trap for same image
trap_response = requests.post(
    'http://localhost:8000/trap/generate',
    files={'file': open('image.png', 'rb')},
    data={'variants': 20, 'intensity': 50, 'format': 'zip'}
)
trap_package = trap_response.content

# Store: original + watermarked + trap variants
```

### Pattern 2: Batch Processing

```python
import os
from concurrent.futures import ThreadPoolExecutor

def process_image(filepath):
    with open(filepath, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/trap/analyze',
            files={'file': f}
        )
    return filepath, response.json()

image_dir = '/path/to/images'
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(
        process_image,
        [os.path.join(image_dir, f) for f in os.listdir(image_dir)]
    ))
```

### Pattern 3: Conditional Trap Generation

```python
# First, analyze to decide intensity
analysis = requests.post(
    'http://localhost:8000/trap/analyze',
    files={'file': open('image.png', 'rb')}
).json()

# Generate based on analysis
intensity = 50
if analysis['poison_potential_score'] < 20:
    intensity = 75  # More aggressive
elif analysis['poison_potential_score'] > 50:
    intensity = 25  # More subtle

trap_package = requests.post(
    'http://localhost:8000/trap/generate',
    files={'file': open('image.png', 'rb')},
    data={'variants': 30, 'intensity': intensity, 'format': 'json'}
).json()
```

---

## Testing

### Run Test Suite

```bash
cd c:\PNG_Protect
python test_trap.py
```

### Debug Single Request

```bash
python debug_trap.py
```

### Manual Endpoint Test

```bash
# Check server health
curl http://localhost:8000/

# Get AI Trap info
curl http://localhost:8000/trap/info

# Analyze a test image
curl -X POST http://localhost:8000/trap/analyze \
  -F "file=@test.png"
```

---

## Troubleshooting

### Issue: 400 Bad Request - "Variants must be between 20 and 100"

**Solution**: Ensure `variants` parameter is between 20-100.

```bash
# ✗ Wrong (too few)
curl -X POST http://localhost:8000/trap/generate \
  -F "variants=5"

# ✓ Correct
curl -X POST http://localhost:8000/trap/generate \
  -F "variants=20"
```

### Issue: 400 Bad Request - "File must be an image"

**Solution**: Ensure file has correct content-type.

```bash
# Make sure the file is actually a valid image
file image.png  # Should show: image: PNG image data

# Proper upload
curl -X POST http://localhost:8000/trap/analyze \
  -F "file=@image.png"
```

### Issue: 500 Internal Server Error

**Solution**: Check server logs for details.

```powershell
# View server terminal for error messages
# Usually indicates:
# - Image format issue
# - GPU memory error (shouldn't happen on CPU)
# - Model loading failure
```

### Issue: Slow Generation (>30s for 20 variants)

**Solution**: Normal on CPU. For faster processing:
- Reduce `variants` to 20
- Skip analysis if not needed
- Use separate server for large batches

---

## Performance Tips

1. **Analyze First**: Use `/trap/analyze` to check poisonability before full generation
2. **Batch Wisely**: Generate multiple traps in parallel from different images
3. **Intensity Tuning**: Use intensity 50 as baseline, adjust based on results
4. **Format Choice**: Use JSON for API, ZIP for distribution

---

## References

- Full documentation: See [AI_TRAP_README.md](AI_TRAP_README.md)
- Test examples: See [test_trap.py](../../test_trap.py)
- API specification: `GET /trap/info`

