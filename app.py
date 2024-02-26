import json
from flask import Flask, request, jsonify
import os
import subprocess  # Importa subprocess

app = Flask(__name__)

UPLOAD_VIDEO_FOLDER = 'uploads'
UPLOAD_AUDIO_FOLDER = 'audios'

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'flv', 'wmv'}
app.config['UPLOAD_VIDEO_FOLDER'] = UPLOAD_VIDEO_FOLDER
app.config['UPLOAD_AUDIO_FOLDER'] = UPLOAD_AUDIO_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def has_audio_stream(video_path):
    """
    Verifica si el archivo de video tiene una pista de audio.
    """
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        streams = json.loads(result.stdout)
        for stream in streams['streams']:
            if stream['codec_type'] == 'audio':
                return True
        return False
    except Exception as e:
        print(f"Error checking audio stream: {e}")
        return False
    
def extract_audio_from_video(video_path, audio_path):
    """
    Utiliza FFmpeg para extraer el audio de un video.
    """
    # Comando para extraer el audio
    audio_dir = os.path.dirname(audio_path)
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    command = ['ffmpeg', '-i', video_path, '-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k', '-f', 'mp3', audio_path]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@app.route('/upload-video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'No selected file or file extension not allowed'}), 400
    
    filename = file.filename
    if not os.path.exists(app.config['UPLOAD_VIDEO_FOLDER']):
        os.makedirs(app.config['UPLOAD_VIDEO_FOLDER'])
    
    video_path = os.path.join(app.config['UPLOAD_VIDEO_FOLDER'], filename)
    file.save(video_path)
    if not has_audio_stream(video_path):
        return jsonify({'message': 'Video not have any sound'}), 400

    # Prepara el nombre del archivo de audio
    audio_filename = os.path.splitext(filename)[0] + '.mp3'
    audio_path = os.path.join(app.config['UPLOAD_AUDIO_FOLDER'], audio_filename)
    print(audio_path)
    
    # Extrae el audio del video
    extract_audio_from_video(video_path, audio_path)
    
    return jsonify({'message': 'File uploaded and audio extracted', 'video_filename': filename, 'audio_filename': audio_filename}), 200

if __name__ == '__main__':
    app.run(debug=True)
