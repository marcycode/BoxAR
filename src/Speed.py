from collections import deque
from math import sqrt

class Speed:

    def __init__(self, maxSize):
        self.prev_time = 0
        self.right_prev_wrist_position = None
        self.left_prev_wrist_position = None
        self.right_speeds = deque(maxlen=maxSize)
        self.left_speeds = deque(maxlen=maxSize)
        self.prev_left, self.prev_right = None, None
        for _ in range(maxSize):
            self.right_speeds.append(0)
            self.left_speeds.append(0)
    
    def euclidean_distance(self, point1, point2):
        """Calculate Euclidean distance between two points."""
        return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def calculate_distance(self, curr, prev):
        """Calculate distance between two points."""
        return (curr[0] - prev[0], curr[1] - prev[1])
    
    def calculate_speeds(self, current_time, right_wrist_position, left_wrist_position):
        right_average, left_average= 0, 0
        # If a previous wrist position exists, calculate speed
        if self.right_prev_wrist_position is not None and self.left_prev_wrist_position is not None:
            # Calculate displacement
            right = self.euclidean_distance(right_wrist_position, self.right_prev_wrist_position)
            left = self.euclidean_distance(left_wrist_position, self.left_prev_wrist_position)

            # Calculate time difference
            time_diff = current_time - self.prev_time

            # Calculate speed (pixels per second)
            if time_diff > 0:  # Avoid division by zero
                right_speed = right / time_diff
                left_speed = left / time_diff
                self.right_speeds.append(right_speed)
                self.left_speeds.append(left_speed)
                right_average = sum(self.right_speeds) / len(self.right_speeds)
                left_average = sum(self.left_speeds) / len(self.left_speeds)
        
        # Update the previous wrist position and time
        self.right_prev_wrist_position = right_wrist_position
        self.left_prev_wrist_position = left_wrist_position
        self.prev_time = current_time
        
        return right_average, left_average

    def calculate_speed_towards_camera(self, current_time, right_hand, left_hand):
        right_average, left_average= 0, 0
        # If a previous wrist position exists, calculate speed
        if self.prev_right is not None and self.prev_left is not None:
            right = right_hand - self.prev_right
            left = left_hand - self.prev_left
            time_diff = current_time - self.prev_time

            # Calculate speed (pixels per second)
            if time_diff > 0:  # Avoid division by zero
                right_speed = right / time_diff
                left_speed = left / time_diff
                self.right_speeds.append(right_speed)
                self.left_speeds.append(left_speed)
                right_average = sum(self.right_speeds) / len(self.right_speeds)
                left_average = sum(self.left_speeds) / len(self.left_speeds)

        self.prev_left, self.prev_right = left_hand, right_hand
        self.prev_time = current_time

        return right_average, left_average