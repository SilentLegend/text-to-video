import ray
import os
from diffusers import StableDiffusionPipeline
from moviepy.video.io.VideoFileClip import VideoFileClip
#from moviepy.editor import ImageSequenceClip
from flask import Flask, request, render_template, send_from_directory
from threading import Thread
import time

os.environ["RAY_CLIENT_TIMEOUT"] = "600"  # Verhoogde timeout

# Initialiseer Ray (maak verbinding met master node)
ray.init(address="ray://192.168.178.157:6379", ignore_reinit_error=True)

# Laad model vooraf (laad het model voordat de Flask-server draait)
pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2")
pipe.to("cpu")

# Functie om een video te genereren voor een gegeven prompt
@ray.remote
def generate_video_for_prompt(prompt, frames=10, fps=4):
    images = []
    height = 256
    width = 256
    
    # Genereer beelden
    for i in range(frames):
        image = pipe(prompt, height=height, width=width).images[0]
        images.append(image)

    # Genereer video
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{prompt.replace(' ', '_')}.mp4")
    clip = ImageSequenceClip([img for img in images], fps=fps)
    clip.write_videofile(video_path, codec="libx264")
    return video_path

# Flask-app configureren
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./output"

# Text-to-video functie
def text_to_video(prompt, frames=10, fps=4):
    # Verdeel de frames over de workers
    futures = [generate_video_for_prompt.remote(prompt, frames, fps) for _ in range(5)]  # Aantal workers
    video_paths = ray.get(futures)
    return video_paths

# Route voor de GUI
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form["prompt"]
        video_paths = text_to_video(prompt)
        return render_template("index.html", video_name=os.path.basename(video_paths[0]), videos=os.listdir(app.config['UPLOAD_FOLDER']))
    return render_template("index.html", videos=os.listdir(app.config['UPLOAD_FOLDER']))

# Route om video's te downloaden
@app.route("/download/<video_name>")
def download(video_name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], video_name, as_attachment=True)

if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Start de Flask-server in een aparte thread zodat het model geladen wordt en de server draait
    def start_flask():
        app.run(host="0.0.0.0", port=8080)

    # Start de Flask-server
    Thread(target=start_flask).start()
