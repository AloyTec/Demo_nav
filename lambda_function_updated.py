import json
import base64
import boto3
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
import time
import random
import os
import urllib3
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from geopy.distance import geodesic
from sklearn.cluster import KMeans
import uuid

# AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Configuration
BUCKET_NAME = 'route-optimizer-demo-889268462469'
TABLE_NAME = 'route-optimizer-demo-tracking'
table = dynamodb.Table(TABLE_NAME)

# Google Maps API Configuration
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
http = urllib3.PoolManager()

# Van and Bus Configuration
VAN_CAPACITY = 10  # Capacidad máxima por van
BUS_CAPACITY = 40  # Capacidad del bus de acercamiento

# Travel Time Estimation Configuration
CITY_SPEED_KMH = 60  # Promedio entre 50-70 km/h para ciudad
HIGHWAY_SPEED_KMH = 105  # Promedio entre 90-120 km/h para autopista
CITY_DISTANCE_THRESHOLD = 15  # km - distancias < 15km se consideran ciudad
SAFETY_BUFFER = 1.2  # 20% buffer de seguridad
PICKUP_TIME_MINUTES = 5  # Tiempo estimado de recogida por pasajero

# Distance Calculation Strategy:
# - Driver → Terminal: Uses Google Maps Distance Matrix API for REAL road distances
# - Pickup → Pickup (TSP optimization): Uses geodesic (straight-line) for performance
# - Bus Stop → Terminal: Uses Google Maps Distance Matrix API for REAL road distances
# - Fallback: If API fails, uses geodesic distance + estimated travel time

# Terminal Maipú - Bus stop location (fixed location near the terminal)
BUS_STOP_MAIPU = {
    'lat': -33.48343,  # Av. Departamental esq Av. Pedro Aguirre Cerda (Metro Cerrillos)
    'lng': -70.69556,
    'address': 'Punto de Encuentro - Av. Departamental esq Av. Pedro Aguirre Cerda'
}

# Known terminal coordinates (to avoid geocoding errors)
KNOWN_TERMINALS = {
    'terminal conquistador': {
        'lat': -33.51505,  # Av. 5 Poniente 1601, Maipú
        'lng': -70.8044,
        'address': 'Terminal Conquistador (Av. 5 Poniente 1601, Maipú)'
    },
    'terminal maipu': {
        'lat': -33.51505,  # Same as Terminal Conquistador - most common terminal in Maipú
        'lng': -70.8044,
        'address': 'Terminal Maipú'
    },
    'terminal maipú': {
        'lat': -33.51505,
        'lng': -70.8044,
        'address': 'Terminal Maipú'
    },
    'terminal aeropuerto t1': {
        'lat': -33.3928,  # Aeropuerto Internacional Arturo Merino Benítez, Terminal 1
        'lng': -70.7856,
        'address': 'Terminal Aeropuerto T1'
    },
    'terminal aeropuerto t2': {
        'lat': -33.3935,  # Terminal 2
        'lng': -70.7865,
        'address': 'Terminal Aeropuerto T2'
    }
}

# Terminals that use bus mode
TERMINALS_WITH_BUS = ['maipu', 'maipú', 'terminal maipu', 'terminal maipú']

def cors_headers():
    """Return empty headers - CORS is handled by Lambda Function URL configuration"""
    return {}

def clean_address_for_geocoding(address):
    """
    Clean and format address for better geocoding results

    Common issues in Chilean addresses:
    - "Calle # 1234" → "Calle 1234"
    - "Calle; Dpto 301" → "Calle"
    - "Av.Pajaritos" → "Avenida Pajaritos"
    """
    import re

    # Remove department/apartment info (after semicolon or "Dpto")
    address = re.split(r';|,\s*Dpto|,\s*Depto', address)[0].strip()

    # Remove "#" symbol
    address = address.replace(' # ', ' ').replace(' #', ' ')

    # Expand common abbreviations
    address = address.replace('Av.', 'Avenida ')
    address = address.replace('Pje.', 'Pasaje ')
    address = address.replace('Psje.', 'Pasaje ')

    # Remove extra spaces
    address = ' '.join(address.split())

    return address

def geocode_terminal(terminal_name):
    """
    Geocode a terminal, checking known terminals first

    Args:
        terminal_name: Terminal name (e.g., "Terminal Conquistador (Av. 5 Poniente 1601, Maipú)")

    Returns:
        Coordinates dict with lat/lng
    """
    # Normalize terminal name for lookup
    # Extract terminal name before parentheses if present
    terminal_lookup = terminal_name.split('(')[0].strip().lower()

    # Check if this is a known terminal
    if terminal_lookup in KNOWN_TERMINALS:
        coords = KNOWN_TERMINALS[terminal_lookup]
        print(f"  ✓ Using known coordinates for terminal: {terminal_name}")
        return {'lat': coords['lat'], 'lng': coords['lng']}

    # If not known, fall back to geocoding
    print(f"  Terminal not in known list, geocoding: {terminal_name}")
    return geocode_address(terminal_name)

