from flask import Flask, request, render_template, send_from_directory
from diffusers import StableDiffusionPipeline
import torch
from moviepy.video.io.VideoFileClip import VideoFileClip
#from moviepy.editor import ImageSequenceClip  # Correcte import voor video
import os

# Flask-app configureren
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./output"

# Laad model (met lagere resolutie)
pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2")
pipe.to("cpu")

# Text-to-video functie
def text_to_video(prompt, frames=10, fps=4):
    images = []
    
    # Laag resolutie instellen (bijvoorbeeld 256x256)
    height = 256
    width = 256
    
    for i in range(frames):
        # Genereer afbeelding met lage resolutie
        image = pipe(prompt, height=height, width=width).images[0]
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
