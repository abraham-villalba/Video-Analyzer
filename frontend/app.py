from utils.api import upload_video, analyze_video
import streamlit as st
import time
from dotenv import load_dotenv
import os

load_dotenv()


UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "")

# Page configuration
st.set_page_config(
    page_title="Video Analyzer",
    page_icon="🎥",
    layout="wide",
)

st.title("Video Analyzer")

st.caption("Tool that analyzes video content by generating a transcript, " \
    "summarizing it, and describing key scenes using an LLM.")

# Initalize state
state_defaults = {
    "video_id": None,
    "waiting": False,
    "analysis_result": None,
    "last_uploaded_video_name": None,
    "last_language": None,
    "last_summary_type": None,
    "error_message": None
}

for key, value in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- FORM SECTION ---
st.markdown("### Upload video for analysis")
col1, col2 = st.columns([0.6, 0.4])
with col1:
    video_file = st.file_uploader("Choose a video file", type=['mp4', 'mov'])
with col2:
    language = st.selectbox("Language", ["en", "es", "fr", "de", "infer"], index=0)
    summary_type = st.selectbox("Summary Type", ["Concise", "Detailed"])

analyze_clicked = st.button("Analyze video", disabled=st.session_state.waiting)

# If button was clicked and not waiting
if analyze_clicked and not st.session_state.waiting:
    if not video_file:
        st.error("You must submit a video")
    elif (
        st.session_state.analysis_result and
        st.session_state.last_uploaded_video_name == video_file.name and
        st.session_state.last_language == language and
        st.session_state.last_summary_type == summary_type
    ):
        st.info("Please change your input fields before submitting again.")
    else:
        st.session_state.waiting = True
        st.session_state.analysis_result = None
        st.session_state.error_message = None
        st.rerun()  # Ensure rerun so the button shows disabled on next render

if st.session_state.error_message:
    st.error(st.session_state.error_message)


# --- LOADING SECTION ---
# After rerun, if waiting is True, start the processing
if st.session_state.waiting and not st.session_state.analysis_result:
    try:
        with st.status("Uploading video...", state="running", expanded=True) as s:
            # Only upload video if its a new file
            if st.session_state.last_uploaded_video_name != video_file.name:
                st.toast('Uploading video...')
                s.update(label="Uploading video...", state="running")
                st.session_state.video_id = upload_video(video_file)
            if st.session_state.video_id == None:
                raise Exception("Error while uploading video, try again later...")
            
            st.toast('Your video was uploaded successfully!', icon='✅')
            st.toast('Analyzing video...')
            s.update(label="Analyzing video...", state="running")
            results = analyze_video(st.session_state.video_id, language, summary_type)
            st.session_state.analysis_result = {
                "topics": results.get('topics', []),
                "transcript_summary": results.get('transcript_summary', 'No summary was generated.'),
                "holistic_summary": results.get('holistic_summary', 'No summary was generated.'),
                "transcript": results.get('transcript', 'No transcript was generated'),
                "keyframes": results.get('keyframes', [])
            }

            s.update(label="Analysis completed!", state="complete")
            st.toast('Analysis completed!', icon='✅')
            time.sleep(1.5)
            
    except Exception as e:
        st.session_state.error_message = f"Error during processing: {e}"
    finally:
        st.session_state.last_uploaded_video_name = video_file.name
        st.session_state.last_language = language
        st.session_state.last_summary_type = summary_type
        st.session_state.waiting = False
        st.rerun()  # Final rerun to re-enable the button and display results

# Results section
if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    st.markdown("---")
    st.markdown("## Video Analysis Results")

    if len(result['topics']) != 0:
        st.markdown("#### Topics")
        st.pills("Topics", result["topics"],label_visibility="collapsed")

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("#### Holistic Summary")
        with st.expander("Holistic Summary", expanded=True):
            st.write(result["holistic_summary"])

        st.markdown("#### Transcript Summary")
        with st.expander("Transcript Summary", expanded=True):
            st.write(result["transcript_summary"])

        st.markdown("#### Transcript")
        with st.expander("Transcript", expanded=True):
            st.write(result["transcript"])

    with right_col:
        st.markdown("#### Keyframes and Descriptions")
        for i, frame in enumerate(result["keyframes"]):
            img_path = os.path.abspath(os.path.join(os.getcwd(), UPLOAD_DIR, frame['image_path']))
            if os.path.exists(img_path):
                st.image(f"{img_path}", caption=f"Frame {i + 1}")
            st.write(frame["description"])
        