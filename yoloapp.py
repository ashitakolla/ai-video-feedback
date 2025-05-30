from ultralytics import YOLO
import mediapipe as mp
import cv2
import os

# Load YOLO and MediaPipe
model = YOLO("yolov8n.pt")
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

# Video input
cap = cv2.VideoCapture("inputvideo.mp4")

# Create folders
os.makedirs("rejected_frames", exist_ok=True)
os.makedirs("accepted_frames", exist_ok=True)

frame_id = 0
frame_feedback = {}

def get_landmark(landmarks, label):
    return landmarks[mp_pose.PoseLandmark[label].value]

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1
    results = model(frame)[0]
    feedback_this_frame = {}

    for i, box in enumerate(results.boxes):
        if int(box.cls[0]) != 0:  # Only detect person
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        person_crop = frame[y1:y2, x1:x2]
        person_rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
        pose_result = pose.process(person_rgb)

        person_feedback = []

        if pose_result.pose_landmarks:
            landmarks = pose_result.pose_landmarks.landmark

            try:
                # Pose checks
                lknee = get_landmark(landmarks, 'LEFT_KNEE')
                lhip = get_landmark(landmarks, 'LEFT_HIP')
                lankle = get_landmark(landmarks, 'LEFT_ANKLE')
                knee_angle = abs(lhip.y - lknee.y) - abs(lknee.y - lankle.y)
                if knee_angle > 0.15:
                    person_feedback.append("Try bending your knees more")

                rshoulder = get_landmark(landmarks, 'RIGHT_SHOULDER')
                relbow = get_landmark(landmarks, 'RIGHT_ELBOW')
                rwrist = get_landmark(landmarks, 'RIGHT_WRIST')
                arm_extension = abs(rshoulder.y - relbow.y) + abs(relbow.y - rwrist.y)
                if arm_extension < 0.2:
                    person_feedback.append("Extend your arm fully")

                lshoulder = get_landmark(landmarks, 'LEFT_SHOULDER')
                rshoulder = get_landmark(landmarks, 'RIGHT_SHOULDER')
                lhip = get_landmark(landmarks, 'LEFT_HIP')
                rhip = get_landmark(landmarks, 'RIGHT_HIP')
                torso_angle = abs(((rshoulder.y + lshoulder.y) / 2) - ((rhip.y + lhip.y) / 2))
                if torso_angle < 0.05:
                    person_feedback.append("Lean forward for better balance")

                lheel = get_landmark(landmarks, 'LEFT_HEEL')
                rheel = get_landmark(landmarks, 'RIGHT_HEEL')
                foot_distance = abs(lheel.x - rheel.x)
                if foot_distance < 0.05:
                    person_feedback.append("Widen your stance")

            except:
                person_feedback.append("Some landmarks missing")

            mp_draw.draw_landmarks(
                person_crop,
                pose_result.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

        else:
            person_feedback.append("Pose not detected")

        # Save frame based on feedback
        if person_feedback:
            # ❌ Rejected frame
            rejected_path = f"rejected_frames/frame{frame_id}_person{i+1}.jpg"
            cv2.imwrite(rejected_path, frame)
        else:
            # ✅ Accepted frame
            accepted_path = f"accepted_frames/frame{frame_id}_person{i+1}.jpg"
            cv2.imwrite(accepted_path, frame)

        # Update feedback dictionary
        feedback_this_frame[i + 1] = {
            'feedback': person_feedback,
            'screenshot_saved': True
        }

        # Annotate label on original frame
        label = f"P{i+1}: {'Good' if not person_feedback else 'Fix'}"
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 0) if not person_feedback else (0, 0, 255), 2)

        frame[y1:y2, x1:x2] = person_crop

    frame_feedback[frame_id] = feedback_this_frame

    # Show live preview
    cv2.imshow("Multi-Person Pose Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
