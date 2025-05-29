# pose_video_processor.py
import cv2
import mediapipe as mp

def process_video(input_path, output_path="output.mp4"):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # ✅ Use mp4v codec for better Streamlit support
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    feedbacks = set()
    total_score = 100

    # Flags to ensure feedback is not repeated
    knee_flag = arm_flag = posture_flag = stance_flag = False

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            # Draw landmarks on the frame
            mp_draw.draw_landmarks(
                frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2)
            )

            landmarks = results.pose_landmarks.landmark
            def get(l): return landmarks[mp_pose.PoseLandmark[l].value]

            # Knee bending check
            left_knee = get('LEFT_KNEE')
            left_hip = get('LEFT_HIP')
            left_ankle = get('LEFT_ANKLE')
            knee_angle = abs(left_hip.y - left_knee.y) - abs(left_knee.y - left_ankle.y)
            if not knee_flag and knee_angle > 0.1:
                feedbacks.add("Try bending your knees more")
                total_score -= 25
                knee_flag = True

            # Arm extension check
            right_shoulder = get('RIGHT_SHOULDER')
            right_elbow = get('RIGHT_ELBOW')
            right_wrist = get('RIGHT_WRIST')
            arm_angle = abs(right_shoulder.y - right_elbow.y) + abs(right_elbow.y - right_wrist.y)
            if not arm_flag and arm_angle < 0.3:
                feedbacks.add("Try extending your arm fully during the swing")
                total_score -= 25
                arm_flag = True

            # Posture check
            left_shoulder = get('LEFT_SHOULDER')
            right_shoulder = get('RIGHT_SHOULDER')
            left_hip = get('LEFT_HIP')
            right_hip = get('RIGHT_HIP')
            torso_angle = abs(((right_shoulder.y + left_shoulder.y) / 2) - ((right_hip.y + left_hip.y) / 2))
            if not posture_flag and torso_angle < 0.1:
                feedbacks.add("Try leaning forward slightly for better balance")
                total_score -= 25
                posture_flag = True

            # Foot stance check
            left_heel = get('LEFT_HEEL')
            right_heel = get('RIGHT_HEEL')
            foot_distance = abs(left_heel.x - right_heel.x)
            if not stance_flag and foot_distance < 0.08:
                feedbacks.add("Try widening your stance for better stability")
                total_score -= 25
                stance_flag = True

        # Write frame with drawing to output video
        out.write(frame)

    cap.release()
    out.release()

    total_score = max(0, total_score)
    return list(feedbacks), total_score
