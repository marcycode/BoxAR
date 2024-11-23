import random
import time
import cv2

class GameUI:
    """Manages the game logic, score, and UI."""

    def __init__(self):
        self.score = 0
        self.current_command = None
        self.last_command_time = time.time()
        self.command_interval = 3 # Command duration in seconds

    def generate_command(self):
        """Generate a random command: 'Left Jab' or 'Right Jab'."""
        self.current_command = random.choice(["Left Jab", "Right Jab"])
        self.last_command_time = time.time()

    def update_command(self):
        """Update the command if the interval has elapsed."""
        if time.time() - self.last_command_time > self.command_interval:
            self.generate_command()

    def display(self, frame):
        """Display the current command and score on the screen."""
        # Display the current command
        if self.current_command:
            cv2.putText(frame, f"Command: {self.current_command}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        # Display the score
        cv2.putText(frame, f"Score: {self.score}", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        return frame

    def increment_score(self):
        """Increment the score when the correct jab is detected."""
        self.score += 1
