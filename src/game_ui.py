import cv2
import time
import random

class GameUI:
    def __init__(self):
        self.score = 0
        self.current_command = None
        self.last_command_time = time.time()
        self.command_interval = 3  # Command update interval in seconds
        self.commands = ["Left Jab", "Right Jab", "Dodge"]

    def update_command(self):
        """Generate a new command if the interval has elapsed."""
        if time.time() - self.last_command_time > self.command_interval or self.current_command is None:
            self.current_command = random.choice(self.commands)
            self.last_command_time = time.time()

    def clear_command(self):
        """Clear the current command after a correct punch."""
        self.current_command = None

    def increment_score(self):
        """Increment the player's score."""
        self.score += 1

    def display(self, frame):
        """Display the current command and score on the screen."""
        if self.current_command:
            cv2.putText(frame, f"Command: {self.current_command}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.putText(frame, f"Score: {self.score}", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return frame
