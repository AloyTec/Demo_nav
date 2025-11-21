import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import FileUpload from './components/FileUpload';
import MapView from './components/MapView';
import KPIDashboard from './components/KPIDashboard';
import RouteEditor from './components/RouteEditor';
import { MapPin, BarChart3, Settings, Upload } from 'lucide-react';

function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const [routeData, setRouteData] = useState(null);
  const [optimizedData, setOptimizedData] = useState(null);

  const handleDataUploaded = (data) => {
    setRouteData(data);
  };

  const handleOptimized = (data) => {
    setOptimizedData(data);
    setActiveView('map');
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-gradient-to-b from-blue-600 to-blue-800 text-white p-6">
        <div className="mb-8">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <MapPin className="w-8 h-8" />
            RouteOptimizer
          </h1>
          <p className="text-blue-200 text-sm mt-1">Sistema Inteligente de Rutas</p>
        </div>

        <nav className="space-y-2">
          <button
            onClick={() => setActiveView('dashboard')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeView === 'dashboard' 
                ? 'bg-white text-blue-600 shadow-lg' 
                : 'hover:bg-blue-700'
            }`}
          >
            <Upload className="w-5 h-5" />
            Carga de Datos
          </button>

          <button
            onClick={() => setActiveView('map')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeView === 'map' 
                ? 'bg-white text-blue-600 shadow-lg' 
                : 'hover:bg-blue-700'
            }`}
            disabled={!optimizedData}
          >
            <MapPin className="w-5 h-5" />
            Mapa de Rutas
          </button>

          <button
            onClick={() => setActiveView('kpis')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeView === 'kpis' 
                ? 'bg-white text-blue-600 shadow-lg' 
                : 'hover:bg-blue-700'
            }`}
            disabled={!optimizedData}
          >
            <BarChart3 className="w-5 h-5" />
            KPIs y Métricas
          </button>

          <button
            onClick={() => setActiveView('editor')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeView === 'editor' 
                ? 'bg-white text-blue-600 shadow-lg' 
                : 'hover:bg-blue-700'
            }`}
            disabled={!optimizedData}
          >
            <Settings className="w-5 h-5" />
            Editor Manual
          </button>
        </nav>

        {optimizedData && (
          <div className="mt-8 p-4 bg-blue-700 rounded-lg">
            <h3 className="font-semibold mb-2">Última Optimización</h3>
            <div className="text-sm space-y-1">
              <p className="text-blue-200">Vans: {optimizedData.vans?.length || 0}</p>
              <p className="text-blue-200">Conductores: {optimizedData.totalDrivers || 0}</p>
              <p className="text-green-300 font-semibold">✓ Optimizado</p>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {activeView === 'dashboard' && (
          <Dashboard 
            onDataUploaded={handleDataUploaded}
            onOptimized={handleOptimized}
            routeData={routeData}
          />
        )}
        
        {activeView === 'map' && optimizedData && (
          <MapView data={optimizedData} />
        )}

        {activeView === 'kpis' && optimizedData && (
          <KPIDashboard data={optimizedData} />
        )}

        {activeView === 'editor' && optimizedData && (
          <RouteEditor 
            data={optimizedData} 
            onUpdate={setOptimizedData}
          />
        )}
      </div>
    </div>
  );
}

export default App;
