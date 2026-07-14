import streamlit as st
import streamlit.components.v1 as components
import librosa
import librosa.display
import matplotlib.pyplot as plt
from transformers import pipeline
import numpy as np

# 1. Base Streamlit configuration
st.set_page_config(page_title="PHONIC-SENTRY // Neural Acoustic Forensics", page_icon="⚡", layout="centered")

# 2. INJECT ACTIVE FLOATING HTML5 CANVAS ANIMATION (Bypasses Streamlit Sandbox)
components.html("""
    <div id="matrix-wrapper" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -999; overflow: hidden; pointer-events: none;">
        <canvas id="matrix-canvas" style="width: 100%; height: 100%; display: block;"></canvas>
    </div>
    
    <script>
    // Break out of iframe constraints to attach canvas to main document body if possible
    const wrapper = document.getElementById('matrix-wrapper');
    window.parent.document.body.appendChild(wrapper);

    const canvas = window.parent.document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');

    function resize() {
        canvas.width = window.parent.innerWidth;
        canvas.height = window.parent.innerHeight;
    }
    resize();
    window.parent.addEventListener('resize', resize);

    // Core acoustic forensic falling elements
    const acousticSymbols = [
        '∿', 'dB', 'Hz', 'kHz', 'FFT', 'STFT', 'VOX', 'PCM', '10', '01', 
        'ə', 'æ', 'ʃ', 'dʒ', 'ʌ', '█', '░', '▒', 'WAV', 'MP3'
    ];

    const fontSize = 14;
    const columns = Math.floor(canvas.width / fontSize);
    const rainDrops = Array(columns).fill(1).map(() => Math.floor(Math.random() * -100)); // Stagger starts

    function draw() {
        ctx.fillStyle = 'rgba(12, 13, 19, 0.16)'; // Fades trailing symbols to simulate fall
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#39FF14'; // Bright Neon Green
        ctx.font = "bold " + fontSize + "px monospace";

        for (let i = 0; i < rainDrops.length; i++) {
            const text = acousticSymbols[Math.floor(Math.random() * acousticSymbols.length)];
            const x = i * fontSize;
            const y = rainDrops[i] * fontSize;

            // Only draw if within visible screen bounds
            if (y > 0) {
                ctx.fillText(text, x, y);
            }

            // Reset drop back to top randomly after leaving viewport
            if (y > canvas.height && Math.random() > 0.975) {
                rainDrops[i] = 0;
            }
            rainDrops[i]++;
        }
    }

    // Lock animation frame cycle at ~40ms intervals
    setInterval(draw, 40);
    </script>
""", height=0)

# 3. Custom Cyber-Forensic Style Injection
st.markdown("""
    <style>
    /* Dark Cyberpunk Terminal Colors & Glow */
    .stApp {
        background-color: transparent !important; /* Let the underlying matrix canvas show through */
        color: #39FF14 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Give main components a subtle background so text remains perfectly legible */
    .block-container {
        background-color: rgba(12, 13, 19, 0.7);
        padding: 30px !important;
        border-radius: 8px;
        box-shadow: 0 0 40px rgba(12, 13, 19, 0.9);
        margin-top: 20px;
    }

    h1, h2, h3, p, span, label {
        color: #39FF14 !important;
        text-shadow: 0 0 8px rgba(57, 255, 20, 0.5);
    }

    /* Style the file uploader */
    div[data-testid="stFileUploader"] {
        border: 2px dashed #39FF14 !important;
        background-color: rgba(8, 9, 13, 0.8) !important;
        border-radius: 4px;
        padding: 15px;
        box-shadow: 0 0 15px rgba(57, 255, 20, 0.05);
    }

    /* Terminal logs styling */
    .terminal-box {
        background-color: rgba(5, 5, 8, 0.9);
        border: 1px solid #39FF14;
        padding: 15px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        margin-bottom: 25px;
        box-shadow: inset 0 0 12px rgba(57, 255, 20, 0.15);
    }

    /* Oscillating neon scanning bar */
    @keyframes scan {
        0% { transform: translateY(-100%); }
        50% { transform: translateY(100%); }
        100% { transform: translateY(-100%); }
    }
    .scanner-line {
        height: 4px;
        background: #39FF14;
        box-shadow: 0 0 15px #39FF14;
        animation: scan 3s infinite linear;
    }
    </style>
    """, unsafe_allow_html=True)

# App Title Header
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="font-size: 2.3rem; letter-spacing: 3px; font-weight: bold;">⚡ PHONIC-SENTRY // NEURAL ACOUSTIC FORENSICS v2.4 ⚡</h1>
    <p style="color: #888 !important; font-size: 0.95rem; letter-spacing: 1px;">COVERT AI CLONE DETECTION & SPECTRAL SPECTROSCOPY LAB</p>
