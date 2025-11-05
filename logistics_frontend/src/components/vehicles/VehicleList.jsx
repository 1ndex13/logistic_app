import React, { useState, useEffect } from 'react';
import api from '../../utils/api';

const VehicleList = () => {
  const [state, setState] = useState({
    vehicles: [], loading: true, error: '', showForm: false, editingVehicle: null
  });
  const [formData, setFormData] = useState({
    license_plate: '', model: '', vehicle_type: 'Грузовик', capacity: '', volume: '', year: '', vin: ''
  });

  useEffect(() => { fetchVehicles(); }, []);

  const fetchVehicles = async () => {
    try {
      const response = await api.get('/vehicles/vehicles/');
      const data = Array.isArray(response.data) ? response.data : response.data?.results || [];
      setState(prev => ({ ...prev, vehicles: data, error: '' }));
    } catch (err) {
      setState(prev => ({ ...prev, error: 'Не удалось загрузить данные транспорта.', vehicles: [] }));
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (state.editingVehicle) {
        await api.put(`/vehicles/vehicles/${state.editingVehicle.id}/`, formData);
      } else {
        await api.post('/vehicles/vehicles/', formData);
      }
      fetchVehicles();
      setState(prev => ({ ...prev, showForm: false, editingVehicle: null }));
      setFormData({ license_plate: '', model: '', vehicle_type: 'Грузовик', capacity: '', volume: '', year: '', vin: '' });
    } catch (error) {
      console.error('Error saving vehicle:', error);
    }
  };

  const handleEdit = (vehicle) => {
    setFormData({
      license_plate: vehicle.license_plate,
      model: vehicle.model,
      vehicle_type: vehicle.vehicle_type,
      capacity: vehicle.capacity,
      volume: vehicle.volume,
      year: vehicle.year,
      vin: vehicle.vin || ''
    });
    setState(prev => ({ ...prev, showForm: true, editingVehicle: vehicle }));
  };

  const handleDelete = async (vehicleId) => {
    if (window.confirm('Вы уверены, что хотите удалить это транспортное средство?')) {
      try {
        await api.delete(`/vehicles/vehicles/${vehicleId}/`);
        fetchVehicles();
      } catch (error) {
        console.error('Error deleting vehicle:', error);
      }
    }
  };

  const updateStatus = async (vehicleId, status) => {
    try {
      await api.patch(`/vehicles/vehicles/${vehicleId}/`, { status });
      fetchVehicles();
    } catch (error) {
      console.error('Error updating vehicle status:', error);
    }
  };

  const { vehicles, loading, error, showForm, editingVehicle } = state;
  const setShowForm = (show) => setState(prev => ({ ...prev, showForm: show, editingVehicle: show ? prev.editingVehicle : null }));

  if (loading) return <div className="text-center">Загрузка...</div>;

  const statusStyles = {
    AVAILABLE: 'bg-green-100 text-green-800',
    IN_USE: 'bg-yellow-100 text-yellow-800',
    MAINTENANCE: 'bg-blue-100 text-blue-800',
    BROKEN: 'bg-red-100 text-red-800'
  };

  const statusLabels = {
    AVAILABLE: 'Доступен',
    IN_USE: 'В работе',
    MAINTENANCE: 'На обслуживании',
    BROKEN: 'Сломан'
  };

  const formFields = [
    { type: 'text', placeholder: 'Госномер', field: 'license_plate', required: true },
    { type: 'text', placeholder: 'Модель', field: 'model', required: true },
    { type: 'number', placeholder: 'Грузоподъемность (т)', field: 'capacity', required: true },
    { type: 'number', placeholder: 'Объем (м³)', field: 'volume', required: true },
    { type: 'number', placeholder: 'Год выпуска', field: 'year', required: true },
    { type: 'text', placeholder: 'VIN (опционально)', field: 'vin', required: false }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Транспортные средства</h1>
        <button onClick={() => setState(prev => ({ ...prev, showForm: true, editingVehicle: null }))} 
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          Добавить транспорт
        </button>
      </div>

      {error && <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">{error}</div>}

      {showForm && (
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">
              {editingVehicle ? 'Редактировать транспорт' : 'Добавить транспорт'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              {formFields.map(({ type, placeholder, field, required }) => (
                <input key={field} type={type} placeholder={placeholder} value={formData[field]}
                  onChange={e => setFormData(prev => ({...prev, [field]: e.target.value}))}
                  className="w-full p-2 border rounded" required={required} />
              ))}
              
              <select value={formData.vehicle_type} onChange={e => setFormData(prev => ({...prev, vehicle_type: e.target.value}))} 
                className="w-full p-2 border rounded">
                <option value="Грузовик">Грузовик</option>
                <option value="VAN">Фургон</option>
                <option value="TRAILER">Прицеп</option>
                <option value="SPECIAL">Спецтранспорт</option>
              </select>
              
              <div className="flex space-x-2">
                <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded flex-1">
                  {editingVehicle ? 'Обновить' : 'Сохранить'}
                </button>
                <button type="button" onClick={() => setShowForm(false)} 
                  className="bg-gray-500 text-white px-4 py-2 rounded flex-1">
                  Отмена
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {vehicles.map(vehicle => (
          <div key={vehicle.id} className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-semibold text-lg">{vehicle.model}</h3>
                <p className="text-gray-600">{vehicle.license_plate}</p>
              </div>
              <div className="flex space-x-1">
                <button onClick={() => handleEdit(vehicle)}
                  className="text-blue-600 hover:text-blue-800 text-sm px-2 py-1 rounded hover:bg-blue-50">
                  Редактировать
                </button>
                <button onClick={() => handleDelete(vehicle.id)}
                  className="text-red-600 hover:text-red-800 text-sm px-2 py-1 rounded hover:bg-red-50">
                  Удалить
                </button>
              </div>
            </div>
            
            <div className="space-y-1">
              <p>Тип: {vehicle.vehicle_type}</p>
              <p>Грузоподъемность: {vehicle.capacity} т</p>
              <p>Объем: {vehicle.volume} м³</p>
              <p>Статус: <span className={`ml-2 px-2 py-1 rounded text-xs ${statusStyles[vehicle.status] || 'bg-gray-100 text-gray-800'}`}>
                {statusLabels[vehicle.status] || vehicle.status}
              </span></p>
            </div>
            
            <div className="mt-3">
              <select value={vehicle.status} onChange={e => updateStatus(vehicle.id, e.target.value)} 
                className="w-full p-1 border rounded text-sm">
                {Object.entries(statusLabels).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
          </div>
        ))}
      </div>

      {!vehicles.length && <div className="text-center py-8 text-gray-500">Нет данных о транспортных средствах</div>}
    </div>
  );
};

export default VehicleList;