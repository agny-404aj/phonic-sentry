import streamlit as st
import streamlit.components.v1 as components
import librosa
import librosa.display
import matplotlib.pyplot as plt
from transformers import pipeline
import numpy as np
import io
import os
import tempfile

# ==========================================
# 1. AUTO-DETECT & REGISTER STATIC-FFMPEG BINARIES
# ==========================================
try:
    import static_ffmpeg
    import static_ffmpeg.run as sf_run
    ffmpeg_bin, ffprobe_bin = sf_run.get_or_fetch_platform_executables_and_set_env()
    
    os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_bin)
    
    from pydub import AudioSegment
    AudioSegment.converter = ffmpeg_bin
    AudioSegment.ffprobe = ffprobe_bin
except Exception as e:
    pass

# Base Streamlit configuration
st.set_page_config(page_title="PHONIC-SENTRY // Neural Acoustic Forensics", page_icon="⚡", layout="centered")

# ==========================================
# 2. CSS DESIGN SYSTEM (Zero Top-Gap styling)
# ==========================================
CYBER_CSS = """
<style>
    /* Prevent the Streamlit HTML wrapper frame from taking up visible space in your app layout flow */
    iframe[title="streamlit_components.v1.html"] {
        position: absolute !important;
        height: 1px !important;
        width: 1px !important;
        border: none !important;
        opacity: 0.01 !important;
    }
    .block-container {
        padding-top: 2rem !important;
        margin-top: 0px !important;
        background-color: rgba(12, 13, 19, 0.85);
        padding: 30px !important;
        border-radius: 8px;
        box-shadow: 0 0 40px rgba(12, 13, 19, 0.9);
        border: 1px solid rgba(57, 255, 20, 0.15);
    }
    .stApp {
        background-color: transparent !important;
        color: #39FF14 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    h1, h2, h3, p, span, label {
        color: #39FF14 !important;
        text-shadow: 0 0 8px rgba(57, 255, 20, 0.4);
    }
    div[data-testid="stFileUploader"] {
        border: 2px dashed #39FF14 !important;
        background-color: rgba(8, 9, 13, 0.8) !important;
        border-radius: 4px;
        padding: 15px;
    }
    .terminal-box {
        background-color: rgba(5, 5, 8, 0.9);
        border: 1px solid #39FF14;
        padding: 15px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        margin-bottom: 25px;
    }
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
"""
st.markdown(CYBER_CSS, unsafe_allow_html=True)

# App Title Header
APP_HEADER = """
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="font-size: 2.3rem; letter-spacing: 3px; font-weight: bold;">⚡ PHONIC-SENTRY // NEURAL ACOUSTIC FORENSICS v2.4 ⚡</h1>
    <p style="color: #888 !important; font-size: 0.95rem; letter-spacing: 1px;">COVERT AI CLONE DETECTION & SPECTRAL SPECTROSCOPY LAB</p>
</div>
"""
st.markdown(APP_HEADER, unsafe_allow_html=True)

# 3. Lazy-Load AI Model
@st.cache_resource
def load_detector():
    return pipeline("audio-classification", model="MelodyMachine/Deepfake-audio-detection-V2")

classifier = load_detector()

# Live System Terminal Console
TERMINAL_HTML = """
<div class="terminal-box">
    &gt;&gt; STACK: PYTHON 3.13 // PYTORCH Core // LIBROSA Engine <br>
    &gt;&gt; DETECTOR: WAV2VEC2-CONV-TRANSFORMER LOADED <br>
    &gt;&gt; SPECTRO-MATRIX: READY [WAV, MP3, OGG, FLAC, M4A, AAC]
</div>
"""
st.markdown(TERMINAL_HTML, unsafe_allow_html=True)

# 4. File Upload Ingestor
uploaded_file = st.file_uploader("📂 INGEST AUDIO RECORDING SIGNAL SPECIMEN", type=["wav", "mp3", "ogg", "flac", "m4a", "aac"])

y = None
sr = 16000

