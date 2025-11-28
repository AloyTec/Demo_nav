"""
Flask development server for Route Optimizer API
This mimics the Lambda function behavior locally for faster development
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import lambda_function

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
    }
})


def create_lambda_event(flask_request, path):
    """Convert Flask request to Lambda event format"""

    # Get body
    body = flask_request.get_data(as_text=True) if flask_request.data else '{}'

    # Create Lambda event structure
    event = {
        'rawPath': path,
        'requestContext': {
            'http': {
                'method': flask_request.method
            }
        },
        'body': body,
        'isBase64Encoded': False
    }

    return event


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    event = create_lambda_event(request, '/api/health')
    response = lambda_function.lambda_handler(event, {})

    return jsonify(response['body']), response['statusCode']


@app.route('/api/upload', methods=['POST', 'OPTIONS'])
def upload():
    """File upload endpoint"""
    if request.method == 'OPTIONS':
        return '', 200

    event = create_lambda_event(request, '/api/upload')
    response = lambda_function.lambda_handler(event, {})

    import json
    body = json.loads(response['body'])
    return jsonify(body), response['statusCode']


@app.route('/api/optimize', methods=['POST', 'OPTIONS'])
def optimize():
    """Route optimization endpoint"""
    if request.method == 'OPTIONS':
        return '', 200

    event = create_lambda_event(request, '/api/optimize')
    response = lambda_function.lambda_handler(event, {})

    import json
    body = json.loads(response['body'])
    return jsonify(body), response['statusCode']


@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'name': 'Route Optimizer API',
        'version': '1.0.0',
        'status': 'running',
        'mode': 'development',
        'endpoints': {
            'health': '/api/health',
            'upload': '/api/upload',
            'optimize': '/api/optimize'
        }
    })


if __name__ == '__main__':
    # Get configuration from environment
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'

    print("=" * 60)
    print("🚀 Route Optimizer API - Development Server")
    print("=" * 60)
    print(f"📍 Running on: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🗺️  Google Maps API: {'✅ Configured' if os.environ.get('GOOGLE_MAPS_API_KEY') else '❌ Not configured'}")
    print(f"☁️  AWS Configured: {'✅ Yes' if os.environ.get('AWS_ACCESS_KEY_ID') else '❌ No'}")
    print("=" * 60)
    print("\n📚 Available endpoints:")
    print("  • GET  http://localhost:{}/".format(port))
    print("  • GET  http://localhost:{}/api/health".format(port))
    print("  • POST http://localhost:{}/api/upload".format(port))
    print("  • POST http://localhost:{}/api/optimize".format(port))
    print("\n⌨️  Press Ctrl+C to stop\n")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
