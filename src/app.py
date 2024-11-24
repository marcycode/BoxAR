from flask import Flask, render_template, Response, request
from camera import VideoCamera
from multiplayer import MultiPlayerConnectionData


app = Flask(__name__)
camera_context: VideoCamera = None
score = 0
flag = True


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
    del camera


@app.route("/boxing_feed")
def boxing_feed():
    global camera_context
    mode = request.args.get("mode")
    if mode is None:
        mode = "free-play"
    page_width = int(request.args.get("page_width"))
    page_height = int(request.args.get("page_height"))
    if not camera_context:
        # TEMP TESTING CODE
        multiplayerData = MultiPlayerConnectionData(
            peer_ip="10.217.13.79", peer_port=8080)
        camera_context = VideoCamera(
            page_width, page_height, multiplayerData=multiplayerData)
    response = Response(
        gen(camera_context, mode),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.post("/api/punch")
def receive_punch():
    global camera_context
    data = request.json
    assert ("punchLocation" in data)

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
        data.get("punchLocation"), multiplayerPunch=True)
    return "Punch received"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True, use_reloader=False)
