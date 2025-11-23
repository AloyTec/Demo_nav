import React, { useCallback, useState, useRef } from 'react';
import { Upload, FileSpreadsheet } from 'lucide-react';

const FileUpload = ({ onFileUpload, disabled }) => {
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls') || file.name.endsWith('.csv')) {
      onFileUpload(file);
    } else {
      alert('Por favor, sube un archivo Excel (.xlsx, .xls) o CSV');
    }
  };

  const handleButtonClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled && inputRef.current) {
      inputRef.current.click();
    }
  };

  return (
    <div>
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative border-3 border-dashed rounded-xl p-6 md:p-12 text-center transition-all ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input
          ref={inputRef}
          type="file"
          id="file-upload"
          accept=".xlsx,.xls,.csv"
          onChange={handleChange}
          disabled={disabled}
          className="hidden"
        />

        <div className="flex flex-col items-center">
          <div className="mb-4">
            {dragActive ? (
              <Upload className="w-12 h-12 md:w-16 md:h-16 text-blue-500 animate-bounce" />
            ) : (
              <FileSpreadsheet className="w-12 h-12 md:w-16 md:h-16 text-gray-400" />
            )}
          </div>

          <h3 className="text-base md:text-xl font-semibold text-gray-700 mb-2">
            {dragActive ? 'Suelta el archivo aquí' : 'Arrastra tu archivo Excel aquí'}
          </h3>

          <p className="text-sm md:text-base text-gray-500 mb-4">
            o haz clic para seleccionar
          </p>

          <button
            type="button"
            onClick={handleButtonClick}
            disabled={disabled}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 active:bg-blue-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm md:text-base touch-manipulation"
          >
            Seleccionar Archivo
          </button>

          <p className="text-xs md:text-sm text-gray-400 mt-4">
            Formatos aceptados: .xlsx, .xls, .csv
          </p>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
