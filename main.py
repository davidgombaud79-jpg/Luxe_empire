import os
import requests
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'Luxe Empire FFmpeg service is running'})

@app.route('/process', methods=['POST'])
def process_video():
    data = request.json
    video_url = data.get('video_url')
    caption = data.get('caption', '')
    
    r = requests.get(video_url)
    with open('/tmp/input.mp4', 'wb') as f:
        f.write(r.content)
    
    cmd = [
        'ffmpeg', '-i', '/tmp/input.mp4',
        '-vf', f"drawtext=text='{caption}':fontsize=40:fontcolor=white:x=50:y=50",
        '-c:a', 'copy',
        '/tmp/output.mp4', '-y'
    ]
    subprocess.run(cmd)
    
    return jsonify({'status': 'done', 'output': '/tmp/output.mp4'})

@app.route('/get_token', methods=['POST'])
def get_token():
    data = request.json
    payload = {
        'client_key': data['client_key'],
        'client_secret': data['client_secret'],
        'code': data['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': data['redirect_uri']
    }
    r = requests.post(
        'https://open.tiktokapis.com/v2/oauth/token/',
        data=payload,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    return jsonify(r.json())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
