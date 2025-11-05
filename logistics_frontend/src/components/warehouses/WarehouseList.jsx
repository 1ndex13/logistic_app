import React, { useState, useEffect } from 'react';
import api from '../../utils/api';

const WarehouseList = () => {
  const [state, setState] = useState({
    warehouses: [], loading: true, error: '', showForm: false, editingWarehouse: null
  });
  const [formData, setFormData] = useState({
    name: '', address: '', capacity: '', current_load: '0', specialization: '', working_hours: ''
  });

  useEffect(() => { fetchWarehouses(); }, []);

  const fetchWarehouses = async () => {
    try {
      const response = await api.get('/warehouses/warehouses/');
      const data = Array.isArray(response.data) ? response.data : response.data?.results || [];
      setState(prev => ({ ...prev, warehouses: data, error: '' }));
    } catch (err) {
      setState(prev => ({ ...prev, error: 'Не удалось загрузить данные складов.', warehouses: [] }));
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (state.editingWarehouse) {
        await api.put(`/warehouses/warehouses/${state.editingWarehouse.id}/`, formData);
      } else {
        await api.post('/warehouses/warehouses/', formData);
      }
      fetchWarehouses();
      setState(prev => ({ ...prev, showForm: false, editingWarehouse: null }));
      setFormData({ name: '', address: '', capacity: '', current_load: '0', specialization: '', working_hours: '' });
    } catch (err) {
      console.error('Error saving warehouse:', err);
      alert('Ошибка при сохранении склада');
    }
  };

  const handleEdit = (warehouse) => {
    setFormData({
      name: warehouse.name,
      address: warehouse.address,
      capacity: warehouse.capacity,
      current_load: warehouse.current_load || '0',
      specialization: warehouse.specialization || '',
      working_hours: warehouse.working_hours || ''
    });
    setState(prev => ({ ...prev, showForm: true, editingWarehouse: warehouse }));
  };

  const handleDelete = async (warehouseId) => {
    if (window.confirm('Вы уверены, что хотите удалить этот склад?')) {
      try {
        await api.delete(`/warehouses/warehouses/${warehouseId}/`);
        fetchWarehouses();
      } catch (error) {
        console.error('Error deleting warehouse:', error);
      }
    }
  };

  const { warehouses, loading, error, showForm, editingWarehouse } = state;
  const setShowForm = (show) => setState(prev => ({ ...prev, showForm: show, editingWarehouse: show ? prev.editingWarehouse : null }));

  if (loading) return <div className="text-center py-4">Загрузка складов...</div>;

  const formFields = [
    { type: 'text', placeholder: 'Название склада', field: 'name', required: true },
    { type: 'textarea', placeholder: 'Адрес', field: 'address', required: true },
    { type: 'number', placeholder: 'Вместимость (м³)', field: 'capacity', required: true },
    { type: 'text', placeholder: 'Специализация', field: 'specialization', required: false },
    { type: 'text', placeholder: 'Режим работы', field: 'working_hours', required: false }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Склады</h1>
        <button onClick={() => setState(prev => ({ ...prev, showForm: true, editingWarehouse: null }))} 
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          Добавить склад
        </button>
      </div>

      {error && <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">{error}</div>}

      {showForm && (
        <div className="fixed inset-0 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">
              {editingWarehouse ? 'Редактировать склад' : 'Добавить склад'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              {formFields.map(({ type, placeholder, field, required }) => 
                type === 'textarea' ? (
                  <textarea key={field} placeholder={placeholder} value={formData[field]}
                    onChange={e => setFormData(prev => ({...prev, [field]: e.target.value}))}
                    className="w-full p-2 border rounded" required={required} rows="3" />
                ) : (
                  <input key={field} type={type} placeholder={placeholder} value={formData[field]}
                    onChange={e => setFormData(prev => ({...prev, [field]: e.target.value}))}
                    className="w-full p-2 border rounded" required={required} />
                )
              )}
              <div className="flex space-x-2">
                <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded flex-1">
                  {editingWarehouse ? 'Обновить' : 'Сохранить'}
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
        {warehouses.map(warehouse => (
          <div key={warehouse.id} className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-semibold text-lg">{warehouse.name}</h3>
                <p className="text-gray-600 text-sm">{warehouse.address}</p>
              </div>
              <div className="flex space-x-1">
                <button onClick={() => handleEdit(warehouse)}
                  className="text-blue-600 hover:text-blue-800 text-sm px-2 py-1 rounded hover:bg-blue-50">
                  Редактировать
                </button>
                <button onClick={() => handleDelete(warehouse.id)}
                  className="text-red-600 hover:text-red-800 text-sm px-2 py-1 rounded hover:bg-red-50">
                  Удалить
                </button>
              </div>
            </div>

            <div className="space-y-2">
              {[
                { label: 'Вместимость:', value: `${warehouse.capacity} м³` },
                { label: 'Загрузка:', value: `${warehouse.current_load} м³` },
                { label: 'Загруженность:', value: `${warehouse.utilization_percentage}%` },
                ...(warehouse.specialization ? [{ label: 'Специализация:', value: warehouse.specialization }] : []),
                ...(warehouse.working_hours ? [{ label: 'Режим работы:', value: warehouse.working_hours }] : [])
              ].map((item, index) => (
                <div key={index} className="flex justify-between">
                  <span>{item.label}</span>
                  <span className="font-medium">{item.value}</span>
                </div>
              ))}
            </div>

            <div className="mt-4 flex items-center space-x-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${warehouse.utilization_percentage}%` }}></div>
              </div>
              <span className={`px-2 py-1 rounded text-xs ${
                warehouse.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {warehouse.is_active ? 'Активен' : 'Неактивен'}
              </span>
            </div>
          </div>
        ))}
      </div>

      {!warehouses.length && <div className="text-center py-8 text-gray-500">Нет данных о складах</div>}
    </div>
  );
};

export default WarehouseList;