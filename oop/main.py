import cv2
import time
from src.game_ui import GameUI
from PunchDetector import PunchDetector

def main():
    # Initialize components
    game_ui = GameUI()
    punch_detector = PunchDetector()

    # Open webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot access the camera.")
            break

        # Flip frame for mirrored view
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        current_time = time.time()

        # Update the current command
        game_ui.update_command()

        # Process frame with MediaPipe
        results = punch_detector.pose.process(rgb_frame)
        if results.pose_landmarks:
            punch_detector.mp_drawing.draw_landmarks(frame, results.pose_landmarks, punch_detector.mp_pose.POSE_CONNECTIONS)
            frame = punch_detector.process_pose(results.pose_landmarks.landmark, frame, current_time, game_ui)

        # Display UI elements
        frame = game_ui.display(frame)

        # Show the frame
        cv2.imshow("Punch Tracking Game", frame)


        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
