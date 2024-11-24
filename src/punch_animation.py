import cv2
import time
from PIL import Image
import numpy as np


class PunchAnimation:
    def __init__(self, gif_path):
        """
        Initialize the punch animation with a GIF.

        Args:
            gif_path (str): Path to the GIF file.
        """
        self.active = False
        self.start_time = 0
        self.duration = 0.5  # Animation duration in seconds
        self.position = (0, 0)  # Position of the animation (x, y)
        self.frames = self.load_gif_frames(gif_path)  # Load GIF frames
        self.current_frame_index = 0

    def load_gif_frames(self, gif_path):
        
        gif = Image.open(gif_path)
        frames = []

        try:
            while True:
                frame = gif.copy().convert("RGBA")  # Convert to RGBA for transparency
                frame_np = cv2.cvtColor(
                    np.array(frame), cv2.COLOR_RGBA2BGRA
                )  # Convert to OpenCV-compatible format
                frames.append(frame_np)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass

        return frames


    def trigger(self, position):
        """
        Activate the animation at the specified position.

        Args:
            position (tuple): (x, y) position to overlay the GIF.
        """
        self.active = True
        self.start_time = time.time()
        self.position = position
        self.current_frame_index = 0

    def draw(self, frame):
        """
        Draw the animation (GIF) on the frame if active.

        Args:
            frame (ndarray): The current video frame.

        Returns:
            ndarray: The frame with the animation overlay.
        """
        if self.active:
            elapsed_time = time.time() - self.start_time
            if elapsed_time < self.duration:
                # Calculate the current frame index
                total_frames = len(self.frames)
                frame_duration = self.duration / total_frames
                self.current_frame_index = int(elapsed_time // frame_duration) % total_frames

                # Overlay the current frame at the specified position
                self.overlay_gif_frame(frame, self.frames[self.current_frame_index])
            else:
                self.active = False  # Deactivate animation after duration

        return frame

    def overlay_gif_frame(self, frame, gif_frame):
        """
        Overlay a single GIF frame on the video frame.

        Args:
            frame (ndarray): The current video frame.
            gif_frame (ndarray): The GIF frame to overlay.
        """
        x, y = self.position
        h, w, _ = gif_frame.shape

        # Calculate the region of interest (ROI) on the video frame
        x1, y1 = max(0, int(x - w // 2)), max(0, int(y - h // 2))
        x2, y2 = min(frame.shape[1], int(x + w // 2)), min(frame.shape[0], int(y + h // 2))

        # Ensure the dimensions are valid and integers
        width = max(1, int(x2 - x1))
        height = max(1, int(y2 - y1))

        # Resize the GIF frame to fit within the ROI
        resized_frame = cv2.resize(gif_frame, (width, height), interpolation=cv2.INTER_AREA)

        # Extract the alpha channel for blending
        alpha_channel = resized_frame[:, :, 3] / 255.0
        for c in range(3):  # Loop over the color channels
            frame[y1:y2, x1:x2, c] = (
                alpha_channel * resized_frame[:, :, c] +
                (1 - alpha_channel) * frame[y1:y2, x1:x2, c]
            )
