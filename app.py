from flask import Flask, request, render_template, send_from_directory
from diffusers import DiffusionPipeline
import torch
from moviepy.video.io.VideoFileClip import VideoFileClip
#from moviepy.editor import ImageSequenceClip
import os

# Flask-app configureren
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./output"

# Laad model
#pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4")
#pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipe = DiffusionPipeline.from_pretrained("ali-vilab/text-to-video-ms-1.7b-legacy")
pipe.to("cpu")

# Text-to-video functie
def text_to_video(prompt, frames=10, fps=4):
    images = []
    for i in range(frames):
        image = pipe(prompt).images[0]
        images.append(image)

    # Genereer video
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{prompt.replace(' ', '_')}.mp4")
    clip = ImageSequenceClip([img for img in images], fps=fps)
    clip.write_videofile(video_path, codec="libx264")
    return video_path

# Route voor de GUI
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form["prompt"]
        video_path = text_to_video(prompt)
        return render_template("index.html", video_name=os.path.basename(video_path), videos=os.listdir(app.config['UPLOAD_FOLDER']))
    return render_template("index.html", videos=os.listdir(app.config['UPLOAD_FOLDER']))

# Route om video's te downloaden
@app.route("/download/<video_name>")
def download(video_name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], video_name, as_attachment=True)

if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host="0.0.0.0", port=8080)
