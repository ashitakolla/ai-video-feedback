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
    input_path = "input_video.mp4"
    output_path = "output_video.mp4"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    # Show original video
    st.markdown("### 🔍 Original Video")
    st.video(input_path)

    # Process the video
    with st.spinner("⏳ Analyzing your stroke..."):
        feedbacks, score, accepted, rejected = process_video(input_path, output_path)

    st.success("✅ Analysis complete!")

    # Show processed video
    st.markdown("### 📊 Pose Overlay Video")
    st.video(output_path)

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

    # --- Show accepted frames ---
    if accepted:
        st.subheader("✅ Good Posture Frames")
        for i, frame in enumerate(accepted[:5]):
            st.image(frame, caption=f"Accepted Frame {i+1}", use_container_width=True)

    # --- Show rejected frames with reasons ---
    if rejected:
        st.subheader("❌ Rejected Posture Frames")
        for i, (frame, reason) in enumerate(rejected[:5]):
            st.image(frame, caption=f"Rejected Frame {i+1}: {reason}", use_container_width=True)
