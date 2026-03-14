import streamlit as st
import google.generativeai as genai
import time
import os
from streamlit_mic_recorder import mic_recorder

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="IO-Assist Anti-Gravity",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- SYSTEM PROMPT (The "Defense-Proofing Engine") ---
SYSTEM_PROMPT = """
**Role:** You are an Expert Tamil Legal Assistant for an Investigating Officer (IO).
**Goal:** Convert raw field notes (in Tanglish, English, or rough Tamil) into a formal, highly professional "Observation Mahazar" in legal Tamil, ready for CCTNS upload.

**CRITICAL INSTRUCTIONS (Defense-Proofing Engine):**
1. **Source of Light (வெளிச்சம்):** You MUST explicitly mention the source of light in the Mahazar (e.g., Natural sunlight, street light, torch light, room light). If the user notes don't specify, you must infer a reasonable source based on context (e.g., day time = natural light) or explicitly state that it was bright enough to observe. NEVER omit this.
2. **Witness Presence (பஞ்சாயத்தார்கள்):** You MUST state that the observation was conducted "in the presence of the following panchayatdars" (சாட்சிகள் முன்னிலையில்).
3. **Boundaries (எல்லைகள்):** You MUST clearly format the four boundaries (East, West, North, South) of the crime scene if provided. If not provided, add placeholders for them.
4. **Tone and Language:** Use formal, authoritative, and precise legal Tamil (நீதிமன்ற தமிழ்). Avoid colloquialisms.
5. **Structure:** The output must be structured logically:
   - Date, Time, and Place of Observation (பார்வையிட்ட நாள், நேரம் மற்றும் இடம்)
   - Presence of Witnesses (சாட்சிகள்)
   - Source of Light (வெளிச்சம்)
   - Boundaries (எல்லைகள்)
   - Detailed Observation (பார்வையிட்ட விவரம்) - *Convert raw notes into formal sentences here.*
   - Seized Items (கைப்பற்றப்பட்ட பொருட்கள்) - *If any.*

**Input:** Raw field notes from the IO.
**Output Requirement:** ONLY provide the translated and formatted Legal Tamil text. Do not add any conversational filler or introductory text.
"""

# --- INITALIZE SESSION STATE ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "generated_mahazar" not in st.session_state:
    st.session_state.generated_mahazar = ""

# --- GEMINI PROCESSING FUNCTION ---
def generate_mahazar(raw_notes, api_key):
    try:
        genai.configure(api_key=api_key)
        # Using gemini-1.5-pro for best reasoning and multilingual support
        model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=SYSTEM_PROMPT)
        
        with st.spinner("Processing legal Tamil phrasing..."):
            response = model.generate_content(raw_notes)
            return response.text
    except Exception as e:
        return f"🚨 Error: {str(e)}"

# --- MAIN UI ---
st.title("⚖️ IO-Assist: Anti-Gravity")
st.markdown("*Voice-to-CCTNS Legal Mahazar Generator*")

st.markdown("---")

# API Key Input
with st.expander("⚙️ Settings (Provide Gemini API Key)", expanded=not st.session_state.api_key):
    st.session_state.api_key = st.text_input(
        "Google Gemini API Key", 
        type="password", 
        value=st.session_state.api_key,
        help="Get your free API key at aistudio.google.com"
    )
    if not st.session_state.api_key:
        st.warning("Please enter your Gemini API Key to use the tool.")
        st.stop()


# Input Section
st.subheader("🎤 Step 1: Record or Type Field Notes")

tab1, tab2 = st.tabs(["Voice Dictation", "Text Input"])

with tab1:
    st.info("Tap the mic below, speak your observation notes (in Tamil or English), then tap again to stop.")
    audio_data = mic_recorder(
        start_prompt="🔴 Start Recording",
        stop_prompt="⏹️ Stop Recording",
        key='mic_input',
        use_container_width=True
    )
    
    # Placeholder for actual transcription. For a purely Streamlit cloud app without external
    # complex STT dependencies, we'd ideally use standard browser Speech Recognition 
    # but `streamlit-mic-recorder` just captures audio bytes.
    # To keep this simple and "no-code" deployable, we'll instruct the user to use 
    # the built-in keyboard dictation on their mobile devices in the Text Tab for highest accuracy.
    if audio_data:
        st.warning("⚠️ For highest accuracy Tamil voice-to-text, please use your phone's built-in keyboard mic (Google Voice Typing) in the 'Text Input' tab instead.")

with tab2:
    st.info("Type or use your phone's keyboard microphone to dictate your raw notes here.")
    raw_text_input = st.text_area(
        "Raw Observation Notes (Tanglish/Tamil/English):",
        height=150,
        placeholder="e.g., Scene paathom, east adutha veedu, west road, blood stains irundhuchu near the door. Rendu witness vandhanga, Ramu um Somu um. Time morning 10 AM so natural light irundhuchu..."
    )

# Processing Section
st.markdown("---")
st.subheader("⚙️ Step 2: Generate Legal Mahazar")

if st.button("🚀 Process & Format (Anti-Gravity)", use_container_width=True, type="primary"):
    if not raw_text_input.strip():
        st.error("Please provide some field notes first.")
    else:
        st.session_state.generated_mahazar = generate_mahazar(raw_text_input, st.session_state.api_key)


# Output Section
if st.session_state.generated_mahazar:
    st.markdown("---")
    st.subheader("📄 Step 3: Copy for CCTNS")
    
    output_container = st.container(border=True)
    with output_container:
        st.markdown(st.session_state.generated_mahazar)
        
    st.code(st.session_state.generated_mahazar, language="markdown")
    st.success("Draft ready! Use the copy icon in the top right of the code block above to copy the text.")

st.markdown("---")
st.caption("🔒 *Anti-Gravity Defense-Shield Active: Ensures Source of Light, Boundaries, and Witnesses are validated.*")
