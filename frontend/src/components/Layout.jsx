import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import {
  HomeIcon,
  ShieldExclamationIcon,
  DocumentTextIcon,
  ArrowRightOnRectangleIcon,
  KeyIcon,
  Bars3Icon,
  XMarkIcon,
} from "@heroicons/react/24/outline";

const Layout = ({ children }) => {
  const location = useLocation();
  const { logout, user } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navigation = [
    { name: "Dashboard", href: "/", icon: HomeIcon, id: "dashboard-link" },
    {
      name: "Threat Modeling",
      href: "/threats",
      icon: ShieldExclamationIcon,
      id: "threats-link",
    },
    {
      name: "Requirements",
      href: "/requirements",
      icon: DocumentTextIcon,
      id: "requirements-link",
    },
    ...(user?.role === "Admin"
      ? [
          {
            name: "API Tokens",
            href: "/api-tokens",
            icon: KeyIcon,
            id: "api-tokens-link",
          },
        ]
      : []),
  ];

  return (
    <div className="min-h-screen bg-cyber-darker">
      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-40 bg-cyber-dark border-r border-cyber-blue/20 transition-transform duration-300 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        style={{ width: "256px" }}
      >
        <div className="flex flex-col h-full">
          {/* Header with hamburger button */}
          <div className="p-6 border-b border-cyber-blue/20 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-cyber-blue">Sentinel</h1>
              <p className="text-xs text-gray-400">DevSecOps Framework</p>
            </div>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 text-cyber-blue hover:text-white hover:bg-cyber-blue/10 rounded-lg transition-all duration-200"
              aria-label="Toggle sidebar"
            >
              {sidebarOpen ? (
                <XMarkIcon className="w-5 h-5 transition-transform duration-200" />
              ) : (
                <Bars3Icon className="w-5 h-5 transition-transform duration-200" />
              )}
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  id={item.id}
                  className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 ${
                    isActive
                      ? "bg-cyber-blue/20 text-cyber-blue border border-cyber-blue/30 shadow-[0_0_8px_rgba(0,217,255,0.3)]"
                      : "text-gray-400 hover:text-white hover:bg-cyber-dark/50 hover:border hover:border-cyber-blue/10"
                  }`}
                >
                  <item.icon
                    className={`w-5 h-5 flex-shrink-0 ${isActive ? "text-cyber-blue" : ""}`}
                  />
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-cyber-blue/20">
            <div className="mb-3">
              <p className="text-sm font-semibold text-white">
                {user?.username}
              </p>
              <p className="text-xs text-gray-400 mt-0.5">{user?.role}</p>
            </div>
            <button
              onClick={logout}
              className="flex items-center gap-2 w-full px-4 py-2.5 text-gray-400 hover:text-white hover:bg-cyber-dark/50 rounded-lg transition-all duration-200 border border-transparent hover:border-cyber-blue/10"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div
        className={`transition-all duration-300 ${
          sidebarOpen ? "ml-64" : "ml-0"
        }`}
      >
        <div className="p-8">{children}</div>
      </div>

      {/* Toggle button - visible when sidebar is closed */}
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="fixed top-4 left-4 z-50 p-2.5 bg-cyber-dark border border-cyber-blue/20 rounded-lg text-cyber-blue hover:bg-cyber-blue/10 hover:border-cyber-blue/40 transition-all duration-200 shadow-lg"
          aria-label="Open sidebar"
        >
          <Bars3Icon className="w-6 h-6" />
        </button>
      )}
    </div>
  );
};

export default Layout;
