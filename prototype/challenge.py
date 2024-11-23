import random
import cv2


class Challenge():
    def __init__(self, name, image, observer=None):
        self.name = name
        self.image = image
        self.observer = observer
        self.expired = False


class PunchChallenge(Challenge):
    END_SIZE = 600
    BASE_IMG = cv2.imread("glove.png")

    def __init__(self, x: int, y: int, startSize: int, timeToLive=3, observer=None):
        super().__init__("Punch Challenge", PunchChallenge.BASE_IMG, observer)
        self.x = x
        self.y = y
        self.size = startSize
        self.timeToLive = timeToLive
        self.growthRate = ((self.END_SIZE - startSize) // timeToLive) + 1

    def update(self):
        self.size += self.growthRate
        self.image = cv2.resize(PunchChallenge.BASE_IMG,
                                (self.size, self.size))
        self.timeToLive -= 1
        if self.timeToLive == 0:
            if self.observer:
                self.observer.notify(self)
            self.expired = True

    def overlayChallenge(self, frame):
        # too lazy to refactor vars
        x = self.x
        y = self.y
        self.image = cv2.resize(PunchChallenge.BASE_IMG,
                                (self.size, self.size))
        frame[y:y + self.size, x:x+self.size] = cv2.addWeighted(
            frame[y:y + self.size, x:x+self.size], 1.0, self.image, 1.0, 1)


class ChallengeManager():
    def __init__(self):
        self.challenges: list[PunchChallenge] = []

    def update_challenges(self):
        for challenge in self.challenges:
            challenge.update()
            if challenge.expired:
                self.challenges.remove(challenge)
        # handle collisions

    def generatePunchChallenge(self, frameWidth=1920, frameHeight=1080, startSize=50, timeToLive=3, observer=None):
        x = random.randint(0, frameWidth - PunchChallenge.END_SIZE)
        y = random.randint(0, frameHeight - PunchChallenge.END_SIZE)
        challenge = PunchChallenge(x, y, startSize, timeToLive, observer)
        self.challenges.append(challenge)
        return challenge

    def draw_challenges(self, frame):
        for challenge in self.challenges:
            challenge.overlayChallenge(frame)
