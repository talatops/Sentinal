import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import {
  HomeIcon,
  ShieldExclamationIcon,
  DocumentTextIcon,
  ArrowRightOnRectangleIcon,
  KeyIcon,
} from '@heroicons/react/24/outline';

const Layout = ({ children }) => {
  const location = useLocation();
  const { logout, user } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon, id: 'dashboard-link' },
    { name: 'Threat Modeling', href: '/threats', icon: ShieldExclamationIcon, id: 'threats-link' },
    { name: 'Requirements', href: '/requirements', icon: DocumentTextIcon, id: 'requirements-link' },
    ...(user?.role === 'Admin' ? [{ name: 'API Tokens', href: '/api-tokens', icon: KeyIcon, id: 'api-tokens-link' }] : []),
  ];

  return (
    <div className="min-h-screen bg-cyber-darker">
      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-40 bg-cyber-dark border-r border-cyber-blue/20 transition-transform duration-300 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ width: '256px' }}
      >
        <div className="flex flex-col h-full">
          <div className="p-6 border-b border-cyber-blue/20">
            <h1 className="text-2xl font-bold text-cyber-blue">Sentinel</h1>
            <p className="text-xs text-gray-400">DevSecOps Framework</p>
          </div>
          
          <nav className="flex-1 p-4 space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  id={item.id}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-cyber-blue/20 text-cyber-blue border border-cyber-blue/30'
                      : 'text-gray-400 hover:text-white hover:bg-cyber-dark'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
          
          <div className="p-4 border-t border-cyber-blue/20">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm font-medium text-white">{user?.username}</p>
                <p className="text-xs text-gray-400">{user?.role}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="flex items-center gap-2 w-full px-4 py-2 text-gray-400 hover:text-white hover:bg-cyber-dark rounded-lg transition-colors"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div
        className={`transition-all duration-300 ${
          sidebarOpen ? 'ml-64' : 'ml-0'
        }`}
      >
        <div className="p-8">
          {children}
        </div>
      </div>

      {/* Toggle button */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="fixed top-4 left-4 z-50 p-2 bg-cyber-dark border border-cyber-blue/20 rounded-lg text-cyber-blue hover:bg-cyber-dark/80"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
    </div>
  );
};

export default Layout;

