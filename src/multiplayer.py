import requests
from challenge import ChallengeManager
from typing import NamedTuple
import time


class MultiPlayerConnectionData(NamedTuple):
    peer_ip: str
    peer_port: int


class MultiPlayerManager():
    def __init__(self, peer_ip: str, peer_port: int, localChallengeManager: ChallengeManager, cooldownSeconds=1):
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.peer_url = f"http://{peer_ip}:{peer_port}"
        self.connected = False
        self.localChallengeManager = localChallengeManager
        self.lastSentTime = time.time()
        self.cooldownSeconds = cooldownSeconds

    def checkConnection(self):
        try:
            requests.get(f"http://{self.peer_ip}:{self.peer_port}")
            self.connected = True
        except requests.ConnectionError:
            self.connected = False

    def sendPunch(self, punchLocation: tuple[float, float]):
        if time.time() - self.lastSentTime < self.cooldownSeconds:
            return
        data = {"punchLocation": punchLocation}
        try:
            requests.post(f"{self.peer_url}/api/punch",
                          json=data, timeout=0.35)
            self.lastSentTime = time.time()
        except requests.ConnectionError:
            self.connected = False
            print("Warning: Connection error")
        except requests.RequestException:
            print("Warning: Request error while sending punch")

    def receivePunch(self, punchLocation: tuple[float, float]):
        self.localChallengeManager.generatePunchChallenge(
            punchLocation, multiplayerPunch=True)
