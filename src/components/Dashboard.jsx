import React, { useState } from 'react';
import FileUpload from './FileUpload';
import axios from 'axios';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '../config/api';

const Dashboard = ({ onDataUploaded, onOptimized, routeData }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [progress, setProgress] = useState({ stage: '', percent: 0 });

  // Configuration parameters
  const [numVans, setNumVans] = useState(3);
  const [safetyMargin, setSafetyMargin] = useState(20);
  const [destinationTerminal, setDestinationTerminal] = useState('Terminal Conquistador (Av. 5 Poniente 1601, Maipú)');

  const handleFileUpload = async (file) => {
    setUploadedFile(file);
    setLoading(true);
    setError(null);
    setProgress({ stage: 'Leyendo archivo...', percent: 10 });

    try {
      // Convert file to base64
      const reader = new FileReader();
      reader.onload = async () => {
        const base64Content = reader.result.split(',')[1]; // Remove data:*/*;base64, prefix

        try {
          // Upload and parse file
          setProgress({ stage: 'Subiendo y procesando datos...', percent: 25 });
          const response = await axios.post(`${API_BASE_URL}/api/upload`, {
            file_content: base64Content,
            filename: file.name
          });

          onDataUploaded(response.data);
          setProgress({ stage: 'Datos procesados correctamente', percent: 50 });

          // Automatically trigger optimization
          await handleOptimize(response.data);

        } catch (err) {
          setError(err.response?.data?.error || 'Error al procesar el archivo');
          setLoading(false);
          setProgress({ stage: '', percent: 0 });
        }
      };

      reader.onerror = () => {
        setError('Error al leer el archivo');
        setLoading(false);
        setProgress({ stage: '', percent: 0 });
      };

      reader.readAsDataURL(file);

    } catch (err) {
      setError(err.message || 'Error al procesar el archivo');
      setLoading(false);
      setProgress({ stage: '', percent: 0 });
    }
  };

  const handleOptimize = async (data) => {
    try {
      setProgress({ stage: 'Geocodificando direcciones...', percent: 65 });

      // Simulate geocoding progress (the actual work happens in Lambda)
      setTimeout(() => {
        setProgress({ stage: 'Optimizando rutas con algoritmos avanzados...', percent: 85 });
      }, 1000);

      // Include configuration parameters in the request
      const optimizationData = {
        ...(data || routeData),
        config: {
          numVans: numVans,
          safetyMargin: safetyMargin / 100, // Convert percentage to decimal
          destinationTerminal: destinationTerminal
        }
      };

      const response = await axios.post(`${API_BASE_URL}/api/optimize`, optimizationData);

      setProgress({ stage: 'Finalizado! Preparando visualización...', percent: 100 });
      onOptimized(response.data);

      // Clear progress after a short delay
      setTimeout(() => {
        setLoading(false);
        setProgress({ stage: '', percent: 0 });
      }, 800);

    } catch (err) {
      setError(err.response?.data?.error || 'Error al optimizar rutas');
      setLoading(false);
      setProgress({ stage: '', percent: 0 });
    }
  };

  return (
    <div className="p-4 md:p-8 pt-16 lg:pt-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl md:text-4xl font-bold text-gray-800 mb-2">
          Panel de Administración
        </h1>
        <p className="text-sm md:text-base text-gray-600 mb-6 md:mb-8">
          Carga tu archivo Excel con las direcciones de conductores para optimizar las rutas
        </p>

        {/* Configuration Section */}
        <div className="bg-white rounded-xl shadow-lg p-4 md:p-8 mb-6">
          <h2 className="text-xl md:text-2xl font-bold text-gray-800 mb-2">
            ⚙️ Configuración de Rutas
          </h2>
          <p className="text-sm md:text-base text-gray-600 mb-6">
            Ajusta los parámetros antes de cargar el archivo
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Number of Vans */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Cantidad de Vans
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={numVans}
                onChange={(e) => setNumVans(parseInt(e.target.value) || 1)}
                disabled={loading}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed text-lg font-semibold"
              />
              <p className="text-xs text-gray-500 mt-1">Entre 1 y 10 vans</p>
            </div>

            {/* Safety Margin */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Margen de Seguridad (%)
              </label>
              <select
                value={safetyMargin}
                onChange={(e) => setSafetyMargin(parseInt(e.target.value))}
                disabled={loading}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed text-lg font-semibold"
              >
                <option value="10">10% - Ajustado</option>
                <option value="15">15% - Moderado</option>
                <option value="20">20% - Recomendado</option>
                <option value="25">25% - Conservador</option>
                <option value="30">30% - Máximo</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">Tiempo extra por imprevistos</p>
            </div>

            {/* Destination Terminal */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Terminal de Destino
              </label>
              <select
                value={destinationTerminal}
                onChange={(e) => setDestinationTerminal(e.target.value)}
                disabled={loading}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed text-lg font-semibold"
              >
                <option value="Terminal Conquistador (Av. 5 Poniente 1601, Maipú)">Terminal Conquistador</option>
                <option value="Terminal Aeropuerto T1">Terminal Aeropuerto T1</option>
                <option value="Terminal Aeropuerto T2">Terminal Aeropuerto T2</option>
                <option value="Terminal Maipú">Terminal Maipú</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">Punto de llegada final</p>
            </div>
          </div>

          {/* Summary of Configuration */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
            <p className="text-sm text-blue-800">
              <span className="font-semibold">Configuración Actual:</span> {numVans} van{numVans > 1 ? 's' : ''} con {safetyMargin}% de margen hacia {destinationTerminal.split('(')[0].trim()}
            </p>
          </div>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-lg p-4 md:p-8 mb-6">
          <h2 className="text-xl md:text-2xl font-bold text-gray-800 mb-2">
            📂 Carga de Archivo
          </h2>
          <p className="text-sm md:text-base text-gray-600 mb-6">
            Sube tu archivo Excel o CSV con las direcciones
          </p>

          <FileUpload onFileUpload={handleFileUpload} disabled={loading} />

          {loading && (
            <div className="mt-6 space-y-4">
              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${progress.percent}%` }}
                />
              </div>

              {/* Progress Info */}
              <div className="flex flex-col md:flex-row items-center justify-between gap-2">
                <div className="flex items-center gap-3 text-blue-600">
                  <Loader2 className="w-5 h-5 md:w-6 md:h-6 animate-spin" />
                  <span className="text-sm md:text-base font-semibold">{progress.stage}</span>
                </div>
                <span className="text-xl md:text-2xl font-bold text-blue-600">{progress.percent}%</span>
              </div>

              {/* Processing Steps */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-2 md:gap-3 mt-4">
                <div className={`flex items-center gap-2 p-2 md:p-3 rounded-lg transition-all ${progress.percent >= 10 ? 'bg-blue-50 text-blue-700' : 'bg-gray-50 text-gray-400'}`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${progress.percent >= 10 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-500'}`}>
                    {progress.percent > 25 ? '✓' : '1'}
                  </div>
                  <span className="text-xs md:text-sm font-medium">Subiendo</span>
                </div>

                <div className={`flex items-center gap-2 p-2 md:p-3 rounded-lg transition-all ${progress.percent >= 50 ? 'bg-blue-50 text-blue-700' : 'bg-gray-50 text-gray-400'}`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${progress.percent >= 50 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-500'}`}>
                    {progress.percent > 65 ? '✓' : '2'}
                  </div>
                  <span className="text-xs md:text-sm font-medium">Procesando</span>
                </div>

                <div className={`flex items-center gap-2 p-2 md:p-3 rounded-lg transition-all ${progress.percent >= 65 ? 'bg-blue-50 text-blue-700' : 'bg-gray-50 text-gray-400'}`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${progress.percent >= 65 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-500'}`}>
                    {progress.percent > 85 ? '✓' : '3'}
                  </div>
                  <span className="text-xs md:text-sm font-medium">Geocodificando</span>
                </div>

                <div className={`flex items-center gap-2 p-2 md:p-3 rounded-lg transition-all ${progress.percent >= 85 ? 'bg-blue-50 text-blue-700' : 'bg-gray-50 text-gray-400'}`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${progress.percent >= 85 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-500'}`}>
                    {progress.percent === 100 ? '✓' : '4'}
                  </div>
                  <span className="text-xs md:text-sm font-medium">Optimizando</span>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="mt-6 flex items-start gap-3 text-red-600 bg-red-50 p-4 rounded-lg">
              <AlertCircle className="w-5 h-5 md:w-6 md:h-6 flex-shrink-0" />
              <span className="text-sm md:text-base">{error}</span>
            </div>
          )}

          {uploadedFile && !loading && !error && (
            <div className="mt-6 flex items-start gap-3 text-green-600 bg-green-50 p-4 rounded-lg">
              <CheckCircle className="w-5 h-5 md:w-6 md:h-6 flex-shrink-0" />
              <span className="font-semibold text-sm md:text-base break-all">Archivo procesado exitosamente: {uploadedFile.name}</span>
            </div>
          )}
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-4 md:p-6 rounded-xl shadow-lg">
            <h3 className="text-base md:text-lg font-semibold mb-2">⚡ Procesamiento Rápido</h3>
            <p className="text-blue-100 text-sm md:text-base">Optimización en menos de 2 minutos por terminal</p>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-4 md:p-6 rounded-xl shadow-lg">
            <h3 className="text-base md:text-lg font-semibold mb-2">📊 Reducción de KM</h3>
            <p className="text-green-100 text-sm md:text-base">10-15% de ahorro en distancias recorridas</p>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-4 md:p-6 rounded-xl shadow-lg">
            <h3 className="text-base md:text-lg font-semibold mb-2">🎯 Balance Óptimo</h3>
            <p className="text-purple-100 text-sm md:text-base">Distribución perfecta entre vans</p>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-white rounded-xl shadow-lg p-4 md:p-8">
          <h2 className="text-xl md:text-2xl font-bold text-gray-800 mb-4">
            📋 Formato de Excel Requerido
          </h2>
          <div className="space-y-3 text-gray-700 text-sm md:text-base">
            <p>El archivo Excel debe contener las siguientes columnas:</p>
            <ul className="list-disc list-inside space-y-2 ml-2 md:ml-4">
              <li><strong>Nombre:</strong> Nombre del conductor</li>
              <li><strong>Dirección:</strong> Dirección completa de recogida</li>
              <li><strong>Terminal:</strong> Terminal de destino (ej: Terminal A, Terminal B)</li>
              <li><strong>Hora:</strong> Hora de recogida programada (opcional)</li>
            </ul>
            <div className="mt-4 p-3 md:p-4 bg-blue-50 rounded-lg">
              <p className="text-xs md:text-sm text-blue-800">
                💡 <strong>Tip:</strong> Puedes usar el botón "Cargar Datos de Ejemplo" para probar el sistema
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
