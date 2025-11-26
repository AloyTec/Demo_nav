/**
 * Vercel Serverless Function
 * Get street route using Google Maps Directions API
 *
 * This function runs on Vercel's edge network and keeps the API key secure
 */

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight request
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed. Use POST.' });
  }

  try {
    const { waypoints } = req.body;

    // Validate input
    if (!waypoints || !Array.isArray(waypoints) || waypoints.length < 2) {
      return res.status(400).json({
        error: 'Invalid waypoints. Must be an array with at least 2 points.'
      });
    }

    // Get API key from environment variables (secure!)
    const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY;

    if (!GOOGLE_MAPS_API_KEY) {
      console.error('GOOGLE_MAPS_API_KEY not configured');
      return res.status(500).json({
        error: 'Server configuration error: API key missing'
      });
    }

    // Build Google Directions API request
    const origin = waypoints[0];
    const destination = waypoints[waypoints.length - 1];
    const waypointsMiddle = waypoints.slice(1, -1);

    // Construct URL for Google Directions API
    const params = new URLSearchParams({
      origin: `${origin.lat},${origin.lng}`,
      destination: `${destination.lat},${destination.lng}`,
      mode: 'driving',
      key: GOOGLE_MAPS_API_KEY,
      language: 'es',
      region: 'CL' // Chile
    });

    // Add intermediate waypoints if any
    if (waypointsMiddle.length > 0) {
      const waypointsStr = waypointsMiddle
        .map(w => `${w.lat},${w.lng}`)
        .join('|');
      params.append('waypoints', `optimize:false|${waypointsStr}`);
    }

    const url = `https://maps.googleapis.com/maps/api/directions/json?${params.toString()}`;

    console.log(`Fetching route for ${waypoints.length} waypoints...`);

    // Call Google Maps API
    const response = await fetch(url);
    const data = await response.json();

    // Check for errors
    if (data.status !== 'OK') {
      console.error('Google Maps API error:', data.status, data.error_message);
      return res.status(500).json({
        error: `Google Maps API error: ${data.status}`,
        message: data.error_message
      });
    }

    // Extract the route
    const route = data.routes[0];

    if (!route || !route.overview_polyline) {
      return res.status(500).json({
        error: 'No route found'
      });
    }

    // Decode polyline to coordinates
    const encodedPolyline = route.overview_polyline.points;
    const decodedCoords = decodePolyline(encodedPolyline);

    // Extract distance and duration
    const totalDistance = route.legs.reduce((sum, leg) => sum + leg.distance.value, 0) / 1000; // km
    const totalDuration = route.legs.reduce((sum, leg) => sum + leg.duration.value, 0) / 60; // minutes

    console.log(`✓ Route calculated: ${totalDistance.toFixed(1)} km, ${totalDuration.toFixed(0)} min`);

    // Return the street route
    return res.status(200).json({
      success: true,
      route: decodedCoords,
      distance: totalDistance,
      duration: totalDuration,
      summary: route.summary
    });

  } catch (error) {
    console.error('Error in get-street-route:', error);
    return res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
}

/**
 * Decode Google Maps polyline encoding
 * Algorithm: https://developers.google.com/maps/documentation/utilities/polylinealgorithm
 */
function decodePolyline(encoded) {
  const points = [];
  let index = 0;
  const len = encoded.length;
  let lat = 0;
  let lng = 0;

  while (index < len) {
    let shift = 0;
    let result = 0;
    let byte;

    // Decode latitude
    do {
      byte = encoded.charCodeAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20);

    const deltaLat = ((result & 1) ? ~(result >> 1) : (result >> 1));
    lat += deltaLat;

    shift = 0;
    result = 0;

    // Decode longitude
    do {
      byte = encoded.charCodeAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20);

    const deltaLng = ((result & 1) ? ~(result >> 1) : (result >> 1));
    lng += deltaLng;

    points.push({
      lat: lat / 1e5,
      lng: lng / 1e5
    });
  }

  return points;
}