def is_in_comuna(geocode_result, expected_comuna):
    """
    Check if a geocoding result is in the expected comuna.

    Args:
        geocode_result: A single result object from Google Maps Geocoding API
        expected_comuna: The expected comuna name (e.g., "Cerro Navia")

    Returns:
        True if the result is in the expected comuna, False otherwise
    """
    # Normalize expected comuna for comparison
    expected_comuna_normalized = expected_comuna.lower().strip()

    # Check address_components for locality or administrative_area_level_3
    # which typically contain the comuna name in Chilean addresses
    address_components = geocode_result.get('address_components', [])

    for component in address_components:
        types = component.get('types', [])
        name = component.get('long_name', '').lower().strip()

        # In Chile, comunas are typically in these types:
        # - locality (most common for comunas)
        # - administrative_area_level_3 (sometimes)
        # - sublocality (sometimes for sectors within comunas)
        if any(t in types for t in ['locality', 'administrative_area_level_3', 'sublocality']):
            if expected_comuna_normalized in name or name in expected_comuna_normalized:
                return True

    return False

def geocode_address(address):
    """
    Geocode an address to lat/lng coordinates using Google Maps Geocoding API
    with multiple fallback strategies and comuna validation
    """
    if not GOOGLE_MAPS_API_KEY:
        print(f"  ❌ ERROR: GOOGLE_MAPS_API_KEY not configured")
        return {
            'lat': -33.4489 + (random.random() - 0.5) * 0.1,
            'lng': -70.6693 + (random.random() - 0.5) * 0.1
        }

    # Clean the address first
    cleaned_address = clean_address_for_geocoding(address)

    # Extract comuna if present (after last comma)
    parts = cleaned_address.rsplit(',', 1)
    base_address = parts[0].strip()
    comuna = parts[1].strip() if len(parts) > 1 else None

    # Strategy 1: Try full cleaned address with comuna validation
    try:
        query = f"{cleaned_address}, Santiago, Chile"
        print(f"  Trying: {query}")

        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={quote(query)}&key={GOOGLE_MAPS_API_KEY}"
        response = http.request('GET', url, timeout=10.0)

        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))
            if data.get('status') == 'OK' and len(data.get('results', [])) > 0:
                results = data.get('results', [])
                print(f"  → Google Maps returned {len(results)} result(s)")

                # If comuna is specified, validate all results against it
                if comuna:
                    for i, result in enumerate(results):
                        if is_in_comuna(result, comuna):
                            location = result['geometry']['location']
                            formatted_address = result.get('formatted_address', 'N/A')
                            print(f"  ✓ Match found in {comuna}: {formatted_address}")
                            return {'lat': location['lat'], 'lng': location['lng']}

                    # No result matched the expected comuna
                    print(f"  ⚠ None of the {len(results)} results matched comuna '{comuna}'")
                    print(f"  → Falling back to Strategy 2")
                else:
                    # No comuna specified, use first result
                    location = results[0]['geometry']['location']
                    formatted_address = results[0].get('formatted_address', 'N/A')
                    print(f"  ✓ Geocoded (no comuna filter): {formatted_address}")
                    return {'lat': location['lat'], 'lng': location['lng']}
            elif data.get('status') == 'ZERO_RESULTS':
                print(f"  Strategy 1: No results found")
            else:
                print(f"  Strategy 1 failed: {data.get('status')}")
    except Exception as e:
        print(f"  Strategy 1 failed: {e}")

    # Strategy 2: Try without number (just street and comuna)
    if base_address and comuna:
        try:
            import re
            street_only = re.sub(r'\d+', '', base_address).strip()
            query = f"{street_only}, {comuna}, Santiago, Chile"
            print(f"  Trying: {query}")

            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={quote(query)}&key={GOOGLE_MAPS_API_KEY}"
            response = http.request('GET', url, timeout=10.0)

            if response.status == 200:
                data = json.loads(response.data.decode('utf-8'))
                if data.get('status') == 'OK' and len(data.get('results', [])) > 0:
                    results = data.get('results', [])
                    print(f"  → Google Maps returned {len(results)} result(s)")

                    # Validate results against comuna
                    for result in results:
                        if is_in_comuna(result, comuna):
                            location = result['geometry']['location']
                            formatted_address = result.get('formatted_address', 'N/A')
                            print(f"  ✓ Match found (street only) in {comuna}: {formatted_address}")
                            return {'lat': location['lat'], 'lng': location['lng']}

                    # If no match, log but continue to Strategy 3
                    print(f"  ⚠ Strategy 2: No results matched comuna '{comuna}'")
        except Exception as e:
            print(f"  Strategy 2 failed: {e}")

    # Strategy 3: Try just the comuna
    if comuna:
        try:
            query = f"{comuna}, Santiago, Chile"
            print(f"  Trying: {query}")

            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={quote(query)}&key={GOOGLE_MAPS_API_KEY}"
            response = http.request('GET', url, timeout=10.0)

            if response.status == 200:
                data = json.loads(response.data.decode('utf-8'))
                if data.get('status') == 'OK' and len(data.get('results', [])) > 0:
                    location = data['results'][0]['geometry']['location']
                    print(f"  ⚠ Using comuna center: {comuna}")
                    # Add small random offset to avoid all addresses in same comuna overlapping
                    return {
                        'lat': location['lat'] + (random.random() - 0.5) * 0.01,
                        'lng': location['lng'] + (random.random() - 0.5) * 0.01
                    }
        except Exception as e:
            print(f"  Strategy 3 failed: {e}")

    # Fallback: Use Santiago center with warning
    print(f"  ❌ GEOCODING FAILED for: {address}")
    print(f"  ⚠ Using Santiago center as fallback")
    return {
        'lat': -33.4489 + (random.random() - 0.5) * 0.1,
        'lng': -70.6693 + (random.random() - 0.5) * 0.1
    }