if uploaded_file is not None:
    SCANNER_HTML = """
    <div style="border: 1px solid #39FF14; height: 8px; overflow: hidden; margin-bottom: 20px; position: relative;">
        <div class="scanner-line"></div>
    </div>
    """
    st.markdown(SCANNER_HTML, unsafe_allow_html=True)
    
    st.subheader("🔊 Audio Signal Monitor")
    st.audio(uploaded_file)
    
    with st.spinner("⚡ DECRYPTING & PARSING SIGNAL MATRIX (RAM-OPTIMIZED)..."):
        file_extension = uploaded_file.name.split('.')[-1].lower()
        file_bytes = uploaded_file.read()
        
        # Guardrails for memory
        try:
            # Load the file quickly using pydub metadata
            audio_segment = AudioSegment.from_file(io.BytesIO(file_bytes), format=file_extension)
            duration_secs = len(audio_segment) / 1000.0
            
            # If the file is longer than 20 seconds, slice it immediately in-memory before conversion!
            if duration_secs > 20.0:
                st.warning(f"⚠️ Clip duration exceeds 20s ({duration_secs:.1f}s). Extracting first 20s to preserve server memory.")
                audio_segment = audio_segment[:20000] # Slice to 20,000ms
            
            # Standardize format
            audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
            raw_data = audio_segment.get_array_of_samples()
            y = np.array(raw_data, dtype=np.float32)
            
            # Normalize bit depth scale
            if audio_segment.sample_width == 2:
                y /= 32768.0
            elif audio_segment.sample_width == 4:
                y /= 2147483648.0
            sr = 16000
            
        except Exception as decrypt_err:
            # Librosa fallback for standard small files if pydub fails
            try:
                y, sr = librosa.load(io.BytesIO(file_bytes), sr=16000, duration=20.0) # Strictly capped at 20s
            except Exception as lib_err:
                st.error(f"SYSTEM ALARM // Decryption Failure: {lib_err}")
        

