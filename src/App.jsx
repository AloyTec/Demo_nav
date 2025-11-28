import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import FileUpload from './components/FileUpload';
import MapView from './components/MapView';
import KPIDashboard from './components/KPIDashboard';
import RouteEditor from './components/RouteEditor';
import { MapPin, BarChart3, Settings, Upload, Menu, X } from 'lucide-react';

function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const [routeData, setRouteData] = useState(null);
  const [optimizedData, setOptimizedData] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleDataUploaded = (data) => {
    setRouteData(data);
  };

  const handleOptimized = (data) => {
    setOptimizedData(data);
    setActiveView('map');
  };

  const handleViewChange = (view) => {
    setActiveView(view);
    setMobileMenuOpen(false); // Close menu on mobile when changing view
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Mobile Menu Button */}
      <button
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 bg-blue-600 text-white p-2 rounded-lg shadow-lg"
      >
        {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      {/* Sidebar - Hidden on mobile by default, overlay when open */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-40
        w-64 bg-gradient-to-b from-blue-600 to-blue-800 text-white p-6
        transform transition-transform duration-300 ease-in-out
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="mb-8 mt-12 lg:mt-0">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <MapPin className="w-8 h-8" />
            RouteOptimizer
          </h1>
          <p className="text-blue-200 text-sm mt-1">Sistema Inteligente de Rutas</p>
        </div>

        <nav className="space-y-2">
          <button
            onClick={() => handleViewChange('dashboard')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeView === 'dashboard'
                ? 'bg-white text-blue-600 shadow-lg'
                : 'hover:bg-blue-700'
            }`}
          >
            <Upload className="w-5 h-5" />
            <span className="text-sm lg:text-base">Carga de Datos</span>
          </button>

          <button
            onClick={() => handleViewChange('map')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeView === 'map'
                ? 'bg-white text-blue-600 shadow-lg'
                : 'hover:bg-blue-700'
            }`}
            disabled={!optimizedData}
          >
            <MapPin className="w-5 h-5" />
            <span className="text-sm lg:text-base">Mapa de Rutas</span>
          </button>

          <button
            onClick={() => handleViewChange('kpis')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeView === 'kpis'
                ? 'bg-white text-blue-600 shadow-lg'
                : 'hover:bg-blue-700'
            }`}
            disabled={!optimizedData}
          >
            <BarChart3 className="w-5 h-5" />
            <span className="text-sm lg:text-base">KPIs y Métricas</span>
          </button>

          <button
            onClick={() => handleViewChange('editor')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeView === 'editor'
                ? 'bg-white text-blue-600 shadow-lg'
                : 'hover:bg-blue-700'
            }`}
            disabled={!optimizedData}
          >
            <Settings className="w-5 h-5" />
            <span className="text-sm lg:text-base">Editor Manual</span>
          </button>
        </nav>

        {optimizedData && (
          <div className="mt-8 p-4 bg-blue-700 rounded-lg hidden lg:block">
            <h3 className="font-semibold mb-2">Última Optimización</h3>
            <div className="text-sm space-y-1">
              <p className="text-blue-200">
                Vans: {
                  new Set(
                    optimizedData.vans
                      ?.filter(van => !van.name.toLowerCase().includes('bus'))
                      .map(van => van.name.match(/Van\s+(\d+)/)?.[1])
                      .filter(Boolean)
                  ).size || 0
                }
              </p>
              <p className="text-blue-200">Conductores: {optimizedData.totalDrivers || 0}</p>
              <p className="text-green-300 font-semibold">✓ Optimizado</p>
            </div>
          </div>
        )}
      </div>

      {/* Overlay for mobile menu */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className={`flex-1 overflow-auto w-full ${mobileMenuOpen ? 'pointer-events-none lg:pointer-events-auto' : ''}`}>
        {activeView === 'dashboard' && (
          <Dashboard
            onDataUploaded={handleDataUploaded}
            onOptimized={handleOptimized}
            routeData={routeData}
          />
        )}

        {activeView === 'map' && optimizedData && (
          <MapView data={optimizedData} mobileMenuOpen={mobileMenuOpen} />
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
