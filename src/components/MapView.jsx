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

const BUS_COLOR = '#DC2626'; // Rojo distintivo para el bus

const MapView = ({ data, mobileMenuOpen = false }) => {
  const [center, setCenter] = useState([-33.4489, -70.6693]); // Santiago de Chile default

  useEffect(() => {
    console.log('MapView data:', data); // DEBUG
    if (data?.vans && data.vans.length > 0) {
      console.log('First van:', data.vans[0]); // DEBUG
      console.log('Route exists?', data.vans[0].route); // DEBUG
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
          const isBus = van.is_bus === true;
          const color = isBus ? BUS_COLOR : COLORS[vanIndex % COLORS.length];

          return (
            <React.Fragment key={`van-${van.name}`}>
              {/* Route polyline with improved styling */}
              {van.route && van.route.length > 1 && (
                <Polyline
                  positions={van.route.map(point => [point.lat, point.lng])}
                  color={color}
                  weight={3}
                  opacity={0.8}
                  dashArray="10, 5"
                  lineJoin="round"
                  lineCap="round"
                />
              )}

              {/* Driver markers */}
              {!isBus && van.drivers.map((driver, driverIndex) => {
                if (!driver.coordinates) return null;

                const isFirst = driverIndex === 0;
                const isLast = driverIndex === van.drivers.length - 1;

                const customIcon = L.divIcon({
                  className: 'custom-marker',
                  html: `
                    <div style="
                      background: ${isFirst ? '#22C55E' : isLast ? '#EF4444' : color};
                      width: ${isFirst || isLast ? '36px' : '30px'};
                      height: ${isFirst || isLast ? '36px' : '30px'};
                      border-radius: 50%;
                      border: 3px solid white;
                      box-shadow: 0 3px 10px rgba(0,0,0,0.4);
                      display: flex;
                      align-items: center;
                      justify-content: center;
                      color: white;
                      font-weight: bold;
                      font-size: ${isFirst || isLast ? '16px' : '13px'};
                      transition: all 0.3s ease;
                    ">
                      ${isFirst ? '🏁' : isLast ? '🏁' : driverIndex + 1}
                    </div>
                  `,
                  iconSize: [isFirst || isLast ? 36 : 30, isFirst || isLast ? 36 : 30],
                  iconAnchor: [isFirst || isLast ? 18 : 15, isFirst || isLast ? 18 : 15],
                });

                return (
                  <Marker
                    key={`${vanIndex}-${driver.code || driverIndex}`}
                    position={[driver.coordinates.lat, driver.coordinates.lng]}
                    icon={customIcon}
                  >
                    <Popup>
                      <div className="p-2 min-w-[200px]">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-bold text-lg">{driver.name}</h3>
                          <span 
                            className="text-xs font-bold px-2 py-1 rounded"
                            style={{ backgroundColor: color, color: 'white' }}
                          >
                            {van.name}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-1">
                          📍 {driver.address}
                        </p>
                        <p className="text-xs text-gray-500">
                          🚩 Terminal: {driver.terminal}
                        </p>
                        <p className="text-xs text-gray-500">
                          ⏰ Hora: {driver.time}
                        </p>
                        <div className="mt-2 pt-2 border-t border-gray-200">
                          <p className="text-xs font-semibold text-gray-700">
                            {isFirst ? '🏁 Inicio de ruta' : isLast ? '🏁 Fin de ruta' : `Parada #${driverIndex + 1}`}
                          </p>
                        </div>
                      </div>
                    </Popup>
                    <Tooltip direction="top" offset={[0, -15]} opacity={0.95}>
                      <div className="text-center">
                        <div className="font-bold">{driver.name}</div>
                        <div className="text-xs">{isFirst ? 'Inicio' : isLast ? 'Fin' : `Parada ${driverIndex + 1}`}</div>
                      </div>
                    </Tooltip>
                  </Marker>
                );
              })}

              {/* Bus markers - show bus icon for bus routes */}
              {isBus && van.route && van.route.map((point, pointIndex) => {
                const isBusStop = pointIndex === 0; // First point is bus stop
                const isTerminal = pointIndex === van.route.length - 1; // Last point is terminal

                const busIcon = L.divIcon({
                  className: 'custom-marker',
                  html: `
                    <div style="
                      background: ${BUS_COLOR};
                      width: 48px;
                      height: 48px;
                      border-radius: 50%;
                      border: 4px solid white;
                      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
                      display: flex;
                      align-items: center;
                      justify-content: center;
                      font-size: 24px;
                    ">
                      ${isBusStop ? '🚏' : '🚌'}
                    </div>
                  `,
                  iconSize: [48, 48],
                  iconAnchor: [24, 24],
                });

                return (
                  <Marker
                    key={`bus-${vanIndex}-${pointIndex}`}
                    position={[point.lat, point.lng]}
                    icon={busIcon}
                  >
                    <Popup>
                      <div className="p-2 min-w-[200px]">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-bold text-lg">{isBusStop ? '🚏 Punto de Encuentro' : '🚌 Terminal'}</h3>
                          <span
                            className="text-xs font-bold px-2 py-1 rounded"
                            style={{ backgroundColor: BUS_COLOR, color: 'white' }}
                          >
                            BUS
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          {isBusStop ? 'Av. Pajaritos con Américo Vespucio' : van.destination}
                        </p>
                        <p className="text-xs text-gray-500 mb-1">
                          👥 Pasajeros: {van.drivers.length}
                        </p>
                        <p className="text-xs text-gray-500">
                          🚌 Capacidad: {van.capacity}
                        </p>
                        <div className="mt-2 pt-2 border-t border-gray-200">
                          <p className="text-xs font-semibold text-red-700">
                            {isBusStop ? 'Punto de transbordo desde vans' : 'Destino final'}
                          </p>
                        </div>
                      </div>
                    </Popup>
                    <Tooltip direction="top" offset={[0, -24]} opacity={0.95}>
                      <div className="text-center">
                        <div className="font-bold">{isBusStop ? 'Bus Stop' : 'Terminal'}</div>
                        <div className="text-xs">{van.drivers.length} pasajeros</div>
                      </div>
                    </Tooltip>
                  </Marker>
                );
              })}
            </React.Fragment>
          );
        })}
      </MapContainer>

      {/* Legend */}
      <div className={`absolute top-4 right-4 bg-white rounded-lg shadow-xl p-4 z-[1000] max-h-96 overflow-y-auto transition-opacity duration-300 ${mobileMenuOpen ? 'opacity-0 pointer-events-none lg:opacity-100 lg:pointer-events-auto' : ''}`}>
        <h3 className="font-bold text-lg mb-3">Rutas por Vehículo</h3>
        <div className="space-y-2">
          {data.vans.map((van, index) => {
            const isBus = van.is_bus === true;
            const color = isBus ? BUS_COLOR : COLORS[index % COLORS.length];

            return (
              <div key={index} className="flex items-center gap-2">
                {isBus ? (
                  <div className="w-8 h-8 flex items-center justify-center text-xl">
                    🚌
                  </div>
                ) : (
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: color }}
                  />
                )}
                <div className="text-sm">
                  <p className="font-semibold">{van.name}</p>
                  <p className="text-gray-500">
                    {van.drivers.length} {isBus ? 'pasajeros' : 'conductores'} • {van.totalDistance?.toFixed(1)} km
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Stats overlay */}
      <div className={`absolute bottom-4 left-4 bg-white rounded-lg shadow-xl p-4 z-[1000] transition-opacity duration-300 ${mobileMenuOpen ? 'opacity-0 pointer-events-none lg:opacity-100 lg:pointer-events-auto' : ''}`}>
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
