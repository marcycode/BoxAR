from pygame import mixer
import time


class SoundEffect:
    def __init__(self, file_path, cooldown=0.5):
        """
        Initialize the sound effect with a cooldown period.
        """
        mixer.init()
        self.sound = mixer.Sound(file_path)
        self.last_played = 0
        self.cooldown = cooldown  # Cooldown in seconds

    def play(self):
        """
        Play the sound with a cooldown to avoid rapid repetition.

        Returns:
            bool: True if the sound was played, False if still on cooldown.
        """
        current_time = time.time()
        if current_time - self.last_played > self.cooldown:
            self.sound.play()
            self.last_played = current_time
            return True
        return False
