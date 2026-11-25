document.addEventListener('DOMContentLoaded', function() {
    // Variables
    let selectedColor = '#FFFFFF';
    let selectedPart = 'all';
    let imageSize = 80; // percentage
    let imagePosition = { x: 50, y: 50 }; // percentage
    let uploadedImage = null;
    let scene, camera, renderer, controls, tshirtModel;
    let imageElement = null;
  
    // Color mapping
    const COLORS = {
      'custom-color': '#FFFFFF',
      'white-color': '#FFFFFF',
      'purple-color': '#A855F7',
      'gray-color': '#9CA3AF',
      'black-color': '#1F2937',
      'blue-color': '#2563EB',
      'beige-color': '#F5F5DC'
    };
  
    // DOM Elements
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.querySelector('.upload-btn');
    const tabTriggers = document.querySelectorAll('.tab-trigger');
    const designItems = document.querySelectorAll('.design-item');
    const colorBtns = document.querySelectorAll('.color-btn');
    const partBtns = document.querySelectorAll('.part-btn');
    const imageControls = document.getElementById('image-controls');
    const smallerBtn = document.getElementById('smaller-btn');
    const largerBtn = document.getElementById('larger-btn');
    const frontImageContainer = document.getElementById('front-image-container');
  
    // Initialize Three.js
    initThreeJS();
  
    // Event Listeners
    uploadBtn.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', handleFileUpload);
    
    tabTriggers.forEach(trigger => {
      trigger.addEventListener('click', () => {
        const tabId = trigger.getAttribute('data-tab');
        
        // Update active tab trigger
        tabTriggers.forEach(t => t.classList.remove('active'));
        trigger.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
          content.classList.remove('active');
        });
        document.getElementById(`${tabId}-content`).classList.add('active');
      });
    });
    
    designItems.forEach(item => {
      item.addEventListener('click', () => {
        const part = item.getAttribute('data-part');
        selectPart(part);
      });
    });
    
    colorBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        colorBtns.forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        
        // Get color from button class
        for (const [className, colorValue] of Object.entries(COLORS)) {
          if (btn.classList.contains(className)) {
            selectedColor = colorValue;
            updateColors();
            break;
          }
        }
      });
    });
    
    partBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const part = btn.getAttribute('data-part');
        selectPart(part);
      });
    });
    
    smallerBtn.addEventListener('click', () => {
      imageSize = Math.max(10, imageSize - 5);
      updateImageSize();
    });
    
    largerBtn.addEventListener('click', () => {
      imageSize = Math.min(100, imageSize + 5);
      updateImageSize();
    });
  
    // Functions
    function handleFileUpload(e) {
      const file = e.target.files[0];
      if (file && file.type.includes('image')) {
        const reader = new FileReader();
        reader.onload = (event) => {
          // Create image element
          uploadedImage = event.target.result;
          
          // Show image controls
          imageControls.style.display = 'block';
          
          // Add image to front view
          addImageToFront();
          
          // Add texture to 3D model
          updateTexture();
          
          // Select front part
          selectPart('front');
        };
        reader.readAsDataURL(file);
      }
    }
    
    function addImageToFront() {
      // Clear previous image
      frontImageContainer.innerHTML = '';
      
      // Create new image container
      imageElement = document.createElement('div');
      imageElement.className = 'uploaded-image';
      imageElement.style.top = `${imagePosition.y}%`;
      imageElement.style.left = `${imagePosition.x}%`;
      imageElement.style.width = `${imageSize}%`;
      imageElement.style.height = `${imageSize}%`;
      
      // Create image
      const img = document.createElement('img');
      img.src = uploadedImage;
      img.alt = 'Uploaded design';
      img.draggable = false;
      
      // Add image to container
      imageElement.appendChild(img);
      frontImageContainer.appendChild(imageElement);
      
      // Add drag functionality
      makeImageDraggable(imageElement);
    }
    
    function makeImageDraggable(element) {
      element.addEventListener('mousedown', startDrag);
      
      function startDrag(e) {
        e.preventDefault();
        
        const parentElement = element.parentElement;
        if (!parentElement) return;
        
        const rect = parentElement.getBoundingClientRect();
        
        function onDrag(moveEvent) {
          const x = Math.min(100, Math.max(0, ((moveEvent.clientX - rect.left) / rect.width) * 100));
          const y = Math.min(100, Math.max(0, ((moveEvent.clientY - rect.top) / rect.height) * 100));
          
          imagePosition = { x, y };
          element.style.left = `${x}%`;
          element.style.top = `${y}%`;
        }
        
        function stopDrag() {
          document.removeEventListener('mousemove', onDrag);
          document.removeEventListener('mouseup', stopDrag);
        }
        
        document.addEventListener('mousemove', onDrag);
        document.addEventListener('mouseup', stopDrag);
      }
    }
    
    function updateImageSize() {
      if (imageElement) {
        imageElement.style.width = `${imageSize}%`;
        imageElement.style.height = `${imageSize}%`;
      }
    }
    
    function selectPart(part) {
      selectedPart = part;
      
      // Update UI
      partBtns.forEach(btn => {
        if (btn.getAttribute('data-part') === part) {
          btn.classList.add('selected');
        } else {
          btn.classList.remove('selected');
        }
      });
      
      designItems.forEach(item => {
        if (item.getAttribute('data-part') === part) {
          item.classList.add('selected');
        } else {
          item.classList.remove('selected');
        }
      });
      
      // Update colors
      updateColors();
    }
    
    function updateColors() {
      // Update 2D t-shirt colors
      designItems.forEach(item => {
        const part = item.getAttribute('data-part');
        const path = item.querySelector('.t-shirt-path');
        
        if (selectedPart === 'all' || selectedPart === part) {
          path.style.fill = selectedColor;
        }
      });
      
      // Update 3D model colors
      if (tshirtModel) {
        tshirtModel.traverse(child => {
          if (child.isMesh) {
            child.material.color.set(selectedColor);
            child.material.needsUpdate = true;
          }
        });
      }
    }
    
    function updateTexture() {
      if (!uploadedImage) return;
      
      // Create texture for 3D model
      const textureLoader = new THREE.TextureLoader();
      const texture = textureLoader.load(uploadedImage);
      
      if (tshirtModel) {
        tshirtModel.traverse(child => {
          if (child.isMesh && (selectedPart === 'all' || selectedPart === 'front')) {
            // Clone material to avoid affecting other parts
            const newMaterial = new THREE.MeshStandardMaterial({
              map: texture,
              color: selectedColor
            });
            child.material = newMaterial;
            child.material.needsUpdate = true;
          }
        });
      }
    }
    
    function initThreeJS() {
      // Get canvas
      const canvas = document.getElementById('three-canvas');
      
      // Create scene
      scene = new THREE.Scene();
      
      // Create camera
      camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
      camera.position.z = 5;
      
      // Create renderer
      renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
      renderer.setSize(canvas.clientWidth, canvas.clientHeight);
      renderer.setClearColor(0xE5E7EB);
      
      // Add lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
      scene.add(ambientLight);
      
      const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
      directionalLight.position.set(5, 5, 5);
      scene.add(directionalLight);
      
      // Add controls
      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      
      // Load t-shirt model
      const loader = new THREE.GLTFLoader();
      loader.load('/assets/3d/duck.glb', (gltf) => {
        tshirtModel = gltf.scene;
        tshirtModel.scale.set(2, 2, 2);
        tshirtModel.position.set(0, -1, 0);
        scene.add(tshirtModel);
        
        // Apply initial color
        updateColors();
      });
      
      // Handle window resize
      window.addEventListener('resize', () => {
        camera.aspect = canvas.clientWidth / canvas.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(canvas.clientWidth, canvas.clientHeight);
      });
      
      // Animation loop
      function animate() {
        requestAnimationFrame(animate);
        
        // Rotate model
        if (tshirtModel) {
          tshirtModel.rotation.y += 0.002;
        }
        
        controls.update();
        renderer.render(scene, camera);
      }
      
      animate();
    }
  });
  
  import * as THREE from 'three';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
  import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';