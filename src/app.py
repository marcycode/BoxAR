from flask import Flask, render_template, Response, request
from flask_cors import CORS, cross_origin
from camera import VideoCamera
from multiplayer import MultiPlayerConnectionData

app = Flask(__name__)
cors = CORS(app)  # allow CORS for all domains on all routes.
app.config["CORS_HEADERS"] = "Content-Type"
camera_context: VideoCamera = None
score = 0
flag = True
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
    global flag
    return {"score": str(score), "finished": str(not flag)}


@app.route("/restart", methods=["POST"])
def restart():
    global video_camera_instance
    global flag
    flag = True
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
    global flag
    global score
    s = 0
    while flag:
        if mode == "survival":
            frame, flag, s = camera.survival_mode()
        elif mode == "scoring-mode":
            frame, flag, s = camera.score_mode()
        elif mode == "free-play":
            frame = camera.free_mode()
        elif mode == "multiplayer":
            # TODO add multiplayer mode logic
            frame, flag = camera.multiplayer_mode()
        else:
            frame = camera.free_mode()
        score = s
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")
    video_camera_instance.restart()

@app.route("/boxing_feed")
def boxing_feed():
    global video_camera_instance  # Access the global instance
    mode = request.args.get("mode")
    if mode is None:
        mode = "free-play"
    page_width = int(request.args.get("page_width"))
    page_height = int(request.args.get("page_height"))
    if not video_camera_instance:
        multiplayerData = None
        # TEMP TESTING CODE
        if mode == "multiplayer":
            multiplayerData = MultiPlayerConnectionData(
                peer_ip="10.217.13.79", peer_port=8080
            )
        video_camera_instance = VideoCamera(
            page_width, page_height, multiplayerData=multiplayerData
        )
    response = Response(
        gen(video_camera_instance, mode),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.post("/api/punch")
def receive_punch():
    global camera_context
    data = request.json
    assert "punchLocation" in data

    if not camera_context:
        res = Response("Camera not initialized", status=500)
        return res

    punchLocation = data.get("punchLocation")
    try:
        punchLocation = (float(punchLocation[0]), float(punchLocation[1]))
    except ValueError:
        res = Response("Invalid punch location", status=400)
        return res
    camera_context.challengeManager.addPunchChallenge(
        data.get("punchLocation"), multiplayerPunch=True
    )
    return "Punch received"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True, use_reloader=False)
