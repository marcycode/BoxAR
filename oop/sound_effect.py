from pygame import mixer


class SoundEffect:
    """Class to manage sound effects using pygame.mixer."""
    
    def __init__(self, sound_file):
        """
        Initialize the SoundEffect object.

        Args:
            sound_file (str): Path to the sound file.
        """
        mixer.init()
        self.sound = mixer.Sound(sound_file)

    def play(self):
        """Play the sound effect."""
        self.sound.play()
