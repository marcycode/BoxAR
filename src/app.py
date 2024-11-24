from flask import Flask, render_template, Response, request
from flask_cors import CORS  # Import Flask-CORS
from camera import VideoCamera

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables
score = 0
video_camera_instance = None  # Initialize as None


@app.route("/")
def index():
    return "Hello world"


@app.route("/ping")
def ping():
    return "Successfully pinged"


@app.route("/score")
def points():
    global score
    return str(score)


@app.route("/restart", methods=["POST"])
def restart():
    global video_camera_instance
    try:
        if video_camera_instance is not None:
            video_camera_instance.restart()
            return "Game restarted successfully", 200
        else:
            return "No active game instance to restart", 400
    except Exception as e:
        print(f"Error during restart: {e}")  # Log the error to the server console
        return f"An error occurred: {str(e)}", 500

def gen(camera, mode):
    flag = True
    global score
    s = 0
    while flag:
        if mode == "survival":
            frame, flag, s = camera.survival_mode()
        elif mode == "scoring-mode":
            frame, flag, s = camera.score_mode()
        elif mode == "free-play":
            frame = camera.free_mode()
        score = s
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")
    del camera


@app.route("/boxing_feed")
def boxing_feed():
    global video_camera_instance  # Access the global instance
    mode = request.args.get("mode")
    if mode is None:
        mode = "free-play"
    page_width = int(request.args.get("page_width"))
    page_height = int(request.args.get("page_height"))
    if video_camera_instance is None:
        video_camera_instance = VideoCamera(page_width, page_height)  # Initialize instance
    response = Response(
        gen(video_camera_instance, mode),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True, use_reloader=False)
