import cv2
import time


class PunchAnimation:
    def __init__(self):
        self.active = False
        self.start_time = 0
        self.duration = 0.5  # Animation duration in seconds
        self.position = (0, 0)  # Position of the animation (x, y)
        self.animation_color = (0, 255, 0)  # Green color for animation
        self.animation_thickness = 5


    def draw(self, frame, position):
        """
        Draw the animation at the specified position if active.

        Args:
            frame (ndarray): The current video frame.

        Returns:
            ndarray: The updated frame with the animation.
        """
        self.active = True
        self.start_time = time.time()
        self.position = (int(position[0]), int(position[1])) 
        if self.active:
            elapsed_time = time.time() - self.start_time
            if elapsed_time < self.duration:
                # Draw a pulsing circle animation
                radius = int(20 + (30 * (elapsed_time / self.duration)))  # Dynamic radius
                cv2.circle(
                    frame, self.position, radius,
                    self.animation_color, self.animation_thickness
                )
            else:
                self.active = False  # Deactivate after the duration

        return frame
