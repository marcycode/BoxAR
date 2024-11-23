from collections import deque
import math

class Speed:

    def __init__(self, maxSize):
        self.prev_time = 0
        self.right_prev_wrist_position = None
        self.left_prev_wrist_position = None
        self.right_prev_hand_position = None
        self.left_prev_hand_position = None
        self.right_speeds = deque(maxlen=maxSize)
        self.right_speeds_y = deque(maxlen=maxSize)
        self.left_speeds = deque(maxlen=maxSize)
        self.left_speeds_y = deque(maxlen=maxSize)
        for _ in range(maxSize):
            self.right_speeds.append(0)
            self.right_speeds_y.append(0)
            self.left_speeds.append(0)
            self.left_speeds_y.append(0)
    
    def euclidean_distance(self, point1, point2):
        """Calculate Euclidean distance between two points."""
        dist = math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
        return dist if point1[0] > point2[0] else -dist

    def calculate_distance(self, curr, prev):
        """Calculate distance between two points."""
        return (curr[0] - prev[0], curr[1] - prev[1])
    
    def calculate_speeds(self, current_time, right_wrist_position, left_wrist_position, right_hand_position, left_hand_position):
        right_average, right_average_y, left_average, left_average_y = 0, 0, 0, 0
        # If a previous wrist position exists, calculate speed
        if self.right_prev_wrist_position is not None and self.left_prev_wrist_position is not None:
            # Calculate displacement
            right = self.euclidean_distance(right_wrist_position, self.right_prev_wrist_position)
            right_x, right_y = self.calculate_distance(right_hand_position, self.right_prev_hand_position)
            left = self.euclidean_distance(left_wrist_position, self.left_prev_wrist_position)
            left_x, left_y = self.calculate_distance(left_hand_position, self.left_prev_hand_position)

            # Calculate time difference
            time_diff = current_time - self.prev_time

            # Calculate speed (pixels per second)
            if time_diff > 0:  # Avoid division by zero
                right_speed = right / time_diff
                left_speed = left / time_diff
                right_speed_y = right_y / time_diff
                left_speed_y = left_y / time_diff
                self.right_speeds.append(right_speed)
                self.right_speeds_y.append(right_speed_y)
                self.left_speeds.append(left_speed)
                self.left_speeds_y.append(left_speed_y)
                right_average = sum(self.right_speeds) / len(self.right_speeds)
                right_average_y = sum(self.right_speeds_y) / len(self.right_speeds_y)
                left_average = sum(self.left_speeds) / len(self.left_speeds)
                left_average_y = sum(self.left_speeds_y) / len(self.left_speeds_y)
        
        # Update the previous wrist position and time
        self.right_prev_wrist_position = right_wrist_position
        self.left_prev_wrist_position = left_wrist_position
        self.right_prev_hand_position = right_hand_position
        self.left_prev_hand_position = left_hand_position
        self.prev_time = current_time
        
        return right_average, right_average_y, left_average, left_average_y