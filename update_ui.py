import os

# 1. Update style.css with Inter font
style_path = 'frontend/style.css'
with open(style_path, 'r', encoding='utf-8') as f:
    css = f.read()

font_import = "@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@700&display=swap');\n@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');\n"
css = css.replace("@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@700&display=swap');", font_import)
css = css.replace("font-family: system-ui, -apple-system, BlinkMacSystemFont, \"SF Pro Text\",\n    \"Segoe UI\", sans-serif;", "font-family: 'Inter', system-ui, -apple-system, sans-serif;")

with open(style_path, 'w', encoding='utf-8') as f:
    f.write(css)

# 2. Update index.html with SVGs and Tech Stack
index_path = 'frontend/index.html'
with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

icons = [
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg>',
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>'
]

parts = html.split('<div class="feature-icon-lg">')
new_html = parts[0]
icon_idx = 0
for i in range(1, len(parts)):
    end_idx = parts[i].find('</div>')
    if icon_idx < len(icons):
        new_html += '<div class="feature-icon-lg">' + icons[icon_idx] + parts[i][end_idx:]
        icon_idx += 1
    else:
        new_html += '<div class="feature-icon-lg">' + parts[i]

tech_stack_html = """
    <!-- TECH STACK SECTION -->
    <section id="tech-stack" class="section tech-stack-section" style="margin-top: 40px;">
      <div class="section-header">
        <h2>Technology Stack</h2>
        <p>Built with modern, production-ready frameworks and advanced machine learning models.</p>
      </div>
      
      <div class="tech-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px; max-width: 1100px; margin: 0 auto;">
        
        <div class="glass card tech-card" style="padding: 30px;">
          <h3 style="margin-top: 0; margin-bottom: 20px; color: var(--accent-blue);">Frontend</h3>
          <ul style="list-style: none; padding: 0; margin: 0; color: var(--text-soft); line-height: 2;">
            <li><strong style="color: var(--text-main);">HTML5 &amp; CSS3</strong> - Modern Glassmorphism</li>
            <li><strong style="color: var(--text-main);">Vanilla ES6+ JS</strong> - No heavy frameworks</li>
            <li><strong style="color: var(--text-main);">Ethers.js v5.7</strong> - Web3 Integration</li>
            <li><strong style="color: var(--text-main);">Three.js</strong> - 3D Backgrounds</li>
          </ul>
        </div>

        <div class="glass card tech-card" style="padding: 30px;">
          <h3 style="margin-top: 0; margin-bottom: 20px; color: var(--accent-purple);">Backend Engine</h3>
          <ul style="list-style: none; padding: 0; margin: 0; color: var(--text-soft); line-height: 2;">
            <li><strong style="color: var(--text-main);">FastAPI 0.95+</strong> - Async REST API</li>
            <li><strong style="color: var(--text-main);">Python 3.10+</strong> - Core Logic</li>
            <li><strong style="color: var(--text-main);">Uvicorn</strong> - ASGI Server (Port Bound)</li>
            <li><strong style="color: var(--text-main);">OpenCV &amp; Pillow</strong> - Image Processing</li>
          </ul>
        </div>

        <div class="glass card tech-card" style="padding: 30px;">
          <h3 style="margin-top: 0; margin-bottom: 20px; color: var(--accent-cyan);">AI &amp; Machine Learning</h3>
          <ul style="list-style: none; padding: 0; margin: 0; color: var(--text-soft); line-height: 2;">
            <li><strong style="color: var(--text-main);">PyTorch 2.0+ (CPU)</strong> - Deep Learning</li>
            <li><strong style="color: var(--text-main);">MobileNetV3</strong> - Memory-efficient Inference</li>
            <li><strong style="color: var(--text-main);">ResNet50</strong> - Confusion Visualisation</li>
            <li><strong style="color: var(--text-main);">FGSM</strong> - Fast Gradient Sign Method</li>
          </ul>
        </div>
        
      </div>
    </section>
"""

new_html = new_html.replace('<!-- FOOTER -->', tech_stack_html + '\n  <!-- FOOTER -->')

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

