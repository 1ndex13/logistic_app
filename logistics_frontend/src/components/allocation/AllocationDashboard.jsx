import React, { useState, useEffect } from 'react';
import api from '../../utils/api';

const AllocationDashboard = () => {
  const [vehicles, setVehicles] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedVehicle, setSelectedVehicle] = useState(null);

  useEffect(() => {
    fetchAllocationData();
  }, []);

  const fetchAllocationData = async () => {
    try {
      const [vehiclesRes, warehousesRes] = await Promise.all([
        api.get('/vehicles/vehicles/'),
        api.get('/warehouses/warehouses/')
      ]);
      
      console.log('Vehicles data:', vehiclesRes.data);
      console.log('Warehouses data:', warehousesRes.data);
      
      setVehicles(vehiclesRes.data.results || vehiclesRes.data);
      setWarehouses(warehousesRes.data.results || warehousesRes.data);
    } catch (error) {
      console.error('Error fetching allocation data:', error);
    } finally {
      setLoading(false);
    }
  };

  const freeVehicleAndWarehouse = async (vehicleId, warehouseId = null) => {
    try {
      const vehicle = vehicles.find(v => v.id === vehicleId);
      if (!vehicle) {
        alert('Транспорт не найден');
        return;
      }

      const targetWarehouseId = warehouseId || vehicle.current_warehouse;
      
      if (targetWarehouseId) {
        const warehouse = warehouses.find(w => w.id === targetWarehouseId);
        if (warehouse) {

          const newLoad = Math.max(0, parseFloat(warehouse.current_load) - parseFloat(vehicle.volume));
          console.log(`Updating warehouse ${warehouse.id}: current_load from ${warehouse.current_load} to ${newLoad}`);
          
          await api.patch(`/warehouses/warehouses/${warehouse.id}/`, {
            current_load: newLoad
          });
        }
      }

      console.log(`Freeing vehicle ${vehicle.id}: status to AVAILABLE, current_warehouse to null`);
      await api.patch(`/vehicles/vehicles/${vehicle.id}/`, {
        status: 'AVAILABLE',
        current_warehouse: null
      });

      fetchAllocationData();
      alert(`Транспорт ${vehicle.license_plate} освобожден`);
    } catch (error) {
      console.error('Error in freeVehicleAndWarehouse:', error);
      alert('Ошибка при освобождении транспорта');
    }
  };

  const unloadWarehouse = async (warehouseId) => {
    if (!window.confirm('Вы уверены, что хотите полностью разгрузить этот склад? Весь транспорт будет освобожден.')) {
      return;
    }

    try {
      const warehouse = warehouses.find(w => w.id === warehouseId);
      if (!warehouse) {
        alert('Склад не найден');
        return;
      }

      const vehiclesOnWarehouse = vehicles.filter(v => v.current_warehouse === warehouseId);
      console.log(`Vehicles on warehouse ${warehouseId}:`, vehiclesOnWarehouse);

      for (let vehicle of vehiclesOnWarehouse) {
        await api.patch(`/vehicles/vehicles/${vehicle.id}/`, {
          status: 'AVAILABLE',
          current_warehouse: null
        });
        console.log(`Freed vehicle ${vehicle.id}`);
      }


      await api.patch(`/warehouses/warehouses/${warehouseId}/`, {
        current_load: 0
      });

      fetchAllocationData();
      alert(`Склад "${warehouse.name}" разгружен! Освобождено ${vehiclesOnWarehouse.length} транспортных средств.`);
    } catch (error) {
      console.error('Error unloading warehouse:', error);
      alert('Ошибка при разгрузке склада');
    }
  };

  const autoAllocateAll = async () => {
    try {
      const availableVehicles = vehicles.filter(v => v.status === 'AVAILABLE');
      const sortedWarehouses = [...warehouses].sort((a, b) => 
        (a.current_load / a.capacity) - (b.current_load / b.capacity)
      );

      let allocatedCount = 0;

      for (let vehicle of availableVehicles) {
        const bestWarehouse = sortedWarehouses.find(warehouse => 
          (warehouse.capacity - warehouse.current_load) >= vehicle.volume
        );
        
        if (bestWarehouse) {
          const newLoad = parseFloat(bestWarehouse.current_load) + parseFloat(vehicle.volume);
          
          await api.patch(`/warehouses/warehouses/${bestWarehouse.id}/`, {
            current_load: newLoad
          });

          await api.patch(`/vehicles/vehicles/${vehicle.id}/`, {
            status: 'IN_USE',
            current_warehouse: bestWarehouse.id
          });

          allocatedCount++;
        }
      }
      
      fetchAllocationData();
      alert(`Автораспределение завершено! Распределено ${allocatedCount} из ${availableVehicles.length} машин`);
    } catch (error) {
      console.error('Error in auto allocation:', error);
      alert('Ошибка при автораспределении');
    }
  };

  const allocateVehicleToWarehouse = async (vehicleId, warehouseId) => {
    try {
      const vehicle = vehicles.find(v => v.id === vehicleId);
      const warehouse = warehouses.find(w => w.id === warehouseId);

      if (!vehicle || !warehouse) {
        alert('Ошибка: не найдены транспорт или склад');
        return;
      }

      const newLoad = parseFloat(warehouse.current_load) + parseFloat(vehicle.volume);
      if (newLoad > warehouse.capacity) {
        alert(`Недостаточно места на складе! Свободно: ${warehouse.capacity - warehouse.current_load} м³, требуется: ${vehicle.volume} м³`);
        return;
      }

      await api.patch(`/warehouses/warehouses/${warehouseId}/`, {
        current_load: newLoad
      });

      await api.patch(`/vehicles/vehicles/${vehicleId}/`, {
        status: 'IN_USE',
        current_warehouse: warehouseId
      });

      fetchAllocationData();
      setSelectedVehicle(null);
      
      alert(`Транспорт ${vehicle.license_plate} распределен на склад "${warehouse.name}"`);
    } catch (error) {
      console.error('Error allocating vehicle:', error);
      alert('Ошибка при распределении транспорта');
    }
  };

  if (loading) return <div className="text-center">Загрузка...</div>;

  const availableVehicles = vehicles.filter(v => v.status === 'AVAILABLE');
  const busyVehicles = vehicles.filter(v => v.status === 'IN_USE');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Распределение транспорта</h1>
        <div className="flex space-x-4">
          <div className="text-sm text-gray-500 mt-2">
            {availableVehicles.length} машин доступно | {busyVehicles.length} занято | {warehouses.length} складов
          </div>
          <button 
            onClick={autoAllocateAll}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-900 transition-all duration-200"
          >
            Автораспределение
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Доступный транспорт</h2>
          <div className="space-y-3">
            {availableVehicles.map(vehicle => (
              <div key={vehicle.id} className="flex justify-between items-center p-3 border rounded-lg hover:bg-gray-50">
                <div className="flex-1">
                  <div className="font-medium">{vehicle.model}</div>
                  <div className="text-sm text-gray-500">{vehicle.license_plate}</div>
                  <div className="text-sm">Грузоподъемность: {vehicle.capacity}т | Объем: {vehicle.volume} м³</div>
                </div>
                <div className="flex space-x-2">
                  <button 
                    onClick={() => setSelectedVehicle(vehicle.id)}
                    className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-all duration-200"
                  >
                    Распределить
                  </button>
                </div>
              </div>
            ))}
            {availableVehicles.length === 0 && (
              <div className="text-center py-4 text-gray-500">
                Нет доступного транспорта
              </div>
            )}
          </div>

          <div className="mt-6">
            <h2 className="text-xl font-semibold mb-4">Занятый транспорт</h2>
            <div className="space-y-3">
              {busyVehicles.map(vehicle => {
                const assignedWarehouse = warehouses.find(w => w.id === vehicle.current_warehouse);
                return (
                  <div key={vehicle.id} className="flex justify-between items-center p-3 border rounded-lg bg-gray-50">
                    <div className="flex-1">
                      <div className="font-medium">{vehicle.model}</div>
                      <div className="text-sm text-gray-500">{vehicle.license_plate}</div>
                      <div className="text-sm">
                        На складе: {assignedWarehouse ? assignedWarehouse.name : 'Не назначен'}
                      </div>
                      <div className="text-sm">Объем: {vehicle.volume} м³</div>
                    </div>
                    <button 
                      onClick={() => freeVehicleAndWarehouse(vehicle.id)}
                      className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition-all duration-200"
                    >
                      Освободить
                    </button>
                  </div>
                );
              })}
              {busyVehicles.length === 0 && (
                <div className="text-center py-4 text-gray-500">
                  Нет занятого транспорта
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Склады и загрузка</h2>
          <div className="space-y-4">
            {warehouses.map(warehouse => {
              const utilization = warehouse.capacity > 0 
                ? (warehouse.current_load / warehouse.capacity * 100).toFixed(1)
                : 0;
              
              const vehiclesOnWarehouse = vehicles.filter(v => v.current_warehouse === warehouse.id);
              
              return (
                <div key={warehouse.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-medium">{warehouse.name}</h3>
                      <p className="text-sm text-gray-500">{warehouse.address}</p>
                    </div>
                    <div className={`px-2 py-1 rounded text-xs ${
                      utilization > 80 ? 'bg-red-100 text-red-800' :
                      utilization > 60 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      Загруженность: {utilization}%
                    </div>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                    <div 
                      className={`h-2 rounded-full ${
                        utilization > 80 ? 'bg-red-600' :
                        utilization > 60 ? 'bg-yellow-600' :
                        'bg-green-600'
                      }`}
                      style={{ width: `${utilization}%` }}
                    ></div>
                  </div>
                  
                  <div className="flex justify-between text-sm mb-3">
                    <span>Свободно: {warehouse.capacity - warehouse.current_load} м³</span>
                    <span>Всего: {warehouse.capacity} м³</span>
                  </div>

                  <div className="flex justify-between items-center text-sm mb-3">
                    <span className="text-gray-600">
                      Транспорта на складе: {vehiclesOnWarehouse.length}
                    </span>
                  </div>

                  {selectedVehicle && (
                    <button
                      onClick={() => allocateVehicleToWarehouse(selectedVehicle, warehouse.id)}
                      className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-all duration-200 mb-2"
                    >
                      Назначить сюда
                    </button>
                  )}

                  <button
                    onClick={() => unloadWarehouse(warehouse.id)}
                    disabled={warehouse.current_load === 0 && vehiclesOnWarehouse.length === 0}
                    className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-900 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {warehouse.current_load === 0 && vehiclesOnWarehouse.length === 0 ? 'Склад пуст' : 'Разгрузить склад'}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {selectedVehicle && (
        <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-blue-600 text-white px-6 py-3 rounded-lg shadow-lg">
          <div className="flex items-center space-x-4">
            <span>
              Выбран транспорт: {vehicles.find(v => v.id === selectedVehicle)?.license_plate} 
              ({vehicles.find(v => v.id === selectedVehicle)?.volume} м³)
            </span>
            <button 
              onClick={() => setSelectedVehicle(null)}
              className="bg-white text-blue-600 px-2 py-1 rounded text-sm hover:bg-gray-100 transition-all duration-200"
            >
              Отмена
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AllocationDashboard;