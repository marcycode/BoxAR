from abc import ABC, abstractmethod
import cv2


class Observer(ABC):
    @abstractmethod
    def notify(self, *args, **kwargs):
        pass


class CollisionObserver(Observer):
    def __init__(self):
        self.collisionCount = 0

    def notify(self,  *args, **kwargs):
        self.collisionCount += 1

    def getCollisionCount(self):
        return self.collisionCount

    def drawCollisionCount(self, frame):
        cv2.putText(frame, f"Collisions: {self.collisionCount}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
