import React, { useState, useEffect } from 'react';
import api from '../../utils/api';

const DriverList = () => {
  const [state, setState] = useState({
    drivers: [], users: [], vehicles: [], loading: true, error: '', showForm: false, editingDriver: null
  });
  const [formData, setFormData] = useState({
    user: '', license_number: '', license_category: '', license_expiry: '', phone_number: '', vehicle: ''
  });

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [driversRes, usersRes, vehiclesRes] = await Promise.all([
        api.get('/vehicles/drivers/'),
        api.get('/auth/users/drivers/'),
        api.get('/vehicles/vehicles/')
      ]);

      const getData = (res) => Array.isArray(res.data) ? res.data : res.data?.results || [];

      setState(prev => ({
        ...prev,
        drivers: getData(driversRes),
        users: getData(usersRes),
        vehicles: getData(vehiclesRes),
        error: ''
      }));
    } catch (err) {
      setState(prev => ({ ...prev, error: 'Не удалось загрузить данные.' }));
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (state.editingDriver) {
        await api.put(`/vehicles/drivers/${state.editingDriver.id}/`, formData);
      } else {
        await api.post('/vehicles/drivers/', formData);
      }
      fetchData();
      setState(prev => ({ ...prev, showForm: false, editingDriver: null }));
      setFormData({ user: '', license_number: '', license_category: '', license_expiry: '', phone_number: '', vehicle: '' });
    } catch (error) {
      console.error('Error saving driver:', error);
    }
  };

  const handleEdit = (driver) => {
    setFormData({
      user: driver.user,
      license_number: driver.license_number,
      license_category: driver.license_category,
      license_expiry: driver.license_expiry,
      phone_number: driver.phone_number,
      vehicle: driver.vehicle || ''
    });
    setState(prev => ({ ...prev, showForm: true, editingDriver: driver }));
  };

  const handleDelete = async (driverId) => {
    if (window.confirm('Вы уверены, что хотите удалить этого водителя?')) {
      try {
        await api.delete(`/vehicles/drivers/${driverId}/`);
        fetchData();
      } catch (error) {
        console.error('Error deleting driver:', error);
      }
    }
  };

  const { drivers, users, vehicles, loading, error, showForm, editingDriver } = state;

  if (loading) return <div className="text-center">Загрузка...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Водители</h1>
        <button 
          onClick={() => setState(prev => ({ ...prev, showForm: true, editingDriver: null }))} 
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Добавить водителя
        </button>
      </div>

      {error && <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">{error}</div>}

      {showForm && (
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">
              {editingDriver ? 'Редактировать водителя' : 'Добавить водителя'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <select value={formData.user} onChange={e => setFormData(prev => ({...prev, user: e.target.value}))} className="w-full p-2 border rounded" required>
                <option value="">Выберите пользователя</option>
                {users.map(user => <option key={user.id} value={user.id}>{user.first_name} {user.last_name} ({user.username})</option>)}
              </select>
              <input type="text" placeholder="Номер водительского удостоверения" value={formData.license_number}
                onChange={e => setFormData(prev => ({...prev, license_number: e.target.value}))} className="w-full p-2 border rounded" required />
              <input type="text" placeholder="Категория прав" value={formData.license_category}
                onChange={e => setFormData(prev => ({...prev, license_category: e.target.value}))} className="w-full p-2 border rounded" required />
              <input type="date" placeholder="Срок действия прав" value={formData.license_expiry}
                onChange={e => setFormData(prev => ({...prev, license_expiry: e.target.value}))} className="w-full p-2 border rounded" required />
              <input type="text" placeholder="Номер телефона" value={formData.phone_number}
                onChange={e => setFormData(prev => ({...prev, phone_number: e.target.value}))} className="w-full p-2 border rounded" required />
              <select value={formData.vehicle} onChange={e => setFormData(prev => ({...prev, vehicle: e.target.value}))} className="w-full p-2 border rounded">
                <option value="">Без привязки к ТС</option>
                {vehicles.map(vehicle => <option key={vehicle.id} value={vehicle.id}>{vehicle.model} ({vehicle.license_plate})</option>)}
              </select>
              <div className="flex space-x-2">
                <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded flex-1">
                  {editingDriver ? 'Обновить' : 'Сохранить'}
                </button>
                <button 
                  type="button" 
                  onClick={() => setState(prev => ({ ...prev, showForm: false, editingDriver: null }))}
                  className="bg-gray-500 text-white px-4 py-2 rounded flex-1"
                >
                  Отмена
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {drivers.map(driver => (
          <div key={driver.id} className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-start">
              <h3 className="font-semibold text-lg">{driver.user_details?.first_name} {driver.user_details?.last_name}</h3>
              <div className="flex space-x-2">
                <button 
                  onClick={() => handleEdit(driver)}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  Редактировать
                </button>
                <button 
                  onClick={() => handleDelete(driver.id)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  Удалить
                </button>
              </div>
            </div>
            <p className="text-gray-600">{driver.license_number}</p>
            <div className="mt-2 space-y-1">
              <p>Категория: {driver.license_category}</p>
              <p>Телефон: {driver.phone_number}</p>
              <p>ТС: {driver.vehicle_details?.model || 'Не назначено'}</p>
              <p>Статус: <span className={`ml-2 px-2 py-1 rounded text-xs ${driver.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {driver.is_active ? 'Активен' : 'Неактивен'}
              </span></p>
            </div>
          </div>
        ))}
      </div>

      {!drivers.length && <div className="text-center py-8 text-gray-500">Нет данных о водителях</div>}
    </div>
  );
};

export default DriverList;