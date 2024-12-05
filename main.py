import os
import subprocess
from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)

# Configuration
RTSP_URL = "rtsp://admin:OINVHA@192.168.1.171:554/ch1/main"
HLS_FOLDER = "hls_stream"
HLS_PLAYLIST = "superindex.m3u8"  # Updated to match your HTML file
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset=utf-8 />
<title>HLS</title>
<link href="https://unpkg.com/video.js/dist/video-js.css" rel="stylesheet">
<style>
.center {
margin-left: auto;
margin-right: auto;
display: block
}
</style>
</head>
<body>
<div>
<h2>Streaming video using HLS - m3u8 manifest file</h2>
</div>
<video-js id="hlsplayer" class="vjs-default-skin center" controls preload="auto" width="720"
height="400" controls>
<source id="hlsSource" type="application/x-mpegURL">
</video-js>
<script type="text/javascript">
document.getElementById("hlsSource").setAttribute("src", "http://" + location.host +
"/hls/{{ playlist }}");
</script>
<script src="https://unpkg.com/video.js/dist/video.js"></script>
<script src="https://unpkg.com/@videojs/http-streaming/dist/videojs-http-streaming.js"></script>
<script>
var player = videojs('hlsplayer');
</script>
</body>
</html>
"""

# Ensure the HLS folder exists
os.makedirs(HLS_FOLDER, exist_ok=True)


def start_ffmpeg_stream():
    """Start FFmpeg process to convert RTSP to HLS."""
    ffmpeg_command = [
        "ffmpeg",
        "-i", RTSP_URL,  # Input from RTSP
        "-c:v", "libx264",  # Video codec
        "-preset", "veryfast",  # Encoding speed
        "-g", "50",  # GOP size
        "-sc_threshold", "0",
        "-f", "hls",  # HLS output format
        "-hls_time", "4",  # Segment duration
        "-hls_list_size", "5",  # Number of segments in playlist
        "-hls_flags", "delete_segments",  # Remove old segments
        f"{HLS_FOLDER}/{HLS_PLAYLIST}"  # Output HLS files
    ]

    return subprocess.Popen(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


@app.route('/')
def index():
    """Serve the HTML template."""
    return render_template_string(HTML_TEMPLATE, playlist=HLS_PLAYLIST)


@app.route('/hls/<path:filename>')
def stream_hls(filename):
    """Serve HLS files."""
    return send_from_directory(HLS_FOLDER, filename)


if __name__ == "__main__":
    # Start FFmpeg process
    ffmpeg_process = start_ffmpeg_stream()

    try:
        # Start Flask server
        app.run(host="0.0.0.0", port=8080, debug=True)
    except KeyboardInterrupt:
        print("Stopping stream...")
        ffmpeg_process.terminate()
