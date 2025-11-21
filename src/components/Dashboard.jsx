import React, { useState } from 'react';
import FileUpload from './FileUpload';
import axios from 'axios';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';

const Dashboard = ({ onDataUploaded, onOptimized, routeData }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleFileUpload = async (file) => {
    setUploadedFile(file);
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Upload and parse file
      const response = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      onDataUploaded(response.data);
      
      // Automatically trigger optimization
      await handleOptimize(response.data);
      
    } catch (err) {
      setError(err.response?.data?.error || 'Error al procesar el archivo');
      setLoading(false);
    }
  };

  const handleOptimize = async (data) => {
    try {
      const response = await axios.post('/api/optimize', data || routeData);
      onOptimized(response.data);
      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Error al optimizar rutas');
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">
          Panel de Administración
        </h1>
        <p className="text-gray-600 mb-8">
          Carga tu archivo Excel con las direcciones de conductores para optimizar las rutas
        </p>

        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
          <FileUpload onFileUpload={handleFileUpload} disabled={loading} />
          
          {loading && (
            <div className="mt-6 flex items-center justify-center gap-3 text-blue-600">
              <Loader2 className="w-6 h-6 animate-spin" />
              <span className="text-lg font-semibold">Procesando y optimizando rutas...</span>
            </div>
          )}

          {error && (
            <div className="mt-6 flex items-center gap-3 text-red-600 bg-red-50 p-4 rounded-lg">
              <AlertCircle className="w-6 h-6" />
              <span>{error}</span>
            </div>
          )}

          {uploadedFile && !loading && !error && (
            <div className="mt-6 flex items-center gap-3 text-green-600 bg-green-50 p-4 rounded-lg">
              <CheckCircle className="w-6 h-6" />
              <span className="font-semibold">Archivo procesado exitosamente: {uploadedFile.name}</span>
            </div>
          )}
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-xl shadow-lg">
            <h3 className="text-lg font-semibold mb-2">⚡ Procesamiento Rápido</h3>
            <p className="text-blue-100">Optimización en menos de 2 minutos por terminal</p>
          </div>
          
          <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-xl shadow-lg">
            <h3 className="text-lg font-semibold mb-2">📊 Reducción de KM</h3>
            <p className="text-green-100">10-15% de ahorro en distancias recorridas</p>
          </div>
          
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-6 rounded-xl shadow-lg">
            <h3 className="text-lg font-semibold mb-2">🎯 Balance Óptimo</h3>
            <p className="text-purple-100">Distribución perfecta entre vans</p>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            📋 Formato de Excel Requerido
          </h2>
          <div className="space-y-3 text-gray-700">
            <p>El archivo Excel debe contener las siguientes columnas:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li><strong>Nombre:</strong> Nombre del conductor</li>
              <li><strong>Dirección:</strong> Dirección completa de recogida</li>
              <li><strong>Terminal:</strong> Terminal de destino (ej: Terminal A, Terminal B)</li>
              <li><strong>Hora:</strong> Hora de recogida programada (opcional)</li>
            </ul>
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
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