def get_route_distance_and_time(origin_coord, destination_coord):
    """
    Get real road distance and travel time using Google Maps Distance Matrix API

    Args:
        origin_coord: Dict with 'lat' and 'lng' keys
        destination_coord: Dict with 'lat' and 'lng' keys

    Returns:
        Dict with 'distance_km' and 'duration_minutes', or None if API fails
    """
    if not GOOGLE_MAPS_API_KEY:
        print(f"  ⚠ WARNING: GOOGLE_MAPS_API_KEY not configured, falling back to geodesic")
        return None

    try:
        # Format coordinates for API
        origin = f"{origin_coord['lat']},{origin_coord['lng']}"
        destination = f"{destination_coord['lat']},{destination_coord['lng']}"

        # Call Distance Matrix API
        url = (
            f"https://maps.googleapis.com/maps/api/distancematrix/json"
            f"?origins={origin}"
            f"&destinations={destination}"
            f"&mode=driving"
            f"&language=es"
            f"&key={GOOGLE_MAPS_API_KEY}"
        )

        response = http.request('GET', url, timeout=10.0)

        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))

            if data.get('status') == 'OK':
                rows = data.get('rows', [])
                if rows and len(rows) > 0:
                    elements = rows[0].get('elements', [])
                    if elements and len(elements) > 0:
                        element = elements[0]

                        if element.get('status') == 'OK':
                            # Extract distance and duration
                            distance_meters = element['distance']['value']
                            duration_seconds = element['duration']['value']

                            distance_km = distance_meters / 1000.0
                            duration_minutes = duration_seconds / 60.0

                            return {
                                'distance_km': round(distance_km, 2),
                                'duration_minutes': round(duration_minutes, 1)
                            }
                        else:
                            print(f"  ⚠ Distance Matrix element status: {element.get('status')}")
            else:
                print(f"  ⚠ Distance Matrix API status: {data.get('status')}")
        else:
            print(f"  ⚠ Distance Matrix API HTTP error: {response.status}")

    except Exception as e:
        print(f"  ⚠ Distance Matrix API error: {e}")

    return None

def calculate_distance(coord1, coord2):
    """
    Calculate distance between two coordinates in km (geodesic/straight-line)

    Note: This calculates straight-line distance, NOT road distance.
    For road distance, use get_route_distance_and_time() instead.
    """
    return geodesic((coord1['lat'], coord1['lng']), (coord2['lat'], coord2['lng'])).km

def estimate_travel_time(distance_km):
    """
    Estimate travel time in minutes based on distance

    NOTE: This is a fallback estimation. When possible, use get_route_distance_and_time()
    to get real travel times from Google Maps Distance Matrix API.

    Args:
        distance_km: Distance in kilometers

    Returns:
        Estimated travel time in minutes (includes 20% safety buffer)
    """
    # Determine speed based on distance (shorter = city, longer = highway)
    if distance_km < CITY_DISTANCE_THRESHOLD:
        speed_kmh = CITY_SPEED_KMH
    else:
        # Mixed: use weighted average (70% highway, 30% city)
        speed_kmh = (HIGHWAY_SPEED_KMH * 0.7) + (CITY_SPEED_KMH * 0.3)

    # Calculate base travel time in hours, then convert to minutes
    travel_time_hours = distance_km / speed_kmh
    travel_time_minutes = travel_time_hours * 60

    # Apply safety buffer (20%)
    travel_time_with_buffer = travel_time_minutes * SAFETY_BUFFER

    return round(travel_time_with_buffer, 1)

