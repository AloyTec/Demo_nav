import React, { useState } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { Users, Truck, Navigation, AlertCircle } from 'lucide-react';

const COLORS = ['#EF4444', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6'];

const RouteEditor = ({ data, onUpdate }) => {
  const [vans, setVans] = useState(data.vans || []);
  const [changes, setChanges] = useState([]);

  const handleDragEnd = (result) => {
    const { source, destination } = result;

    if (!destination) return;
    if (source.droppableId === destination.droppableId && source.index === destination.index) {
      return;
    }

    const sourceVanIndex = parseInt(source.droppableId.split('-')[1]);
    const destVanIndex = parseInt(destination.droppableId.split('-')[1]);

    const newVans = [...vans];
    const sourceVan = newVans[sourceVanIndex];
    const destVan = newVans[destVanIndex];

    const [movedDriver] = sourceVan.drivers.splice(source.index, 1);
    destVan.drivers.splice(destination.index, 0, movedDriver);

    // Recalculate distances (simplified)
    sourceVan.totalDistance = sourceVan.drivers.length * 5; // Mock calculation
    destVan.totalDistance = destVan.drivers.length * 5;

    setVans(newVans);
    
    // Track changes
    const change = {
      timestamp: new Date().toLocaleTimeString(),
      driver: movedDriver.name,
      from: sourceVan.name,
      to: destVan.name
    };
    setChanges([change, ...changes]);

    // Update parent
    onUpdate({ ...data, vans: newVans });
  };

  return (
    <div className="p-8 bg-gray-50 min-h-full">
      <h1 className="text-4xl font-bold text-gray-800 mb-2">Editor Manual de Rutas</h1>
      <p className="text-gray-600 mb-6">
        Arrastra conductores entre vans para ajustar las asignaciones
      </p>

      {changes.length > 0 && (
        <div className="mb-6 bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900">Historial de Cambios</h3>
              <div className="mt-2 space-y-1 text-sm">
                {changes.slice(0, 3).map((change, index) => (
                  <p key={index} className="text-blue-800">
                    <span className="font-mono text-xs text-blue-600">{change.timestamp}</span>
                    {' - '}
                    <strong>{change.driver}</strong> movido de{' '}
                    <span className="font-semibold">{change.from}</span> a{' '}
                    <span className="font-semibold">{change.to}</span>
                  </p>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {vans.map((van, vanIndex) => (
            <div
              key={vanIndex}
              className="bg-white rounded-xl shadow-lg overflow-hidden"
              style={{ borderTop: `4px solid ${COLORS[vanIndex % COLORS.length]}` }}
            >
              {/* Van Header */}
              <div className="p-4 bg-gray-50 border-b">
                <div className="flex items-center gap-3 mb-2">
                  <Truck className="w-6 h-6" style={{ color: COLORS[vanIndex % COLORS.length] }} />
                  <h3 className="text-lg font-bold text-gray-800">{van.name}</h3>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex items-center gap-1 text-gray-600">
                    <Users className="w-4 h-4" />
                    <span>{van.drivers.length} conductores</span>
                  </div>
                  <div className="flex items-center gap-1 text-gray-600">
                    <Navigation className="w-4 h-4" />
                    <span>{van.totalDistance?.toFixed(1)} km</span>
                  </div>
                </div>
              </div>

              {/* Droppable Driver List */}
              <Droppable droppableId={`van-${vanIndex}`}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`p-4 min-h-[300px] transition-colors ${
                      snapshot.isDraggingOver ? 'bg-blue-50' : ''
                    }`}
                  >
                    {van.drivers.length === 0 ? (
                      <p className="text-gray-400 text-center py-8">
                        Arrastra conductores aquí
                      </p>
                    ) : (
                      van.drivers.map((driver, driverIndex) => (
                        <Draggable
                          key={`${vanIndex}-${driverIndex}`}
                          draggableId={`driver-${vanIndex}-${driverIndex}`}
                          index={driverIndex}
                        >
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              className={`mb-2 p-3 rounded-lg border-2 transition-all ${
                                snapshot.isDragging
                                  ? 'border-blue-500 bg-blue-100 shadow-lg'
                                  : 'border-gray-200 bg-white hover:border-gray-300'
                              }`}
                            >
                              <div className="flex items-center gap-2">
                                <div
                                  className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm"
                                  style={{ backgroundColor: COLORS[vanIndex % COLORS.length] }}
                                >
                                  {driverIndex + 1}
                                </div>
                                <div className="flex-1 min-w-0">
                                  <p className="font-semibold text-sm text-gray-800 truncate">
                                    {driver.name}
                                  </p>
                                  <p className="text-xs text-gray-500 truncate">
                                    {driver.address}
                                  </p>
                                </div>
                              </div>
                            </div>
                          )}
                        </Draggable>
                      ))
                    )}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>
    </div>
  );
};

export default RouteEditor;
