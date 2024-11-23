import cv2


class VideoCamera(object):
    def __init__(self, page_width, page_height):
        self.video = cv2.VideoCapture(1)
        self.video.set(3, page_width / 2)  # 3 -> WIDTH
        self.video.set(4, page_height / 2)  # 4 -> HEIGHT

    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, frame = self.video.read()
        ret, jpeg = cv2.imencode(".jpg", frame)
        return jpeg.tobytes()
