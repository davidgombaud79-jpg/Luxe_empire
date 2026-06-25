import os
import requests
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_video():
    data = request.json
    video_url = data.get('video_url')
    caption = data.get('caption', '')
    
    # Télécharger la vidéo
    r = requests.get(video_url)
    with open('/tmp/input.mp4', 'wb') as f:
        f.write(r.content)
    
    # FFmpeg : ajouter texte sur la vidéo
    cmd = [
        'ffmpeg', '-i', '/tmp/input.mp4',
        '-vf', f"drawtext=text='{caption}':fontsize=40:fontcolor=white:x=50:y=50",
        '-c:a', 'copy',
        '/tmp/output.mp4', '-y'
    ]
    subprocess.run(cmd)
    
    return jsonify({'status': 'done', 'output': '/tmp/output.mp4'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
