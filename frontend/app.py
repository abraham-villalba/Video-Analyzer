import streamlit as st
import time

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
    "last_summary_type": None
}

for key, value in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.markdown("### Upload video for analysis")
col1, col2 = st.columns([0.6, 0.4])
with col1:
    video_file = st.file_uploader("Choose a video file", type=['mp4', 'mov'])
with col2:
    language = st.selectbox("Language", ["en", "es", "fr", "de", "infer"], index=0)
    summary_type = st.selectbox("Summary Type", ["concise", "detailed"])

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
        st.rerun()  # Ensure rerun so the button shows disabled on next render

# After rerun, if waiting is True, start the processing
if st.session_state.waiting and not st.session_state.analysis_result:
    try:
        with st.status("Uploading video...", state="running", expanded=True) as s:
            files = {"file": video_file.getvalue()}
            time.sleep(5)
            s.update(label="Analyzing video...", state="running")
            time.sleep(5)
            st.session_state.analysis_result = {
                "topics": ["Sports", "Politics"],
                "summary": "This is a summary of the video.",
                "transcript": "This is a transcript.",
                "keyframes": [
                    {"image_url": f"Image {i+1}", "description": f"Description {i+1}"}
                    for i in range(20)
                ]
            }
            s.update(label="Analysis completed!", state="complete")
    except Exception as e:
        st.error(f"Error during processing: {e}")
    finally:
        st.session_state.last_uploaded_video_name = video_file.name
        st.session_state.last_language = language
        st.session_state.last_summary_type = summary_type
        st.session_state.waiting = False
        st.rerun()  # Final rerun to re-enable the button and display results

# Results section
if st.session_state.analysis_result:
    st.success("Processing completed!")
    result = st.session_state.analysis_result
    st.markdown("---")
    st.markdown("## Video Analysis Results")

    st.markdown("#### Topics")
    st.pills("Topics", result["topics"],label_visibility="collapsed")

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("#### Summary")
        with st.expander("Summary", expanded=True):
            st.write(result["summary"])

        st.markdown("#### Transcript")
        with st.expander("Transcript", expanded=True):
            st.write(result["transcript"])

    with right_col:
        st.markdown("#### Keyframes and Descriptions")
        for i, frame in enumerate(result["keyframes"]):
            st.write(f"**{frame['image_url']}**")
            st.write(frame["description"])
        