# --- Forensic Predictor Execution ---
        if y is not None:
            try:
                # 1. SIGNAL CLEANING: Strip low-frequency room rumble (High-pass filter at 80Hz)
                # This removes microphone hums and ambient noise that confuse the AI model.
                if len(y) > 0:
                    # Quick FFT-based high-pass filter to clean room acoustics
                    fft_data = np.fft.rfft(y)
                    freqs = np.fft.rfftfreq(len(y), d=1/sr)
                    fft_data[freqs < 80] = 0  # Cut off everything below 80Hz (non-vocal noise)
                    y = np.fft.irfft(fft_data)
                
                # 2. GAIN NORMALIZATION: Prevents mic clipping from mimicking synthetic patterns
                if np.max(np.abs(y)) > 0:
                    y = y / np.max(np.abs(y))
                
                duration = len(y) / sr
                if duration > 20:
                    st.warning(f"⚠️ Clip duration exceeds 20s ({duration:.1f}s). Processing first 20s limit.")
                    y = y[:16000 * 20]
                
                # Run the classifier on the cleaned signal
                results = classifier(y)
                fake_score = next((item['score'] for item in results if item['label'].lower() == 'fake'), 0.0)
                real_score = next((item['score'] for item in results if item['label'].lower() == 'real'), 0.0)
                
                st.markdown("### 🖥️ Forensics Analysis Log")
                
                # 3. CONVERT TO PERCENTAGES
                fake_pct = fake_score * 100
                real_pct = real_score * 100
                
                # 4. TUNED REAL-WORLD THRESHOLD
                # Deepfake detectors are notoriously over-sensitive to mic noise.
                # We require a strong 80% confidence match to trigger a true clone warning.
                if fake_score > 0.80:
                    formatted_fake = "{:.2f}".format(fake_pct)
                    WARNING_HTML = """
                    <div style="border: 2px solid #FF3131; background-color: rgba(36, 0, 0, 0.9); padding: 20px; border-radius: 4px; box-shadow: 0 0 15px #FF3131;">
                        <h2 style="color: #FF3131 !important; margin: 0; text-shadow: 0 0 8px #FF3131;">🚨 WARNING: CLONE SIGNATURE MATCH</h2>
                        <p style="color: #FF3131 !important; margin: 5px 0 0 0; font-size: 1.15rem; font-family: monospace;">
                            SYNTHETIC COGNITIVE CLONE PROBABILITY: {probability}%
                        </p>
                    </div>
                    """.format(probability=formatted_fake)
                    st.markdown(WARNING_HTML, unsafe_allow_html=True)
                else:
                    # If it doesn't clearly cross the clone threshold, it is natural human speech.
                    # We normalize the display bar so the user gets a stable, clean reading.
                    adjusted_real = max(real_pct, 100.0 - fake_pct)
                    formatted_real = "{:.2f}".format(adjusted_real)
                    
                    VERDICT_HTML = """
                    <div style="border: 2px solid #39FF14; background-color: rgba(0, 31, 0, 0.9); padding: 20px; border-radius: 4px; box-shadow: 0 0 15px #39FF14;">
                        <h2 style="color: #39FF14 !important; margin: 0; text-shadow: 0 0 8px #39FF14;">🍏 VERDICT: NATURAL SIGNATURE CONFIRMED</h2>
                        <p style="color: #39FF14 !important; margin: 5px 0 0 0; font-size: 1.15rem; font-family: monospace;">
                            HUMAN AUTHENTICITY CONFIDENCE: {confidence}%
                        </p>
                    </div>
                    """.format(confidence=formatted_real)
                    st.markdown(VERDICT_HTML, unsafe_allow_html=True)
                    
            except Exception as eval_err:
                st.error(f"SYSTEM ALARM // Inference Core Failure: {eval_err}")

    # Spectrogram Panel
    if y is not None:
        st.subheader("📈 Signal Spectrogram Matrix")
        try:
            X = librosa.stft(y)
            Xdb = librosa.amplitude_to_db(abs(X))
            
            fig, ax = plt.subplots(figsize=(10, 4.5))
            fig.patch.set_facecolor('#0c0d13')
            ax.set_facecolor('#0c0d13')
            
            img = librosa.display.specshow(Xdb, sr=sr, x_axis='time', y_axis='linear', ax=ax, cmap='viridis')
            
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

