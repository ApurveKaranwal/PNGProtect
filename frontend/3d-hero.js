/**
 * 3D Hero Animation for PNGProtect
 * Creates a glowing, interactive neural/shield network using Three.js
 */

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('hero-3d-canvas');
    if (!canvas || typeof THREE === 'undefined') return;

    // --- Scene Setup ---
    const scene = new THREE.Scene();
    
    // Camera
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 300;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ 
        canvas: canvas, 
        alpha: true, // Transparent background
        antialias: true 
    });
    
    const setSize = () => {
        // Find hero section to match its height if possible, otherwise use window
        const heroSection = document.getElementById('hero');
        const width = window.innerWidth;
        const height = heroSection ? heroSection.offsetHeight : window.innerHeight;
        
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
    };
    
    setSize();
    window.addEventListener('resize', setSize);

    // --- Particles & Lines (Neural Network / Shield Look) ---
    const particleCount = window.innerWidth < 768 ? 400 : 800; // Less particles on mobile
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    // Color palette matching the theme
    const colorPalette = [
        new THREE.Color(0x3b82f6), // Blue
        new THREE.Color(0xa855f7), // Purple
        new THREE.Color(0x22c55e)  // Green
    ];

    const maxDistance = 250;

    for (let i = 0; i < particleCount; i++) {
        // Spherical distribution
        const theta = Math.random() * 2 * Math.PI;
        const phi = Math.acos(Math.random() * 2 - 1);
        const radius = maxDistance * Math.cbrt(Math.random());

        positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
        positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
        positions[i * 3 + 2] = radius * Math.cos(phi);

        // Assign random color from palette
        const color = colorPalette[Math.floor(Math.random() * colorPalette.length)];
        colors[i * 3] = color.r;
        colors[i * 3 + 1] = color.g;
        colors[i * 3 + 2] = color.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Material for particles
    const particleMaterial = new THREE.PointsMaterial({
        size: 3.5,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });

    const particles = new THREE.Points(geometry, particleMaterial);
    scene.add(particles);

    // Lines connecting nearby particles
    const lineMaterial = new THREE.LineBasicMaterial({
        vertexColors: true,
        transparent: true,
        opacity: 0.15,
        blending: THREE.AdditiveBlending
    });
    
    // Instead of computing all lines dynamically every frame (too heavy),
    // we'll pre-compute a static set of lines that rotates with the sphere
    const linePositions = [];
    const lineColors = [];
    
    for (let i = 0; i < particleCount; i++) {
        for (let j = i + 1; j < particleCount; j++) {
            const dx = positions[i * 3] - positions[j * 3];
            const dy = positions[i * 3 + 1] - positions[j * 3 + 1];
            const dz = positions[i * 3 + 2] - positions[j * 3 + 2];
            const distSq = dx*dx + dy*dy + dz*dz;
            
            if (distSq < 2500) { // Only connect if close enough
                linePositions.push(
                    positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2],
                    positions[j * 3], positions[j * 3 + 1], positions[j * 3 + 2]
                );
                
                // Mix colors for the line
                lineColors.push(
                    colors[i * 3], colors[i * 3 + 1], colors[i * 3 + 2],
                    colors[j * 3], colors[j * 3 + 1], colors[j * 3 + 2]
                );
            }
        }
    }

    const lineGeometry = new THREE.BufferGeometry();
    lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
    lineGeometry.setAttribute('color', new THREE.Float32BufferAttribute(lineColors, 3));
    
    const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
    scene.add(lines);

    // Group them together to easily rotate the whole structure
    const networkGroup = new THREE.Group();
    networkGroup.add(particles);
    networkGroup.add(lines);
    scene.add(networkGroup);
    
    // Position it nicely (offset to the right on desktop, centered on mobile)
    const updateGroupPosition = () => {
        if (window.innerWidth > 1024) {
            networkGroup.position.x = 120;
            networkGroup.position.y = 0;
        } else {
            networkGroup.position.x = 0;
            networkGroup.position.y = 50;
        }
    };
    updateGroupPosition();
    window.addEventListener('resize', updateGroupPosition);

    // --- Mouse Interaction ---
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const windowHalfX = window.innerWidth / 2;
    const windowHalfY = window.innerHeight / 2;

    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX - windowHalfX) * 0.0005;
        mouseY = (event.clientY - windowHalfY) * 0.0005;
    });

    // Theme responsiveness
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class') {
                const isLight = document.body.classList.contains('light-mode');
                // Subtle adjustment based on theme
                particleMaterial.opacity = isLight ? 0.6 : 0.8;
                lineMaterial.opacity = isLight ? 0.2 : 0.15;
            }
        });
    });
    observer.observe(document.body, { attributes: true });

    // --- Animation Loop ---
    const clock = new THREE.Clock();

    const animate = () => {
        requestAnimationFrame(animate);

        const elapsedTime = clock.getElapsedTime();

        // Smoothly move towards target mouse position
        targetX = mouseX * 0.5;
        targetY = mouseY * 0.5;
        
        networkGroup.rotation.y += 0.002; // Constant slow rotation
        networkGroup.rotation.x += 0.001;
        
        // Add subtle mouse parallax
        networkGroup.rotation.y += (targetX - networkGroup.rotation.y) * 0.05;
        networkGroup.rotation.x += (targetY - networkGroup.rotation.x) * 0.05;
        
        // Gentle pulsing effect
        const scale = 1 + Math.sin(elapsedTime * 0.5) * 0.03;
        networkGroup.scale.set(scale, scale, scale);

        renderer.render(scene, camera);
    };

    animate();
});
