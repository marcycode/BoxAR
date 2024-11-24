from flask import Flask, render_template, Response, request
from camera import VideoCamera


app = Flask(__name__)
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
            frame = camera.multiplayer_mode()
        else:
            frame = camera.free_mode()
        score = s
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")
    del camera


@app.route("/boxing_feed")
def boxing_feed():
    mode = request.args.get("mode")
    if mode is None:
        mode = "free-play"
    page_width = int(request.args.get("page_width"))
    page_height = int(request.args.get("page_height"))
    response = Response(
        gen(VideoCamera(page_width, page_height), mode),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True, use_reloader=False)