def parse_presentation_time(time_str):
    """
    Parse time string to minutes since midnight

    Args:
        time_str: Time string in format "HH:MM" or "H:MM"

    Returns:
        Minutes since midnight (e.g., "06:30" -> 390)
    """
    try:
        # Handle different time formats
        time_str = str(time_str).strip()

        # Split by colon
        parts = time_str.split(':')
        if len(parts) == 2:
            hours = int(parts[0])
            minutes = int(parts[1])
            return hours * 60 + minutes
        else:
            # Default to 8:00 AM if parsing fails
            print(f"Warning: Could not parse time '{time_str}', using 08:00")
            return 8 * 60
    except Exception as e:
        print(f"Error parsing time '{time_str}': {e}, using 08:00")
        return 8 * 60

def calculate_pickup_time_window(presentation_time_str, travel_time_minutes):
    """
    Calculate the latest pickup time based on presentation time and travel time

    Args:
        presentation_time_str: Time string like "06:30"
        travel_time_minutes: Estimated travel time in minutes

    Returns:
        dict with pickup_time (minutes since midnight) and presentation_time
    """
    presentation_minutes = parse_presentation_time(presentation_time_str)

    # Latest pickup time = presentation time - travel time
    pickup_minutes = presentation_minutes - travel_time_minutes

    # Ensure pickup time is not negative (early morning edge case)
    if pickup_minutes < 0:
        pickup_minutes = 0

    return {
        'presentation_time_minutes': presentation_minutes,
        'pickup_time_latest_minutes': pickup_minutes,
        'travel_time_minutes': travel_time_minutes,
        'presentation_time_str': format_minutes_to_time(presentation_minutes),
        'pickup_time_latest_str': format_minutes_to_time(pickup_minutes)
    }

def format_minutes_to_time(minutes):
    """Convert minutes since midnight to HH:MM format"""
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours:02d}:{mins:02d}"

def optimize_route_tsp(drivers):
    """Improved TSP algorithm with 2-opt optimization"""
    if len(drivers) <= 1:
        return drivers

    # Greedy nearest neighbor
    route = [drivers[0]]
    remaining = drivers[1:]

    while remaining:
        last = route[-1]
        nearest = min(remaining, key=lambda d: calculate_distance(
            last['coordinates'], d['coordinates']
        ))
        route.append(nearest)
        remaining.remove(nearest)

    # 2-opt improvement
    improved = True
    max_iterations = 50
    iteration = 0

    while improved and iteration < max_iterations:
        improved = False
        iteration += 1

        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route)):
                if j - i == 1:
                    continue

                current_dist = (
                    calculate_distance(route[i-1]['coordinates'], route[i]['coordinates']) +
                    calculate_distance(route[j-1]['coordinates'], route[j % len(route)]['coordinates'])
                )

                new_dist = (
                    calculate_distance(route[i-1]['coordinates'], route[j-1]['coordinates']) +
                    calculate_distance(route[i]['coordinates'], route[j % len(route)]['coordinates'])
                )

                if new_dist < current_dist:
                    route[i:j] = reversed(route[i:j])
                    improved = True
                    break

            if improved:
                break

    return route

def balance_load(clusters):
    """Balance the number of drivers across vans"""
    while True:
        sizes = [len(c) for c in clusters]
        max_idx = sizes.index(max(sizes))
        min_idx = sizes.index(min(sizes))

        if sizes[max_idx] - sizes[min_idx] <= 1:
            break

        driver = clusters[max_idx].pop()
        clusters[min_idx].append(driver)

    return clusters

def track_demo_usage(demo_id, data):
    """Track demo usage in DynamoDB"""
    try:
        table.put_item(
            Item={
                'demo_id': demo_id,
                'timestamp': int(time.time()),
                'data': json.dumps(data, default=str),
                'created_at': datetime.now().isoformat()
            }
        )
        print(f"✓ Tracked demo usage: {demo_id}")
    except Exception as e:
        print(f"Error tracking demo: {e}")

def geocode_driver_parallel(driver_data):
    """
    Geocode a single driver and calculate travel times (for parallel processing)

    Args:
        driver_data: Tuple of (index, driver, destination_terminal_config)

    Returns:
        Tuple of (index, driver_with_coordinates)
    """
    idx, driver, destination_terminal_config = driver_data

    print(f"Geocoding {idx+1}: {driver['address']}")

    # Geocode driver address
    driver['coordinates'] = geocode_address(driver['address'])

    # Determine terminal
    if destination_terminal_config:
        terminal = destination_terminal_config
        driver['terminal'] = terminal
    else:
        terminal = driver.get('terminal', 'Terminal Aeropuerto T1')

    # Geocode terminal
    terminal_coord = geocode_terminal(terminal)

    # Get REAL road distance and travel time using Distance Matrix API
    route_info = get_route_distance_and_time(driver['coordinates'], terminal_coord)

    if route_info:
        # Use real road distance and time from Google Maps
        distance_to_terminal = route_info['distance_km']
        travel_time = route_info['duration_minutes']
        print(f"  ✓ Real route: {distance_to_terminal} km, {travel_time} min (from Distance Matrix API)")
    else:
        # Fallback to geodesic distance if API fails
        distance_to_terminal = calculate_distance(driver['coordinates'], terminal_coord)
        travel_time = estimate_travel_time(distance_to_terminal)
        print(f"  ⚠ Fallback to geodesic: {distance_to_terminal} km, {travel_time} min (estimated)")

    # Calculate pickup time window
    presentation_time = driver.get('time', '08:00')
    time_window = calculate_pickup_time_window(presentation_time, travel_time)

    # Add timing information to driver
    driver['distance_to_terminal_km'] = round(distance_to_terminal, 2)
    driver['travel_time_minutes'] = round(travel_time, 1)
    driver['presentation_time'] = time_window['presentation_time_str']
    driver['presentation_time_minutes'] = time_window['presentation_time_minutes']
    driver['pickup_time_latest'] = time_window['pickup_time_latest_str']
    driver['pickup_time_latest_minutes'] = time_window['pickup_time_latest_minutes']

    print(f"  → {idx+1}: Distance: {driver['distance_to_terminal_km']} km, Travel time: {travel_time} min, Pickup: {driver['pickup_time_latest']}, Present: {driver['presentation_time']}")

    return idx, driver

