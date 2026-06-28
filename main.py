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

@app.route('/publish_tiktok', methods=['POST'])
def publish_tiktok():
    data = request.json
    access_token = data.get('access_token')
    video_url = data.get('video_url')
    title = data.get('title', 'Luxe Empire')

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; charset=UTF-8'
    }

    # Télécharger la vidéo
    r = requests.get(video_url)
    video_bytes = r.content
    video_size = len(video_bytes)

    # Étape 1 : Init upload
    init_payload = {
        "post_info": {
            "title": title,
            "privacy_level": "SELF_ONLY",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": video_size,
            "total_chunk_count": 1
        }
    }

    init_r = requests.post(
        'https://open.tiktokapis.com/v2/post/publish/inbox/video/init/',
        json=init_payload,
        headers=headers
    )
    init_data = init_r.json()

    if 'data' not in init_data:
        return jsonify({'error': 'Init failed', 'details': init_data})

    publish_id = init_data['data']['publish_id']
    upload_url = init_data['data']['upload_url']

    # Étape 2 : Upload vidéo
    upload_headers = {
        'Content-Type': 'video/mp4',
        'Content-Range': f'bytes 0-{video_size-1}/{video_size}'
    }
    upload_r = requests.put
