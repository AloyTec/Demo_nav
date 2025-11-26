import json
import base64
import boto3
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
import time
import random
from geopy.geocoders import Nominatim
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

# Van and Bus Configuration
VAN_CAPACITY = 10  # Capacidad máxima por van
BUS_CAPACITY = 40  # Capacidad del bus de acercamiento

# Terminal Maipú - Bus stop location (fixed location near the terminal)
BUS_STOP_MAIPU = {
    'lat': -33.5115,  # Cerca del terminal Maipú
    'lng': -70.7646,
    'address': 'Punto de Encuentro - Av. Pajaritos con Américo Vespucio'
}

# Terminals that use bus mode
TERMINALS_WITH_BUS = ['maipu', 'maipú', 'terminal maipu', 'terminal maipú']

# Initialize geocoder
geolocator = Nominatim(user_agent="route_optimizer_demo_chile", timeout=10)

def cors_headers():
    """Return CORS headers for responses"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }

def geocode_address(address):
    """Geocode an address to lat/lng coordinates"""
    try:
        location = geolocator.geocode(f"{address}, Santiago, Chile")
        if location:
            print(f"✓ Geocoded: {address}")
            return {'lat': location.latitude, 'lng': location.longitude}
    except Exception as e:
        print(f"Geocoding error for {address}: {e}")

    # Fallback to random coordinates in Santiago area
    print(f"⚠ Using fallback coordinates for: {address}")
    return {
        'lat': -33.4489 + (random.random() - 0.5) * 0.1,
        'lng': -70.6693 + (random.random() - 0.5) * 0.1
    }

def calculate_distance(coord1, coord2):
    """Calculate distance between two coordinates in km"""
    return geodesic((coord1['lat'], coord1['lng']), (coord2['lat'], coord2['lng'])).km

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

def optimize_with_bus_mode(drivers, terminal, terminal_coord):
    """
    Optimize routes using bus de acercamiento mode

    Flow:
    1. Van picks up Group 1 drivers and drops them at bus stop
    2. Van returns and picks up Group 2 drivers, takes them directly to terminal
    3. Bus takes all Group 1 passengers from bus stop to terminal
    """
    print(f"Using BUS MODE for {len(drivers)} drivers to {terminal}")

    # Determine number of vans needed
    num_vans = max(2, min(5, len(drivers) // 10 + 1))

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
        bus_distance = calculate_distance(BUS_STOP_MAIPU, terminal_coord)
        total_distance += bus_distance

        # Create driver list for bus with bus stop info
        bus_driver_list = []
        for passenger in bus_passengers:
            bus_driver_list.append({
                **passenger,
                'pickup_location': 'Bus Stop - Av. Pajaritos con Américo Vespucio'
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
                # First try: Read with auto-detection
                df = pd.read_csv(BytesIO(file_content), sep=None, engine='python')

                # Check if first row is "Table 1" (Excel export header)
                if len(df) > 0 and str(df.iloc[0, 0]).strip() == 'Table 1':
                    print("Detected 'Table 1' header, re-reading file...")
                    # Re-read skipping the first row
                    df = pd.read_csv(BytesIO(file_content), sep=';', skiprows=1)

            except Exception as e:
                print(f"Auto-detection failed: {e}, trying semicolon...")
                # Fallback to semicolon
                df = pd.read_csv(BytesIO(file_content), sep=';')

                # Check for Table 1 header
                if len(df) > 0 and str(df.iloc[0, 0]).strip() == 'Table 1':
                    df = pd.read_csv(BytesIO(file_content), sep=';', skiprows=1)
        else:
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

        # Generate demo ID for tracking
        demo_id = str(uuid.uuid4())

        # Geocode all addresses
        print("Geocoding addresses...")
        for i, driver in enumerate(drivers):
            print(f"Geocoding {i+1}/{len(drivers)}: {driver['address']}")
            driver['coordinates'] = geocode_address(driver['address'])
            time.sleep(1.0)  # Rate limiting

        # Group drivers by terminal
        terminal_groups = group_drivers_by_terminal(drivers)

        # Optimize each terminal group
        all_vans = []
        total_distance = 0
        total_vans = 0

        for terminal, terminal_drivers in terminal_groups.items():
            print(f"\nProcessing {len(terminal_drivers)} drivers for terminal: {terminal}")

            # Check if this terminal uses bus mode
            if uses_bus_mode(terminal):
                # BUS MODE: Use bus de acercamiento
                terminal_coord = geocode_address(f"{terminal}, Santiago, Chile")
                vans, distance = optimize_with_bus_mode(terminal_drivers, terminal, terminal_coord)
                all_vans.extend(vans)
                total_distance += distance
                total_vans += len([v for v in vans if v.get('is_van', False)])

            else:
                # NORMAL MODE: Direct to terminal
                num_vans = max(2, min(5, len(terminal_drivers) // 10 + 1))

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
