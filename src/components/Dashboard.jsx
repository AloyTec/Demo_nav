import React, { useState } from 'react';
import FileUpload from './FileUpload';
import axios from 'axios';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '../config/api';

const Dashboard = ({ onDataUploaded, onOptimized, routeData }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleFileUpload = async (file) => {
    setUploadedFile(file);
    setLoading(true);
    setError(null);

    try {
      // Convert file to base64
      const reader = new FileReader();
      reader.onload = async () => {
        const base64Content = reader.result.split(',')[1]; // Remove data:*/*;base64, prefix

        try {
          // Upload and parse file
          const response = await axios.post(`${API_BASE_URL}/api/upload`, {
            file_content: base64Content,
            filename: file.name
          });

          onDataUploaded(response.data);

          // Automatically trigger optimization
          await handleOptimize(response.data);

        } catch (err) {
          setError(err.response?.data?.error || 'Error al procesar el archivo');
          setLoading(false);
        }
      };

      reader.onerror = () => {
        setError('Error al leer el archivo');
        setLoading(false);
      };

      reader.readAsDataURL(file);

    } catch (err) {
      setError(err.message || 'Error al procesar el archivo');
      setLoading(false);
    }
  };

  const handleOptimize = async (data) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/optimize`, data || routeData);
      onOptimized(response.data);
      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Error al optimizar rutas');
      setLoading(false);
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

        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-lg p-4 md:p-8 mb-6">
          <FileUpload onFileUpload={handleFileUpload} disabled={loading} />

          {loading && (
            <div className="mt-6 flex flex-col md:flex-row items-center justify-center gap-3 text-blue-600">
              <Loader2 className="w-6 h-6 animate-spin" />
              <span className="text-sm md:text-lg font-semibold text-center">Procesando y optimizando rutas...</span>
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