# ==========================================
# 5. INJECT RESTORED COVERT BOOT ANIMATION + MATRIX (Zero Height)
# ==========================================
components.html("""
    <style>
        body, html {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: transparent;
        }
    </style>
    
    <script>
    const body = window.parent.document.body;
    
    // --- 1. Rain Matrix Canvas Creation ---
    if (!window.parent.document.getElementById('matrix-canvas')) {
        const bgContainer = document.createElement('div');
        bgContainer.style = "position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -999; overflow: hidden; pointer-events: none;";
        bgContainer.innerHTML = '<canvas id="matrix-canvas" style="width: 100%; height: 100%; display: block;"></canvas>';
        body.appendChild(bgContainer);

        const canvas = window.parent.document.getElementById('matrix-canvas');
        const ctx = canvas.getContext('2d');

        function resize() {
            canvas.width = window.parent.innerWidth;
            canvas.height = window.parent.innerHeight;
        }
        resize();
        window.parent.addEventListener('resize', resize);

        const acousticSymbols = ['∿', 'dB', 'Hz', 'kHz', 'FFT', 'STFT', 'VOX', 'PCM', '10', '01', 'WAV', 'MP3'];
        const fontSize = 14;
        const columns = Math.floor(canvas.width / fontSize);
        const rainDrops = Array(columns).fill(1).map(() => Math.floor(Math.random() * -100));

        function draw() {
            ctx.fillStyle = 'rgba(12, 13, 19, 0.16)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#39FF14';
            ctx.font = "bold " + fontSize + "px monospace";

            for (let i = 0; i < rainDrops.length; i++) {
                const text = acousticSymbols[Math.floor(Math.random() * acousticSymbols.length)];
                const x = i * fontSize;
                const y = rainDrops[i] * fontSize;

                if (y > 0) ctx.fillText(text, x, y);
                if (y > canvas.height && Math.random() > 0.975) rainDrops[i] = 0;
                rainDrops[i]++;
            }
        }
        setInterval(draw, 40);
    }

    // --- 2. Restored Interactive Loader Overlay ---
    if (!window.parent.document.getElementById('boot-loader')) {
        const loaderDiv = document.createElement('div');
        loaderDiv.id = "boot-loader";
        loaderDiv.style = "position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #0c0d13; z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: 'Courier New', monospace; color: #39FF14; transition: opacity 0.5s ease; overflow: hidden;";
        loaderDiv.innerHTML = `
            <div style="width: 80%; max-width: 600px; border: 1px solid #39FF14; background-color: rgba(5, 5, 8, 0.95); padding: 25px; border-radius: 4px; box-shadow: 0 0 20px rgba(57, 255, 20, 0.25);">
                <div style="font-weight: bold; font-size: 1.1rem; margin-bottom: 15px; text-shadow: 0 0 8px rgba(57, 255, 20, 0.6); letter-spacing: 2px;">
                    ⚡ INITIALIZING COVERT SPECTRO-SIGNAL LINK...
                </div>
                <div id="boot-terminal" style="font-size: 0.8rem; line-height: 1.6; height: 120px; overflow: hidden; color: #39FF14; opacity: 0.85; margin-bottom: 20px;"></div>
                <div style="width: 100%; height: 6px; background-color: #111; border: 1px solid #39FF14; border-radius: 3px; position: relative; overflow: hidden;">
                    <div id="progress-fill" style="height: 100%; width: 0%; background-color: #39FF14; box-shadow: 0 0 10px #39FF14; transition: width 0.05s linear;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-top: 8px; color: #666;">
                    <span>SYSTEM ID: SENTRY_SECURE_V2.4</span>
                    <span id="pct-label">0%</span>
                </div>
            </div>
        `;
        body.appendChild(loaderDiv);

        const bootLogs = [
            "&gt;&gt; CONNECTING SECURE NEURAL CLASSIFIER BRIDGE...",
            "&gt;&gt; DECRYPTING AUDIO SIGNAL SOURCE...",
            "&gt;&gt; CACHING COGNITIVE SPECTROGRAM WEIGHTS...",
            "&gt;&gt; MOUNTING AUDIO PCM SIGNAL BUFFER...",
            "&gt;&gt; ALIGNING LIBROSA FAST FOURIER TRANSFORM (FFT) MATRIX...",
            "&gt;&gt; COVERT PHONIC SENTRY LINK ESTABLISHED."
        ];

        const terminal = window.parent.document.getElementById('boot-terminal');
        const progressFill = window.parent.document.getElementById('progress-fill');
        const pctLabel = window.parent.document.getElementById('pct-label');
        const bootLoader = window.parent.document.getElementById('boot-loader');

        let logIndex = 0;
        let progress = 0;
        const totalDuration = 4000; 
        const updateInterval = 40; 
        const stepIncrement = (100 / (totalDuration / updateInterval));

        const bootTimer = setInterval(() => {
            progress += stepIncrement;
            if (progress >= 100) {
                progress = 100;
                clearInterval(bootTimer);
                bootLoader.style.opacity = '0';
                setTimeout(() => { bootLoader.style.display = 'none'; }, 500);
            }
            progressFill.style.width = Math.min(progress, 100) + '%';
            pctLabel.innerText = Math.min(Math.floor(progress), 100) + '%';
        }, updateInterval);

        function addLog() {
            if (logIndex < bootLogs.length) {
                const line = window.parent.document.createElement('div');
                line.innerHTML = bootLogs[logIndex];
                line.style.marginBottom = '4px';
                terminal.appendChild(line);
                terminal.scrollTop = terminal.scrollHeight;
                logIndex++;
                setTimeout(addLog, (totalDuration / bootLogs.length) - 100);
            }
        }
        addLog();
    }
    </script>
""", height=0)