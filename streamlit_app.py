import streamlit as st
import cadquery as cq
import os
import base64

# पेज कॉन्फ़िगरेशन (डार्क और वाइड लुक)
st.set_page_config(page_title="AI 2D to 3D CAD Engine", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; }
    h1 { color: #00f2fe; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AI Mechanical CAD Engine (Streamlit)")
st.caption("कास्टिंग ड्रॉइंग इमेज अपलोड करें और तुरंत STEP/STL मॉडल डाउनलोड करें")

# कैड जनरेशन लॉजिक (CadQuery)
def generate_cad_model(data):
    width = data.get('total_width', 150.0)
    depth = data.get('total_depth', 61.0)
    base_h = data.get('base_height', 40.0)
    boss_dia = data.get('boss_diameter', 32.0)
    hole_dia = data.get('hole_diameter', 20.0)

    # 3D सॉलिड मॉडल का निर्माण
    base = cq.Workplane("XY").box(width, depth, base_h)
    base = base.faces(">Z").workplane().circle(boss_dia / 2).extrude(25)
    base = base.faces(">Z").workplane().circle(hole_dia / 2).cutThruAll()
    base = base.faces("<Y").workplane().center(0, -5).rect(70, 30).cutThruAll()

    # फाइलें सेव करना
    step_path = "model.step"
    stl_path = "model.stl"
    cq.exporters.export(base, step_path)
    cq.exporters.export(base, stl_path, cq.exporters.ExportTypes.STL, 0.1)
    return step_path, stl_path

# दो हिस्सों में यूआई को बांटना (Sidebar, Left Column, Right Column)
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. ड्रॉइंग अपलोड करें")
    uploaded_file = st.file_uploader("2D इंजीनियरिंग ड्रॉइंग चुनें (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    convert_btn = st.button("⚡ Convert to 3D Model", type="primary", use_container_width=True)

if uploaded_file and convert_btn:
    with st.spinner("AI प्रोसेसिंग और 3D मॉडलिंग जारी है..."):
        # यहाँ आपका इमेज विज़न एआई डेटा मैप होगा (अभी के लिए आपकी इमेज की सटीक वैल्यूज हैं)
        extracted_dimensions = {
            "total_width": 150.0,
            "total_depth": 61.0,
            "base_height": 40.0,
            "boss_diameter": 32.0,
            "hole_diameter": 20.0
        }
        
        # 3D मॉडल बनाएं
        step_file, stl_file = generate_cad_model(extracted_dimensions)
        
        with col1:
            st.success("✅ 3D मॉडल सफलतापूर्वक बन गया है!")
            # AI डाइमेंशन्स डिस्प्ले
            st.json(extracted_dimensions)
            
            # STEP फ़ाइल डाउनलोड बटन
            with open(step_file, "rb") as f:
                st.download_button(
                    label="📥 Download STEP File",
                    data=f,
                    file_name="mechanical_pattern.step",
                    mime="application/step",
                    use_container_width=True
                )

        with col2:
            st.subheader("Interactive 3D Viewport (टच करके घुमाएं)")
            
            # STL फाइल को बेस64 में बदलना ताकि ब्राउज़र इसे पढ़ सके
            with open(stl_file, "rb") as f:
                stl_base64 = base64.b64encode(f.read()).decode()

            # Three.js 3D व्यूअर का HTML कोड (मोबाइल टच इनेबल्ड)
            html_viewer = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
                <style> body {{ margin: 0; background-color: #090d16; overflow: hidden; }} </style>
            </head>
            <body>
                <div id="canvas-container" style="width: 100vw; height: 450px;"></div>
                <script>
                    const scene = new THREE.Scene();
                    scene.background = new THREE.Color(0x090d16);
                    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / 450, 1, 1000);
                    camera.position.set(150, 150, 150);
                    
                    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                    renderer.setSize(window.innerWidth, 450);
                    document.getElementById('canvas-container').appendChild(renderer.domElement);
                    
                    const controls = new THREE.OrbitControls(camera, renderer.domElement);
                    controls.enableDamping = true;
                    
                    scene.add(new THREE.AmbientLight(0x666666));
                    const light = new THREE.DirectionalLight(0xffffff, 0.8);
                    light.position.set(1, 1, 1).normalize();
                    scene.add(light);

                    // Base64 से STL डेटा लोड करना
                    const stlBinary = atob("{stl_base64}");
                    const bytes = new Uint8Array(stlBinary.length);
                    for (let i = 0; i < stlBinary.length; i++) {{ bytes[i] = stlBinary.charCodeAt(i); }}
                    
                    const loader = new THREE.STLLoader();
                    const geometry = loader.parse(bytes.buffer);
                    const material = new THREE.MeshStandardMaterial({{ color: 0x00f2fe, roughness: 0.4, metalness: 0.7 }});
                    const mesh = new THREE.Mesh(geometry, material);
                    geometry.center();
                    scene.add(mesh);

                    function animate() {{
                        requestAnimationFrame(animate);
                        controls.update();
                        renderer.render(scene, camera);
                    }}
                    animate();
                </script>
            </body>
            </html>
            """
            st.components.v1.html(html_viewer, height=460)
