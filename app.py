import streamlit as st
from pose_detection import process_video
import os

# Set up the page
st.set_page_config(page_title="🏓 Pickleball AI Coach", layout="centered")
st.title("🏓 Pickleball AI Coach")
st.markdown(
    "Upload a short video (2–3 minutes) of your pickleball stroke or serve, "
    "and get **AI-generated feedback** on your posture and technique."
)

# File upload
uploaded_file = st.file_uploader("🎥 Upload your pickleball stroke video", type=["mp4", "mov", "avi"])

if uploaded_file:
    # Save uploaded video to disk
    with open("input_video.mp4", "wb") as f:
        f.write(uploaded_file.read())

    # Show original video
    st.markdown("### 🔍 Original Video")
    st.video("input_video.mp4")

    # Process the video
    with st.spinner("⏳ Analyzing your stroke..."):
        feedbacks, score = process_video("input_video.mp4", "output_video.mp4")

    st.success("✅ Analysis complete!")

    # Show processed video
    st.markdown("### 📊 Pose Overlay Video")
    st.video("output_video.mp4")

    # Show score
    st.markdown(f"### 🏅 Score: `{score}/100`")
    if score == 100:
        st.success("Perfect form! Great job!")
    elif score >= 75:
        st.info("Good form overall. Few improvements suggested below.")
    elif score >= 50:
        st.warning("Some issues found. Pay attention to feedback.")
    else:
        st.error("Major improvements needed. Please review the feedback carefully.")

    # Show AI feedback
    st.markdown("### 📝 AI Feedback")
    if feedbacks:
        for fb in feedbacks:
            st.write(f"- {fb}")
    else:
        st.info("No major issues detected.")
