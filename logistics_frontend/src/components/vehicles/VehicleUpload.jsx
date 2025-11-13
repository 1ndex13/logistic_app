import React, { useState } from 'react';
import api from '../../utils/api';

const VehicleUpload = ({ onUploadComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [detailedErrors, setDetailedErrors] = useState([]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    setMessage('');
    setError('');
    setDetailedErrors([]);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/vehicles/vehicles/upload-excel/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMessage(`Успешно загружено ${response.data.vehicles_created} транспортных средств`);
      
      if (response.data.errors && response.data.errors.length > 0) {
        setDetailedErrors(response.data.errors);
        setError(`Обнаружены ошибки в ${response.data.errors.length} строках`);
      }

      if (onUploadComplete) {
        onUploadComplete();
      }
    } catch (err) {
      setError('Ошибка при загрузке файла: ' + (err.response?.data?.error || err.message));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">Загрузка транспорта из Excel</h2>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Выберите Excel файл
        </label>
        <input
          type="file"
          accept=".xlsx, .xls"
          onChange={handleFileUpload}
          disabled={uploading}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        <p className="text-xs text-gray-500 mt-1">
          Поддерживаются файлы .xlsx и .xls
        </p>
      </div>

      {uploading && (
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2">Загрузка и обработка файла...</span>
        </div>
      )}

      {message && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {message}
        </div>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {detailedErrors.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <h3 className="font-medium text-yellow-800 mb-2">Детали ошибок:</h3>
          <div className="max-h-40 overflow-y-auto">
            {detailedErrors.map((err, index) => (
              <div key={index} className="text-sm text-yellow-700 mb-1">
                {err}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-medium mb-2">Требования к файлу:</h3>
        <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
          <li>Файл должен содержать колонки: Наименование грузополучателей, Модель авто, Гос.номер, Номер склада, Наименование ТМЦ, Объемы ТМЦ</li>
          <li>Старые данные о транспорте будут удалены</li>
          <li>Поддерживается формат .xlsx и .xls</li>
          <li>Склады будут созданы автоматически если их нет в системе</li>
          <li>Числа с запятыми (1,896) автоматически конвертируются в формат с точками (1.896)</li>
        </ul>
      </div>
    </div>
  );
};

export default VehicleUpload;