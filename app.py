"""
TubeTale Analytics - Flask Application
A narrative-driven YouTube intelligence platform powered by Google Gemini AI
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
import secrets
from services.gemini_service import analyze_channel, run_battle, analyze_video_truth

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

# Enable CORS
CORS(app)

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour


@app.route('/')
def index():
    """Homepage with three analysis modes"""
    return render_template('index.html')


@app.route('/api/analyze-channel', methods=['POST'])
def api_analyze_channel():
    """API endpoint for channel analysis"""
    try:
        data = request.get_json()
        channel_name = data.get('channelName')
        
        if not channel_name:
            return jsonify({'error': 'Channel name is required'}), 400
        
        result = analyze_channel(channel_name)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/run-battle', methods=['POST'])
def api_run_battle():
    """API endpoint for battle analysis"""
    try:
        data = request.get_json()
        channels = data.get('channels')
        
        if not channels or not isinstance(channels, list):
            return jsonify({'error': 'Channels array is required'}), 400
        
        if len(channels) < 2 or len(channels) > 5:
            return jsonify({'error': 'Please provide 2-5 channels'}), 400
        
        # Extract channel names from the data
        channel_names = [ch['channelName'] if isinstance(ch, dict) else ch for ch in channels]
        
        result = run_battle(channel_names)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze-truth', methods=['POST'])
def api_analyze_truth():
    """API endpoint for video truth analysis"""
    try:
        data = request.get_json()
        video_input = data.get('videoInput')
        
        if not video_input:
            return jsonify({'error': 'Video URL is required'}), 400
        
        result = analyze_video_truth(video_input)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Check if API key is configured
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('VITE_GEMINI_API_KEY')
    if not api_key:
        print("WARNING: GEMINI_API_KEY not found in environment variables!")
        print("Please set GEMINI_API_KEY in your .env file")
    
    # Run development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