</div>
""", unsafe_allow_html=True)

# 4. Lazy-Load Free Hugging Face AI Model
@st.cache_resource
def load_detector():
    return pipeline("audio-classification", model="MelodyMachine/Deepfake-audio-detection-V2")

classifier = load_detector()

# Live System Terminal Console
st.markdown("""
<div class="terminal-box">
    &gt;&gt; STACK: PYTHON 3.13 // PYTORCH Core // LIBROSA Engine <br>
    &gt;&gt; DETECTOR: WAV2VEC2-CONV-TRANSFORMER LOADED <br>
    &gt;&gt; SPECTRO-MATRIX: READY [WAV, MP3, OGG, FLAC, M4A, AAC]
</div>
""", unsafe_allow_html=True)

# 5. Secure File Upload Ingestor
uploaded_file = st.file_uploader("📂 INGEST AUDIO RECORDING SIGNAL SPECIMEN", type=["wav", "mp3", "ogg", "flac", "m4a", "aac"])

if uploaded_file is not None:
    # Diagnostic Scanning Bar Line
    st.markdown("""
    <div style="border: 1px solid #39FF14; height: 8px; overflow: hidden; margin-bottom: 20px; position: relative;">
        <div class="scanner-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🔊 Audio Signal Monitor")
    st.audio(uploaded_file)
    
    with st.spinner("⚡ DECRYPTING & PARSING WAV SIGNAL MATRIX..."):
        try:
            # Multi-format conversion using Librosa
            y, sr = librosa.load(uploaded_file, sr=16000)
            
            # 20-Second Cap to keep the app lightning fast
            duration = len(y) / sr
            if duration > 20:
                st.warning(f"⚠️ Clip duration exceeds 20s ({duration:.1f}s). Processing first 20s limit.")
                y = y[:16000 * 20]
            
            # Classify audio with the AI Model
            results = classifier(y)
            
            fake_score = next((item['score'] for item in results if item['label'].lower() == 'fake'), 0.0)
            real_score = next((item['score'] for item in results if item['label'].lower() == 'real'), 0.0)
            
            # Forensic Verdict Output Cards
            st.markdown("### 🖥️ Forensics Analysis Log")
            if fake_score > real_score:
                st.markdown(f"""
                <div style="border: 2px solid #FF3131; background-color: rgba(36, 0, 0, 0.9); padding: 20px; border-radius: 4px; box-shadow: 0 0 15px #FF3131;">
                    <h2 style="color: #FF3131 !important; margin: 0; text-shadow: 0 0 8px #FF3131;">🚨 WARNING: CLONE SIGNATURE MATCH</h2>
                    <p style="color: #FF3131 !important; margin: 5px 0 0 0; font-size: 1.15rem; font-family: monospace;">
                        SYNTHETIC COGNITIVE CLONE PROBABILITY: {fake_score*100:.2f}%
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="border: 2px solid #39FF14; background-color: rgba(0, 31, 0, 0.9); padding: 20px; border-radius: 4px; box-shadow: 0 0 15px #39FF14;">
                    <h2 style="color: #39FF14 !important; margin: 0; text-shadow: 0 0 8px #39FF14;">🍏 VERDICT: NATURAL SIGNATURE CONFIRMED</h2>
                    <p style="color: #39FF14 !important; margin: 5px 0 0 0; font-size: 1.15rem; font-family: monospace;">
                        HUMAN AUTHENTICITY CONFIDENCE: {real_score*100:.2f}%
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as model_err:
            st.error(f"SYSTEM ALARM // Decryption Failure: {model_err}")

        # Spectrogram Panel
        st.subheader("📈 Signal Spectrogram Matrix")
        try:
            # Generate short-time Fourier transform (STFT)
            X = librosa.stft(y)
            Xdb = librosa.amplitude_to_db(abs(X))
            
            # Plot the spectrogram
            fig, ax = plt.subplots(figsize=(10, 4.5))
            fig.patch.set_facecolor('#0c0d13')
            ax.set_facecolor('#0c0d13')
            
            img = librosa.display.specshow(Xdb, sr=sr, x_axis='time', y_axis='linear', ax=ax, cmap='viridis')
            
            # Match the axes with neon terminal theme
            ax.tick_params(colors='#39FF14')
            ax.xaxis.label.set_color('#39FF14')
            ax.yaxis.label.set_color('#39FF14')
            ax.title.set_color('#39FF14')
            
            for spine in ax.spines.values():
                spine.set_edgecolor('#39FF14')
                
            ax.set_title("SPECTRAL FREQUENCIES OVER TIME", fontsize=10, fontweight='bold', color='#39FF14')
            st.pyplot(fig)
            
        except Exception as graph_err:
            st.error(f"SYSTEM ALARM // Visualizer Defect: {graph_err}")
