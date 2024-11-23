import cv2
from game_ui import GameUI
from punch_tracker import PunchTracker
from sound_effect import SoundEffect

def main():
    # Initialize components
    game_ui = GameUI()
    punch_tracker = PunchTracker(game_ui)
    sound_effect = SoundEffect("Punch.mp3")  # Replace with your sound file

    # Open webcam
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot access the camera.")
            break

        # Flip the frame for a mirrored effect
        frame = cv2.flip(frame, 1)

        # Update game logic
        game_ui.update_command()

        # Process the frame for punch detection
        frame = punch_tracker.process_frame(frame)

        # Display game information
        frame = game_ui.display(frame)

        # Show the video feed
        cv2.imshow("Punch Game", frame)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
