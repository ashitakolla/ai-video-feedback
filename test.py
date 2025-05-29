import os
import streamlit as st

video_path = os.path.abspath("output.mp4")
st.write("Trying to load video from:", video_path)

if os.path.exists(video_path):
    video_file = open(video_path, "rb")
    video_bytes = video_file.read()
    st.video(video_bytes)
else:
    st.error("Video file not found!")
