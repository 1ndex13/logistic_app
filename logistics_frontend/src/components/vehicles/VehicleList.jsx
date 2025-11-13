import React, { useState, useEffect } from 'react';
import api from '../../utils/api';
import VehicleUpload from './VehicleUpload';

const VehicleList = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [stats, setStats] = useState({});

  const fetchVehicles = async () => {
    try {
      const response = await api.get('/vehicles/vehicles/');
      setVehicles(Array.isArray(response.data) ? response.data : response.data.results || []);
    } catch (err) {
      setError('Не удалось загрузить данные транспорта');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/vehicles/vehicles/stats/');
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  useEffect(() => {
    fetchVehicles();
    fetchStats();
  }, []);

  const handleUploadComplete = () => {
    fetchVehicles();
    fetchStats();
  };

  if (loading) return <div className="text-center py-4">Загрузка транспорта...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Транспортные средства</h1>
          <div className="flex space-x-4 mt-2 text-sm text-gray-600">
            <span>Всего: {stats.total_vehicles || 0}</span>
            <span>Доступно: {stats.available_vehicles || 0}</span>
            <span>В работе: {stats.in_use_vehicles || 0}</span>
          </div>
        </div>
        <button 
          onClick={() => setShowForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Добавить транспорт
        </button>
      </div>

      <VehicleUpload onUploadComplete={handleUploadComplete} />

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {vehicles.map(vehicle => (
          <div key={vehicle.id} className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold text-lg">{vehicle.model}</h3>
              <span className={`px-2 py-1 rounded text-xs ${
                vehicle.status === 'AVAILABLE' ? 'bg-green-100 text-green-800' :
                vehicle.status === 'IN_USE' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {vehicle.status === 'AVAILABLE' ? 'Доступен' :
                 vehicle.status === 'IN_USE' ? 'В работе' : 'Неактивен'}
              </span>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Госномер:</span>
                <span className="font-medium">{vehicle.license_plate}</span>
              </div>
              
              {vehicle.cargo_recipient && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Грузополучатель:</span>
                  <span className="font-medium">{vehicle.cargo_recipient}</span>
                </div>
              )}
              
              {vehicle.current_warehouse_details && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Склад:</span>
                  <span className="font-medium">{vehicle.current_warehouse_details.name}</span>
                </div>
              )}
              
              {vehicle.cargo_volume && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Объем ТМЦ:</span>
                  <span className="font-medium">{vehicle.cargo_volume} т</span>
                </div>
              )}
              
              {vehicle.cargo_description && (
                <div>
                  <span className="text-gray-600">Груз:</span>
                  <p className="font-medium mt-1">{vehicle.cargo_description}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {vehicles.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          Нет данных о транспортных средствах. Загрузите Excel файл или добавьте транспорт вручную.
        </div>
      )}
    </div>
  );
};

export default VehicleList;