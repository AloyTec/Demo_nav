#!/usr/bin/env python3
"""
Test script for geocoding comuna validation fix.
This script tests the specific issue reported: "Resbalon # 1568, Cerro Navia"
being incorrectly mapped to Cementerio General in Recoleta.
"""

import json
import os
import urllib3
import random
import re

# Configuration
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
http = urllib3.PoolManager()

def clean_address_for_geocoding(address):
    """Clean and format address for better geocoding results"""
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

def geocode_address_with_validation(address):
    """
    Geocode an address with comuna validation.
    This is the FIXED version that validates results against the comuna.
    """
    if not GOOGLE_MAPS_API_KEY:
        print(f"  ❌ ERROR: GOOGLE_MAPS_API_KEY not configured")
        return None

    # Clean the address first
    cleaned_address = clean_address_for_geocoding(address)

    # Extract comuna if present (after last comma)
    parts = cleaned_address.rsplit(',', 1)
    base_address = parts[0].strip()
    comuna = parts[1].strip() if len(parts) > 1 else None

    print(f"\n{'='*80}")
    print(f"Testing: {address}")
    print(f"Cleaned: {cleaned_address}")
    print(f"Base address: {base_address}")
    print(f"Comuna: {comuna}")
    print(f"{'='*80}")

    # Try full cleaned address with comuna validation
    try:
        query = f"{cleaned_address}, Santiago, Chile"
        print(f"\nQuerying Google Maps: {query}")

        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib3.util.url.quote(query)}&key={GOOGLE_MAPS_API_KEY}"
        response = http.request('GET', url, timeout=10.0)

        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))
            if data.get('status') == 'OK' and len(data.get('results', [])) > 0:
                results = data.get('results', [])
                print(f"\n→ Google Maps returned {len(results)} result(s)")

                # Print all results for debugging
                for i, result in enumerate(results):
                    formatted_address = result.get('formatted_address', 'N/A')
                    location = result['geometry']['location']
                    print(f"\n  Result #{i+1}:")
                    print(f"    Address: {formatted_address}")
                    print(f"    Coordinates: ({location['lat']}, {location['lng']})")

                    # Check comuna
                    if comuna:
                        in_comuna = is_in_comuna(result, comuna)
                        print(f"    In comuna '{comuna}': {'✓ YES' if in_comuna else '✗ NO'}")

                # If comuna is specified, validate all results against it
                if comuna:
                    print(f"\n→ Filtering results by comuna '{comuna}'...")
                    for i, result in enumerate(results):
                        if is_in_comuna(result, comuna):
                            location = result['geometry']['location']
                            formatted_address = result.get('formatted_address', 'N/A')
                            print(f"\n✅ MATCH FOUND (Result #{i+1}):")
                            print(f"   Address: {formatted_address}")
                            print(f"   Coordinates: ({location['lat']}, {location['lng']})")
                            return {
                                'lat': location['lat'],
                                'lng': location['lng'],
                                'address': formatted_address
                            }

                    # No result matched the expected comuna
                    print(f"\n❌ VALIDATION FAILED: None of the {len(results)} results matched comuna '{comuna}'")
                    return None
                else:
                    # No comuna specified, use first result
                    location = results[0]['geometry']['location']
                    formatted_address = results[0].get('formatted_address', 'N/A')
                    print(f"\n✓ Using first result (no comuna filter):")
                    print(f"   Address: {formatted_address}")
                    print(f"   Coordinates: ({location['lat']}, {location['lng']})")
                    return {
                        'lat': location['lat'],
                        'lng': location['lng'],
                        'address': formatted_address
                    }
            else:
                print(f"\n❌ Geocoding failed: {data.get('status')}")
                return None
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return None

# Test cases
test_addresses = [
    "Resbalon # 1568, Cerro Navia",  # The problematic case
    "Calle Los Copihues 1234, La Florida",
    "Avenida Vicuña Mackenna 4860, Macul",
    "Pasaje Las Rosas 789, Pudahuel",
]

if __name__ == "__main__":
    if not GOOGLE_MAPS_API_KEY:
        print("❌ ERROR: GOOGLE_MAPS_API_KEY environment variable not set")
        print("Set it with: export GOOGLE_MAPS_API_KEY='your-key-here'")
        exit(1)

    print("\n" + "="*80)
    print("GEOCODING COMUNA VALIDATION TEST")
    print("="*80)

    results = []
    for address in test_addresses:
        result = geocode_address_with_validation(address)
        results.append({
            'original_address': address,
            'result': result
        })

    print("\n\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    for item in results:
        print(f"\nOriginal: {item['original_address']}")
        if item['result']:
            print(f"  ✅ SUCCESS")
            print(f"  Geocoded: {item['result']['address']}")
            print(f"  Coords: ({item['result']['lat']}, {item['result']['lng']})")
        else:
            print(f"  ❌ FAILED TO GEOCODE")

    print("\n")
