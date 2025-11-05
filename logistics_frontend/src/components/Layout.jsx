import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import VehicleList from './vehicles/VehicleList';
import DriverList from './vehicles/DriverList';
import WarehouseList from './warehouses/WarehouseList';


const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'warehouses':
        return <WarehouseList />;
      case 'vehicles':
        return <VehicleList />;
      case 'drivers':
        return <DriverList />;
      case 'dashboard':
      default:
        return <WarehouseList />;
    }
  };

  const getTabClass = (tabName) => {
    return `px-4 py-2 rounded-lg font-medium transition-all duration-200 ${activeTab === tabName
      ? 'bg-blue-600 text-white shadow-lg transform scale-105'
      : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
      }`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow-lg border-b border-blue-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center space-x-4">
              <div className="bg-blue-600 text-white p-2 rounded-xl">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Logistics System</h1>
                <p className="text-sm text-gray-500">Управление логистикой</p>
              </div>
            </div>

            <nav className="flex items-center space-x-2">

              <button onClick={() => setActiveTab('warehouses')} className={getTabClass('warehouses')}>
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  <span>Склады</span>
                </div>
              </button>

              <button onClick={() => setActiveTab('vehicles')} className={getTabClass('vehicles')}>
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0" />
                  </svg>
                  <span>Транспорт</span>
                </div>
              </button>

              <button onClick={() => setActiveTab('drivers')} className={getTabClass('drivers')}>
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <span>Водители</span>
                </div>
              </button>
            </nav>

            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="font-semibold text-gray-800">{user?.first_name} {user?.last_name}</p>
                <p className="text-sm text-gray-500 capitalize">{user?.role?.toLowerCase()}</p>
              </div>
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </div>
              <button
                onClick={logout}
                className="bg-gradient-to-r from-red-500 to-pink-600 text-white px-4 py-2 rounded-lg hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              >
                Выйти
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl border border-white/20 p-8">
          {renderContent()}
        </div>
      </main>
    </div>
  );
};

export default Layout;