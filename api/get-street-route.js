/**
 * Vercel Serverless Function
 * Get street route using Google Maps Directions API
 *
 * This function runs on Vercel's edge network and keeps the API key secure
 */

export default async function handler(req, res) {
  console.log('🚀 [API] get-street-route called');
  console.log('   Method:', req.method);
  console.log('   Headers:', req.headers);

  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight request
  if (req.method === 'OPTIONS') {
    console.log('✅ [API] OPTIONS request handled');
    return res.status(200).end();
  }

  // Only allow POST requests
  if (req.method !== 'POST') {
    console.error('❌ [API] Invalid method:', req.method);
    return res.status(405).json({ error: 'Method not allowed. Use POST.' });
  }

  try {
    console.log('📦 [API] Request body:', req.body);
    const { waypoints } = req.body;

    // Validate input
    if (!waypoints || !Array.isArray(waypoints) || waypoints.length < 2) {
      console.error('❌ [API] Invalid waypoints:', waypoints);
      return res.status(400).json({
        error: 'Invalid waypoints. Must be an array with at least 2 points.'
      });
    }

    console.log(`✅ [API] Validated ${waypoints.length} waypoints`);

    // Get API key from environment variables (secure!)
    const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY;

    if (!GOOGLE_MAPS_API_KEY) {
      console.error('❌ [API] GOOGLE_MAPS_API_KEY not configured');
      console.error('   Available env vars:', Object.keys(process.env).filter(k => k.includes('GOOGLE')));
      return res.status(500).json({
        error: 'Server configuration error: API key missing'
      });
    }

    console.log('✅ [API] API key found (length:', GOOGLE_MAPS_API_KEY.length, ')');

    // Build Google Directions API request
    const origin = waypoints[0];
    const destination = waypoints[waypoints.length - 1];
    const waypointsMiddle = waypoints.slice(1, -1);

    console.log('📍 [API] Route details:');
    console.log('   Origin:', origin);
    console.log('   Destination:', destination);
    console.log('   Intermediate waypoints:', waypointsMiddle.length);

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

    console.log(`🌐 [API] Calling Google Maps API...`);
    console.log(`   URL: ${url.substring(0, 100)}...`);

    // Call Google Maps API
    const response = await fetch(url);
    console.log(`📥 [API] Google Maps response status: ${response.status}`);

    const data = await response.json();
    console.log(`📦 [API] Google Maps response:`, JSON.stringify(data).substring(0, 200));

    // Check for errors
    if (data.status !== 'OK') {
      console.error('❌ [API] Google Maps API error:', data.status, data.error_message);
      return res.status(500).json({
        error: `Google Maps API error: ${data.status}`,
        message: data.error_message
      });
    }

    console.log('✅ [API] Google Maps API returned OK status');

    // Extract the route
    const route = data.routes[0];

    if (!route || !route.overview_polyline) {
      console.error('❌ [API] No route found in response');
      return res.status(500).json({
        error: 'No route found'
      });
    }

    console.log('✅ [API] Route found, decoding polyline...');

    // Decode polyline to coordinates
    const encodedPolyline = route.overview_polyline.points;
    console.log(`   Encoded polyline length: ${encodedPolyline.length}`);

    const decodedCoords = decodePolyline(encodedPolyline);
    console.log(`   Decoded ${decodedCoords.length} coordinate points`);

    // Extract distance and duration
    const totalDistance = route.legs.reduce((sum, leg) => sum + leg.distance.value, 0) / 1000; // km
    const totalDuration = route.legs.reduce((sum, leg) => sum + leg.duration.value, 0) / 60; // minutes

    console.log(`✅ [API] Route calculated successfully:`);
    console.log(`   Distance: ${totalDistance.toFixed(1)} km`);
    console.log(`   Duration: ${totalDuration.toFixed(0)} min`);
    console.log(`   Points: ${decodedCoords.length}`);
    console.log(`   Summary: ${route.summary}`);

    // Return the street route
    return res.status(200).json({
      success: true,
      route: decodedCoords,
      distance: totalDistance,
      duration: totalDuration,
      summary: route.summary
    });

  } catch (error) {
    console.error('❌ [API] Unexpected error in get-street-route:');
    console.error('   Error:', error);
    console.error('   Stack:', error.stack);
    return res.status(500).json({
      error: 'Internal server error',
      message: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
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