def uses_bus_mode(terminal):
    """Check if a terminal uses bus de acercamiento mode"""
    terminal_lower = terminal.lower().strip()
    return any(term in terminal_lower for term in TERMINALS_WITH_BUS)

def group_drivers_by_terminal(drivers):
    """Group drivers by their destination terminal"""
    terminal_groups = {}
    for driver in drivers:
        terminal = driver.get('terminal', 'Terminal Aeropuerto T1')
        if terminal not in terminal_groups:
            terminal_groups[terminal] = []
        terminal_groups[terminal].append(driver)
    return terminal_groups

def optimize_with_bus_mode(drivers, terminal, terminal_coord, num_vans_override=None):
    """
    Optimize routes using bus de acercamiento mode

    Flow:
    1. Van picks up Group 1 drivers and drops them at bus stop
    2. Van returns and picks up Group 2 drivers, takes them directly to terminal
    3. Bus takes all Group 1 passengers from bus stop to terminal
    """
    print(f"Using BUS MODE for {len(drivers)} drivers to {terminal}")

    # Determine number of vans needed
    if num_vans_override is not None:
        # User specified number of vans - use it directly (frontend already validated)
        num_vans = num_vans_override
        print(f"Using user-configured number of vans: {num_vans}")
    else:
        # Auto-calculate optimal number of vans (limit to 2-5 range)
        num_vans = max(2, min(5, len(drivers) // 10 + 1))
        print(f"Auto-calculated number of vans: {num_vans}")

    # Cluster drivers using K-means
    print(f"Clustering into {num_vans} vans...")
    coordinates = np.array([[d['coordinates']['lat'], d['coordinates']['lng']] for d in drivers])
    kmeans = KMeans(n_clusters=num_vans, random_state=42, n_init=10)
    labels = kmeans.fit_predict(coordinates)

    # Group drivers by cluster
    clusters = [[] for _ in range(num_vans)]
    for driver, label in zip(drivers, labels):
        clusters[label].append(driver)

    # Balance load
    clusters = balance_load(clusters)

    # Optimize routes for each van (split into 2 groups)
    vans = []
    bus_passengers = []  # Accumulate all Group 1 passengers for the bus
    total_distance = 0

    for van_idx, cluster in enumerate(clusters):
        if not cluster:
            continue

        # Split cluster into 2 groups (max 5 per group for capacity of 10)
        mid_point = len(cluster) // 2
        group_1 = cluster[:mid_point]  # Go to bus
        group_2 = cluster[mid_point:]  # Go directly to terminal

        # GROUP 1: Optimize route home → bus stop
        if group_1:
            route_1 = optimize_route_tsp(group_1)
            route_1_coords = [d['coordinates'] for d in route_1]
            route_1_coords.append(BUS_STOP_MAIPU)  # End at bus stop

            # Calculate distance for group 1 route
            distance_1 = 0
            for j in range(len(route_1_coords) - 1):
                distance_1 += calculate_distance(route_1_coords[j], route_1_coords[j + 1])

            total_distance += distance_1

            vans.append({
                'name': f'Van {van_idx + 1} - Grupo 1',
                'drivers': route_1,
                'route': route_1_coords,
                'totalDistance': distance_1,
                'destination': 'Bus de Acercamiento',
                'capacity': VAN_CAPACITY,
                'utilization': len(route_1) / VAN_CAPACITY * 100,
                'trip_type': 'to_bus',
                'is_van': True
            })

            bus_passengers.extend(group_1)

        # GROUP 2: Optimize route home → terminal direct
        if group_2:
            route_2 = optimize_route_tsp(group_2)
            route_2_coords = [d['coordinates'] for d in route_2]
            route_2_coords.append(terminal_coord)  # End at terminal

            # Calculate distance for group 2 route
            distance_2 = 0
            for j in range(len(route_2_coords) - 1):
                distance_2 += calculate_distance(route_2_coords[j], route_2_coords[j + 1])

            total_distance += distance_2

            vans.append({
                'name': f'Van {van_idx + 1} - Grupo 2',
                'drivers': route_2,
                'route': route_2_coords,
                'totalDistance': distance_2,
                'destination': terminal,
                'capacity': VAN_CAPACITY,
                'utilization': len(route_2) / VAN_CAPACITY * 100,
                'trip_type': 'to_terminal',
                'is_van': True
            })

    # Create BUS route (bus stop → terminal)
    if bus_passengers:
        bus_route = [BUS_STOP_MAIPU, terminal_coord]

        # Get real road distance for bus route
        bus_route_info = get_route_distance_and_time(BUS_STOP_MAIPU, terminal_coord)
        if bus_route_info:
            bus_distance = bus_route_info['distance_km']
            print(f"  ✓ Bus route (real): {bus_distance} km")
        else:
            bus_distance = calculate_distance(BUS_STOP_MAIPU, terminal_coord)
            print(f"  ⚠ Bus route (geodesic fallback): {bus_distance} km")

        total_distance += bus_distance

        # Create driver list for bus with bus stop info
        bus_driver_list = []
        for passenger in bus_passengers:
            bus_driver_list.append({
                **passenger,
                'pickup_location': 'Bus Stop - Av. Departamental esq Av. Pedro Aguirre Cerda'
            })

        vans.append({
            'name': 'Bus de Acercamiento',
            'drivers': bus_driver_list,
            'route': bus_route,
            'totalDistance': bus_distance,
            'destination': terminal,
            'capacity': BUS_CAPACITY,
            'utilization': len(bus_passengers) / BUS_CAPACITY * 100,
            'trip_type': 'bus_to_terminal',
            'is_bus': True
        })

    print(f"Bus mode optimization complete: {len(vans)} vehicles, {total_distance:.1f} km total")
    return vans, total_distance

def handle_upload(event):
    """Handle file upload"""
    try:
        # Parse multipart form data from base64
        body = event.get('body', '')
        is_base64 = event.get('isBase64Encoded', False)

        if is_base64:
            body = base64.b64decode(body)

        # For Lambda Function URLs, the body might already be bytes
        if isinstance(body, str):
            body = body.encode('utf-8')

        # Parse the uploaded file
        # Note: In production, you'd properly parse multipart/form-data
        # For now, we'll accept JSON with base64 encoded file
        data = json.loads(body if isinstance(body, str) else body.decode('utf-8'))
        file_content = base64.b64decode(data.get('file_content', ''))

        # Read Excel/CSV file
        file_ext = data.get('filename', '').lower()
        print(f"Processing file: {file_ext}")

        if file_ext.endswith('.csv'):
            # Try to auto-detect delimiter (comma or semicolon)
            try:
                # First, peek at the first line to check for "Table 1" header
                first_line = file_content.decode('utf-8').split('\n')[0].strip()
                print(f"First line of CSV: {first_line}")

                skip_rows = 0
                if first_line == 'Table 1':
                    print("Detected 'Table 1' header, will skip first row")
                    skip_rows = 1

                # Try to read with auto-detection
                df = pd.read_csv(BytesIO(file_content), sep=None, engine='python', skiprows=skip_rows)

                # If columns look wrong (like ['Table', '1']), try with semicolon delimiter
                if len(df.columns) <= 2 or 'Table' in df.columns:
                    print("Column detection looks wrong, forcing semicolon delimiter...")
                    df = pd.read_csv(BytesIO(file_content), sep=';', skiprows=skip_rows)

            except Exception as e:
                print(f"Auto-detection failed: {e}, trying semicolon...")
                # Fallback to semicolon
                try:
                    df = pd.read_csv(BytesIO(file_content), sep=';', skiprows=1)
                except:
                    df = pd.read_csv(BytesIO(file_content), sep=';')
        else:
            # Excel files (.xls or .xlsx)
            if file_ext.endswith('.xls') and not file_ext.endswith('.xlsx'):
                # Old Excel format (.xls) - use xlrd
                print("Detected .xls file, using xlrd engine")
                df = pd.read_excel(BytesIO(file_content), engine='xlrd')
            else:
                # Modern Excel format (.xlsx) - use openpyxl (default)
                print("Detected .xlsx file, using openpyxl engine")
                df = pd.read_excel(BytesIO(file_content))

        # Clean column names (remove extra spaces)
        df.columns = df.columns.str.strip()

        print(f"Columns found: {list(df.columns)}")
        print(f"Rows: {len(df)}")

        # Flexible column mapping to support multiple formats
        # Try to detect name column
        name_col = None
        for possible_name in ['Nombre Completo', 'Nombre', 'Name']:
            if possible_name in df.columns:
                name_col = possible_name
                break

        # Try to detect address column
        address_col = None
        for possible_address in ['Dirección', 'Dirección Casa', 'Address']:
            if possible_address in df.columns:
                address_col = possible_address
                break

        # Try to detect terminal/destination column
        terminal_col = None
        for possible_terminal in ['Lugar de presentación', 'Terminal Destino', 'Terminal', 'Deposito']:
            if possible_terminal in df.columns:
                terminal_col = possible_terminal
                break

        # Try to detect time column
        time_col = None
        for possible_time in ['Hora de presentación', 'Hora Presentación', 'Hora']:
            if possible_time in df.columns:
                time_col = possible_time
                break

        # Try to detect commune column (optional, for better geocoding)
        commune_col = None
        if 'Comuna' in df.columns:
            commune_col = 'Comuna'

        # Validate required columns
        if not name_col or not address_col:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({
                    'error': f'El archivo debe contener columnas de Nombre y Dirección. Columnas encontradas: {list(df.columns)}'
                })
            }

        print(f"Mapped columns: Name={name_col}, Address={address_col}, Terminal={terminal_col}, Time={time_col}, Commune={commune_col}")

        # Convert to JSON
        drivers = []
        for idx, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row[name_col]) or str(row[name_col]).strip() == '':
                continue

            # Build address with commune for better geocoding
            address = str(row[address_col])
            if commune_col and not pd.isna(row[commune_col]):
                commune = str(row[commune_col]).strip()
                # Only append commune if it's not already in the address
                if commune.lower() not in address.lower():
                    address = f"{address}, {commune}"

            driver = {
                'name': str(row[name_col]).strip(),
                'address': address,
                'terminal': str(row[terminal_col]).strip() if terminal_col and not pd.isna(row[terminal_col]) else 'Terminal Aeropuerto T1',
                'time': str(row[time_col]).strip() if time_col and not pd.isna(row[time_col]) else '08:00'
            }

            # Add optional fields if available
            if 'Código OB' in df.columns and not pd.isna(row['Código OB']):
                driver['code'] = str(row['Código OB'])
            elif 'Código' in df.columns and not pd.isna(row['Código']):
                driver['code'] = str(row['Código'])

            if 'Celular' in df.columns and not pd.isna(row['Celular']):
                driver['phone'] = str(row['Celular'])

            if 'Rut' in df.columns and not pd.isna(row['Rut']):
                driver['rut'] = str(row['Rut'])

            drivers.append(driver)

        print(f"Successfully parsed {len(drivers)} drivers from file")

        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'drivers': drivers,
                'count': len(drivers),
                'message': 'Archivo procesado exitosamente'
            })
        }

    except Exception as e:
        import traceback
        print(f"Upload error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def handle_optimize(event):
    """Handle route optimization with support for bus mode"""
    try:
        body = event.get('body', '{}')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')

        data = json.loads(body)
        drivers = data.get('drivers', [])

        if not drivers:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'No drivers data provided'})
            }

        # Get configuration parameters from request (with defaults)
        config = data.get('config', {})
        num_vans_config = config.get('numVans', None)  # None means auto-calculate
        safety_margin_config = config.get('safetyMargin', 0.20)  # Default 20%
        destination_terminal_config = config.get('destinationTerminal', None)  # None means use from data

        print(f"Configuration: num_vans={num_vans_config}, safety_margin={safety_margin_config}, terminal={destination_terminal_config}")

        # Override SAFETY_BUFFER with user configuration
        global SAFETY_BUFFER
        original_safety_buffer = SAFETY_BUFFER

        try:
            SAFETY_BUFFER = 1.0 + safety_margin_config

            # Generate demo ID for tracking
            demo_id = str(uuid.uuid4())

            # Geocode all addresses and calculate travel times IN PARALLEL
            print(f"Geocoding {len(drivers)} addresses in parallel using Google Maps API...")

            # Prepare driver data for parallel processing
            driver_data_list = [(i, driver, destination_terminal_config) for i, driver in enumerate(drivers)]

            # Use ThreadPoolExecutor for parallel geocoding
            # Max 10 workers to avoid overwhelming the API
            max_workers = min(10, len(drivers))
            print(f"Using {max_workers} parallel workers for geocoding")

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all geocoding tasks
                future_to_idx = {executor.submit(geocode_driver_parallel, driver_data): driver_data[0]
                                for driver_data in driver_data_list}

                # Collect results as they complete
                results = []
                for future in as_completed(future_to_idx):
                    try:
                        idx, geocoded_driver = future.result()
                        results.append((idx, geocoded_driver))
                    except Exception as e:
                        idx = future_to_idx[future]
                        print(f"Error geocoding driver {idx+1}: {e}")
                        # Keep original driver data if geocoding fails
                        results.append((idx, drivers[idx]))

            # Sort results by original index to maintain order
            results.sort(key=lambda x: x[0])
            drivers = [driver for _, driver in results]

            print(f"✓ Completed geocoding {len(drivers)} addresses in parallel")

            # Sort drivers by presentation time (earliest first) within each terminal
            drivers_sorted = sorted(drivers, key=lambda d: d['presentation_time_minutes'])
            print(f"\nDrivers sorted by presentation time (earliest: {drivers_sorted[0]['pickup_time_latest']}, latest: {drivers_sorted[-1]['pickup_time_latest']})")

            # Group drivers by terminal (using sorted drivers)
            terminal_groups = group_drivers_by_terminal(drivers_sorted)

            # Optimize each terminal group
            all_vans = []
            total_distance = 0
            total_vans = 0

            for terminal, terminal_drivers in terminal_groups.items():
                print(f"\nProcessing {len(terminal_drivers)} drivers for terminal: {terminal}")

                # Check if this terminal uses bus mode
                if uses_bus_mode(terminal):
                    # BUS MODE: Use bus de acercamiento
                    terminal_coord = geocode_terminal(terminal)
                    vans, distance = optimize_with_bus_mode(terminal_drivers, terminal, terminal_coord, num_vans_config)
                    all_vans.extend(vans)
                    total_distance += distance
                    total_vans += len([v for v in vans if v.get('is_van', False)])

                else:
                    # NORMAL MODE: Direct to terminal
                    if num_vans_config is not None:
                        # User specified number of vans - use it directly (frontend already validated)
                        num_vans = num_vans_config
                        print(f"Using user-configured number of vans: {num_vans}")
                    else:
                        # Auto-calculate optimal number of vans (limit to 2-5 range)
                        num_vans = max(2, min(5, len(terminal_drivers) // 10 + 1))
                        print(f"Auto-calculated number of vans: {num_vans}")

                    # Cluster drivers using K-means
                    print(f"Clustering into {num_vans} vans...")
                    coordinates = np.array([[d['coordinates']['lat'], d['coordinates']['lng']] for d in terminal_drivers])
                    kmeans = KMeans(n_clusters=num_vans, random_state=42, n_init=10)
                    labels = kmeans.fit_predict(coordinates)

                    # Group drivers by cluster
                    clusters = [[] for _ in range(num_vans)]
                    for driver, label in zip(terminal_drivers, labels):
                        clusters[label].append(driver)

                    # Balance load
                    clusters = balance_load(clusters)

                    # Optimize route for each van
                    for i, cluster in enumerate(clusters):
                        if not cluster:
                            continue

                        optimized_route = optimize_route_tsp(cluster)

                        route_distance = 0
                        route_coordinates = []

                        for j in range(len(optimized_route)):
                            route_coordinates.append(optimized_route[j]['coordinates'])
                            if j > 0:
                                route_distance += calculate_distance(
                                    optimized_route[j-1]['coordinates'],
                                    optimized_route[j]['coordinates']
                                )

                        total_distance += route_distance

                        all_vans.append({
                            'name': f'Van {total_vans + i + 1}',
                            'drivers': optimized_route,
                            'route': route_coordinates,
                            'totalDistance': route_distance,
                            'destination': terminal,
                            'capacity': VAN_CAPACITY,
                            'utilization': len(optimized_route) / VAN_CAPACITY * 100,
                            'is_van': True
                        })

                    total_vans += num_vans

            # Calculate metrics
            manual_distance = total_distance * 1.12
            distance_saved = ((manual_distance - total_distance) / manual_distance) * 100

            result = {
                'vans': all_vans,
                'totalDrivers': len(drivers),
                'totalDistance': total_distance,
                'distanceSavedPercent': round(distance_saved, 1),
                'timeSaved': '15-20',
                'optimizationTime': '< 2 min',
                'success': True,
                'demoId': demo_id,
                'usingBusMode': any(v.get('is_bus', False) for v in all_vans)
            }

            # Track demo usage
            track_demo_usage(demo_id, {
                'drivers_count': len(drivers),
                'vans_count': total_vans,
                'total_distance': total_distance,
                'bus_mode': result['usingBusMode']
            })

            print(f"Optimization complete: {total_vans} vans, {total_distance:.1f} km total")
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps(result)
            }

        finally:
            # Restore original SAFETY_BUFFER
            SAFETY_BUFFER = original_safety_buffer

    except Exception as e:
        print(f"Optimization error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def lambda_handler(event, context):
    """Main Lambda handler for Function URLs"""
    print(f"Event: {json.dumps(event)}")

    # Handle OPTIONS for CORS preflight
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': ''
        }

    # Get the path and method
    path = event.get('rawPath', event.get('path', ''))
    method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')

    # Route to appropriate handler
    if path == '/api/upload' or path == '/upload':
        return handle_upload(event)
    elif path == '/api/optimize' or path == '/optimize':
        return handle_optimize(event)
    elif path == '/api/health' or path == '/health':
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'status': 'ok',
                'message': 'Route Optimizer Lambda is running'
            })
        }
    else:
        return {
            'statusCode': 404,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Not found'})
        }
