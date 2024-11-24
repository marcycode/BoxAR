import cv2


class CooldownBar():
    def __init__(self, maxCooldown=15):
        self.maxCooldown = maxCooldown
        self.currentCooldown = 0

    def setMaxCooldown(self, maxCooldown):
        self.maxCooldown = maxCooldown

    def updateCooldown(self):
        if self.currentCooldown > 0:
            self.currentCooldown -= 1

    def resetCooldown(self):
        self.currentCooldown = self.maxCooldown

    def displayCooldown(self, frame):

        # Cooldown Bar Dimensions
        bar_width = 300
        bar_height = 30

        bar_x = frame.shape[1] // 2 - bar_width // 2
        bar_y = 50

        # Calculate current cooldown bar width
        current_bar_width = int(
            (self.currentCooldown / self.maxCooldown) * bar_width)

        # cv2.putText(frame, f"Cooldown: {self.currentCooldown}", (bar_x - 300, bar_y + 20),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        # Draw the background (gray bar)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width,
                      bar_y + bar_height), (128, 128, 128), -1)

        # Draw the current cooldown bar
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x +
                      current_bar_width, bar_y + bar_height), (50, 50, 50), -1)
