export const autoAllocate = (vehicles, warehouses) => {
  const availableVehicles = vehicles.filter(v => v.status === 'AVAILABLE');
  const sortedWarehouses = [...warehouses].sort((a, b) => 
    (a.current_load / a.capacity) - (b.current_load / b.capacity)
  );

  const allocation = [];
  
  availableVehicles.forEach(vehicle => {
    const bestWarehouse = sortedWarehouses.find(warehouse => 
      (warehouse.capacity - warehouse.current_load) >= vehicle.volume
    );
    
    if (bestWarehouse) {
      allocation.push({
        vehicleId: vehicle.id,
        warehouseId: bestWarehouse.id,
        warehouseName: bestWarehouse.name,
        utilization: ((bestWarehouse.current_load + vehicle.volume) / bestWarehouse.capacity * 100).toFixed(1)
      });
    }
  });

  return allocation;
};