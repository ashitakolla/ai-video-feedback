def process_video(input_path, output_path="output.mp4"):
    import cv2
    import mediapipe as mp
    from ultralytics import YOLO
    from collections import defaultdict

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_draw = mp.solutions.drawing_utils
    model = YOLO("yolov8n.pt")

    cap = cv2.VideoCapture(input_path)
    width, height = int(cap.get(3)), int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    feedbacks = set()
    total_score = 100
    flags = {'knee': False, 'arm': False, 'posture': False, 'stance': False, 'object': False}

    accepted_frames = []
    rejected_frames = []

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        original_frame = frame.copy()
        reasons = []

        # --- YOLO Detection ---
        yolo_results = model.predict(source=frame, conf=0.4, verbose=False)[0]
        object_detected = False
        for r in yolo_results.boxes.data.tolist():
            x1, y1, x2, y2, conf, cls = map(int, r[:6])
            label = model.names[cls]
            if label in ['sports ball', 'paddle', 'person']:
                object_detected = True
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        if not object_detected:
            reasons.append("No paddle/ball detected")
            if not flags['object']:
                feedbacks.add("Object not clearly visible (ball or paddle)")
                total_score -= 10
                flags['object'] = True

        # --- Pose Detection ---
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            lm = results.pose_landmarks.landmark
            def get(l): return lm[mp_pose.PoseLandmark[l].value]

            # Knee bending
            knee_angle = abs(get('LEFT_HIP').y - get('LEFT_KNEE').y) - abs(get('LEFT_KNEE').y - get('LEFT_ANKLE').y)
            if knee_angle > 0.15:
                reasons.append("Knee not bent enough")
                if not flags['knee']:
                    feedbacks.add("Try bending your knees more")
                    total_score -= 25
                    flags['knee'] = True

            # Arm extension
            arm_angle = abs(get('RIGHT_SHOULDER').y - get('RIGHT_ELBOW').y) + abs(get('RIGHT_ELBOW').y - get('RIGHT_WRIST').y)
            if arm_angle < 0.2:
                reasons.append("Arm not extended")
                if not flags['arm']:
                    feedbacks.add("Try extending your arm fully")
                    total_score -= 25
                    flags['arm'] = True

            # Posture
            torso_angle = abs(((get('LEFT_SHOULDER').y + get('RIGHT_SHOULDER').y)/2) - ((get('LEFT_HIP').y + get('RIGHT_HIP').y)/2))
            if torso_angle < 0.05:
                reasons.append("Posture too upright")
                if not flags['posture']:
                    feedbacks.add("Try leaning forward")
                    total_score -= 25
                    flags['posture'] = True

            # Stance
            foot_distance = abs(get('LEFT_HEEL').x - get('RIGHT_HEEL').x)
            if foot_distance < 0.06:
                reasons.append("Stance too narrow")
                if not flags['stance']:
                    feedbacks.add("Widen your stance")
                    total_score -= 25
                    flags['stance'] = True

        # Save selected frames (1 out of every 15)
        if len(accepted_frames) + len(rejected_frames) < 100 and cap.get(cv2.CAP_PROP_POS_FRAMES) % 15 == 0:
            if reasons:
                text = ", ".join(reasons)
                cv2.putText(frame, f"REJECTED: {text}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                rejected_frames.append((frame.copy(), text))
            else:
                cv2.putText(frame, "ACCEPTED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                accepted_frames.append(frame.copy())

        out.write(frame)

    cap.release()
    out.release()
    total_score = max(0, total_score)
    return list(feedbacks), total_score, accepted_frames, rejected_frames
