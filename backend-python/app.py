"""
Flask development server for Route Optimizer API
This mimics the Lambda function behavior locally for faster development
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import lambda_function

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

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
    logger.info(f"Creating Lambda event - Path: {path}, Method: {flask_request.method}")

    # Get body
    body = flask_request.get_data(as_text=True) if flask_request.data else '{}'
    body_size = len(body) if body else 0
    logger.debug(f"Request body size: {body_size} bytes")

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

    logger.debug(f"Lambda event created successfully for {path}")
    return event


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    logger.info("Health check endpoint called")

    try:
        event = create_lambda_event(request, '/api/health')
        response = lambda_function.lambda_handler(event, {})

        logger.info(f"Health check completed - Status: {response['statusCode']}")
        return jsonify(response['body']), response['statusCode']

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return jsonify({'error': 'Health check failed'}), 500


@app.route('/api/upload', methods=['POST', 'OPTIONS'])
def upload():
    """File upload endpoint"""
    if request.method == 'OPTIONS':
        logger.debug("CORS preflight request for /api/upload")
        return '', 200

    logger.info("File upload endpoint called")

    try:
        event = create_lambda_event(request, '/api/upload')
        logger.info("Processing file upload through Lambda handler")

        response = lambda_function.lambda_handler(event, {})

        import json
        body = json.loads(response['body'])

        logger.info(f"File upload completed - Status: {response['statusCode']}")
        return jsonify(body), response['statusCode']

    except Exception as e:
        logger.error(f"File upload failed: {str(e)}", exc_info=True)
        return jsonify({'error': 'File upload failed', 'message': str(e)}), 500


@app.route('/api/optimize', methods=['POST', 'OPTIONS'])
def optimize():
    """Route optimization endpoint"""
    if request.method == 'OPTIONS':
        logger.debug("CORS preflight request for /api/optimize")
        return '', 200

    logger.info("Route optimization endpoint called")

    try:
        import json
        request_data = request.get_json()
        num_locations = len(request_data.get('locations', [])) if request_data else 0
        logger.info(f"Optimizing route with {num_locations} locations")

        event = create_lambda_event(request, '/api/optimize')
        logger.info("Processing route optimization through Lambda handler")

        response = lambda_function.lambda_handler(event, {})

        body = json.loads(response['body'])

        logger.info(f"Route optimization completed - Status: {response['statusCode']}")
        if response['statusCode'] == 200:
            logger.info(f"Codigo Tilencia - Generated optimized route")

        return jsonify(body), response['statusCode']

    except Exception as e:
        logger.error(f"Route optimization failed: {str(e)}", exc_info=True)
        return jsonify({'error': 'Route optimization failed', 'message': str(e)}), 500


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

    logger.info(f"Starting Route Optimizer API on port {port} (debug={debug})")
    logger.info(f"Google Maps API: {'Configured' if os.environ.get('GOOGLE_MAPS_API_KEY') else 'Not configured'}")
    logger.info(f"AWS: {'Configured' if os.environ.get('AWS_ACCESS_KEY_ID') else 'Not configured'}")

    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server crashed: {str(e)}", exc_info=True)
