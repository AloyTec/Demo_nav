import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const COLORS = [
  '#EF4444', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6',
  '#EC4899', '#14B8A6', '#F97316', '#6366F1', '#84CC16'
];

const MapView = ({ data }) => {
  const [center, setCenter] = useState([-33.4489, -70.6693]); // Santiago de Chile default

  useEffect(() => {
    if (data?.vans && data.vans.length > 0) {
      const firstDriver = data.vans[0].drivers[0];
      if (firstDriver?.coordinates) {
        setCenter([firstDriver.coordinates.lat, firstDriver.coordinates.lng]);
      }
    }
  }, [data]);

  if (!data || !data.vans) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-100">
        <p className="text-gray-500 text-lg">Carga datos para visualizar rutas</p>
      </div>
    );
  }

  return (
    <div className="h-full relative">
      {/* Map */}
      <MapContainer 
        center={center} 
        zoom={12} 
        className="h-full w-full"
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {data.vans.map((van, vanIndex) => {
          const color = COLORS[vanIndex % COLORS.length];
          
          return (
            <React.Fragment key={vanIndex}>
              {/* Route polyline */}
              {van.route && (
                <Polyline
                  positions={van.route.map(point => [point.lat, point.lng])}
                  color={color}
                  weight={4}
                  opacity={0.7}
                />
              )}

              {/* Driver markers */}
              {van.drivers.map((driver, driverIndex) => {
                if (!driver.coordinates) return null;

                const customIcon = L.divIcon({
                  className: 'custom-marker',
                  html: `
                    <div style="
                      background-color: ${color};
                      width: 32px;
                      height: 32px;
                      border-radius: 50%;
                      border: 3px solid white;
                      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                      display: flex;
                      align-items: center;
                      justify-content: center;
                      color: white;
                      font-weight: bold;
                      font-size: 14px;
                    ">
                      ${driverIndex + 1}
                    </div>
                  `,
                  iconSize: [32, 32],
                  iconAnchor: [16, 16],
                });

                return (
                  <Marker
                    key={`${vanIndex}-${driverIndex}`}
                    position={[driver.coordinates.lat, driver.coordinates.lng]}
                    icon={customIcon}
                  >
                    <Popup>
                      <div className="p-2">
                        <h3 className="font-bold text-lg">{driver.name}</h3>
                        <p className="text-sm text-gray-600">{driver.address}</p>
                        <p className="text-xs text-gray-500 mt-1">Orden: #{driverIndex + 1}</p>
                        <p className="text-xs font-semibold" style={{ color }}>
                          {van.name}
                        </p>
                      </div>
                    </Popup>
                    <Tooltip direction="top" offset={[0, -10]} opacity={0.9}>
                      <span className="font-semibold">{driver.name}</span>
                    </Tooltip>
                  </Marker>
                );
              })}
            </React.Fragment>
          );
        })}
      </MapContainer>

      {/* Legend */}
      <div className="absolute top-4 right-4 bg-white rounded-lg shadow-xl p-4 z-[1000] max-h-96 overflow-y-auto">
        <h3 className="font-bold text-lg mb-3">Rutas por Van</h3>
        <div className="space-y-2">
          {data.vans.map((van, index) => (
            <div key={index} className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <div className="text-sm">
                <p className="font-semibold">{van.name}</p>
                <p className="text-gray-500">
                  {van.drivers.length} conductores • {van.totalDistance?.toFixed(1)} km
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Stats overlay */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-xl p-4 z-[1000]">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-blue-600">{data.vans.length}</p>
            <p className="text-xs text-gray-600">Vans</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-green-600">{data.totalDrivers}</p>
            <p className="text-xs text-gray-600">Conductores</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-purple-600">
              {data.totalDistance?.toFixed(0)}
            </p>
            <p className="text-xs text-gray-600">KM Total</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapView;
