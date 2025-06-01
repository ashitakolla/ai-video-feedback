import streamlit as st
from PIL import Image
import tempfile
import os
from pose_detection import process_video

def create_gif_from_segment(frames, fps=3):
    images = []
    for fdata in frames:
        rgb_frame = fdata['frame'][..., ::-1]
        images.append(Image.fromarray(rgb_frame))
    gif_path = os.path.join(tempfile.gettempdir(), f"segment_{frames[0]['timestamp']:.2f}.gif")
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=int(1000 / fps),
        loop=0
    )
    return gif_path

st.set_page_config(page_title="🏓 Pickleball AI Coach", layout="centered")
st.title("🏓 Pickleball AI Coach")
st.markdown(
    "Upload a short video (2–3 minutes) of your pickleball stroke or serve, "
    "and get **AI-generated feedback** on your posture and technique."
)

analysis_type = st.selectbox("🎯 What would you like to analyze?", ["Stroke", "Serve"])
uploaded_file = st.file_uploader("🎥 Upload your pickleball stroke video", type=["mp4", "mov", "avi"])

if uploaded_file:
    input_path = "input_video.mp4"
    output_path = "output_video.mp4"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    st.markdown("### 🔍 Original Video")
    st.video(input_path)

    with st.spinner("⏳ Analyzing your stroke..."):
        feedbacks, score, accepted, rejected = process_video(input_path, output_path, analysis_type.lower())

    st.success("✅ Analysis complete!")

    st.markdown("### 📊 Pose Overlay Video (Slowed)")
    st.video(output_path)

    with open(output_path, "rb") as vid_file:
        st.download_button("⬇️ Download Processed Video", vid_file, file_name="pose_analysis.mp4", mime="video/mp4")

    st.markdown(f"### 🏅 Score: `{score}/100`")
    if score == 100:
        st.success("Perfect form! Great job!")
    elif score >= 75:
        st.info("Good form overall. Few improvements suggested below.")
    elif score >= 50:
        st.warning("Some issues found. Pay attention to feedback.")
    else:
        st.error("Major improvements needed. Please review the feedback carefully.")

    st.markdown("### 📝 AI Feedback")
    st.caption("Feedback is based on posture, stance, and motion.")
    if feedbacks:
        for fb in feedbacks:
            st.write(f"- {fb}")
    else:
        st.info("No major issues detected.")

    # Accepted segments
    # Accepted segments with GIF previews
    import streamlit as st
from PIL import Image
import tempfile
import os

def create_gif_from_segment(frames, fps=3):
    images = []
    for fdata in frames:
        rgb_frame = fdata['frame'][..., ::-1]
        images.append(Image.fromarray(rgb_frame))
    gif_path = os.path.join(tempfile.gettempdir(), f"segment_{frames[0]['timestamp']:.2f}.gif")
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=int(1000 / fps),
        loop=0
    )
    return gif_path

# --- Inside your Streamlit app, after processing video ---

if uploaded_file:
    # Slider for GIF speed (fps)
    gif_fps = st.slider("Adjust GIF playback speed (frames per second)", min_value=1, max_value=10, value=3)

    # Accepted segments with GIF and frames side-by-side
    if accepted:
        with st.expander("✅ Good Posture Segments"):
            for i, segment in enumerate(accepted):
                st.markdown(f"**Segment {i+1}** — `{segment['start']:.2f}s` to `{segment['end']:.2f}s`")

                col1, col2 = st.columns([1, 3])  # Smaller column for GIF, larger for frames

                # Create GIF at user selected speed
                gif_path = create_gif_from_segment(segment['frames'], fps=gif_fps)

                with col1:
                    st.image(gif_path, caption="🟢 Good posture motion preview", use_container_width=True)

                with col2:
                    st.markdown("Frames:")
                    frames_imgs = []
                    for fdata in segment['frames']:
                        rgb_frame = fdata['frame'][..., ::-1]
                        frames_imgs.append(Image.fromarray(rgb_frame))

                    # Show frames horizontally scrollable
                    st.image(frames_imgs, width=100)

                st.markdown("---")

    # Rejected segments with GIF and frames side-by-side
    if rejected:
        with st.expander("❌ Posture Issue Segments"):
            for i, segment in enumerate(rejected):
                issues = ", ".join(segment["reasons"])
                st.markdown(f"**Segment {i+1}** — `{segment['start']:.2f}s` to `{segment['end']:.2f}s`")
                st.markdown(f"**Issues**: {issues}")

                col1, col2 = st.columns([1, 3])

                gif_path = create_gif_from_segment(segment['frames'], fps=gif_fps)

                with col1:
                    st.image(gif_path, caption="🔴 Issue motion preview", use_container_width=True)

                with col2:
                    st.markdown("Frames:")
                    frames_imgs = []
                    for fdata in segment['frames']:
                        rgb_frame = fdata['frame'][..., ::-1]
                        frames_imgs.append(Image.fromarray(rgb_frame))

                    st.image(frames_imgs, width=100)

                st.markdown("---")
