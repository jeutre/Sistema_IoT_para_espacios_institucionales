import React, { useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import ThemeToggle from '../components/ThemeToggle';
import './PortalLayout.css';

const PortalLayout = () => {
  const logout = useAuthStore((state) => state.logout);
  const user = useAuthStore((state) => state.user);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const location = useLocation();

  const navItems = [
    { to: '/dashboard', icon: 'grid', label: 'Dashboard', end: true },
    { to: '/dashboard/perfil', icon: 'user', label: 'Perfil' },
    { to: '/dashboard/dispositivos', icon: 'cpu', label: 'ESP32' },
    { to: '/dashboard/ocupacion', icon: 'users', label: 'Ocupación' },
    { to: '/dashboard/alertas', icon: 'bell', label: 'Alertas IoT' },
  ];

  const adminItems = [
    { to: '/dashboard/reportes', icon: 'chart', label: 'Reportes' },
    { to: '/dashboard/auditoria', icon: 'shield', label: 'Auditoría' },
  ];

  const getIcon = (name) => {
    const icons = {
      grid: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>,
      user: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>,
      cpu: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M1 9h3M1 15h3M20 9h3M20 15h3"/></svg>,
      users: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>,
      bell: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>,
      chart: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>,
      shield: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
      logout: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>,
      burger: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>,
    };
    return icons[name] || null;
  };

  const pageTitle = {
    '/dashboard': 'Dashboard Principal',
    '/dashboard/perfil': 'Mi Perfil',
    '/dashboard/dispositivos': 'Dispositivos ESP32',
    '/dashboard/ocupacion': 'Monitoreo Ocupación',
    '/dashboard/alertas': 'Alertas IoT',
    '/dashboard/reportes': 'Reportes',
    '/dashboard/auditoria': 'Auditoría',
  };

  const currentTitle = Object.entries(pageTitle).find(([path]) => 
    location.pathname === path
  )?.[1] || 'Centro de Comando';

  return (
    <div className={`portal-wrapper ${sidebarCollapsed ? 'collapsed' : ''}`}>
      <aside className="portal-sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#00f0ff" strokeWidth="2">
              <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
              <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
              <line x1="6" y1="6" x2="6.01" y2="6" />
              <line x1="6" y1="18" x2="6.01" y2="18" />
            </svg>
            <span className="sidebar-brand-text">IoT Center</span>
          </div>
          <button className="sidebar-collapse-btn" onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
            {getIcon('burger')}
          </button>
        </div>

        <div className="sidebar-user">
          <div className="sidebar-avatar">
            {user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="sidebar-user-info">
            <span className="sidebar-user-name">{user?.username || 'Usuario'}</span>
            <span className="sidebar-user-role">Administrador</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <span className="nav-section-title">Navegación</span>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}
            >
              <span className="nav-icon">{getIcon(item.icon)}</span>
              <span className="nav-label">{item.label}</span>
              {item.label === 'Alertas IoT' && (
                <span className="nav-badge">3</span>
              )}
            </NavLink>
          ))}

          <span className="nav-section-title">Administración</span>
          {adminItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}
            >
              <span className="nav-icon">{getIcon(item.icon)}</span>
              <span className="nav-label">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-footer-top">
            <ThemeToggle />
            <span className="sidebar-version">v2.0</span>
          </div>
          <button className="sidebar-logout" onClick={() => logout()}>
            <span className="nav-icon">{getIcon('logout')}</span>
            <span className="nav-label">Cerrar Sesión</span>
          </button>
        </div>
      </aside>

      <main className="portal-content">
        <div className="portal-topbar">
          <div className="topbar-left">
            <h2 className="topbar-title">{currentTitle}</h2>
          </div>
          <div className="topbar-right">
            <div className="topbar-status">
              <span className="topbar-dot"></span>
              Sistema Activo
            </div>
            <div className="topbar-time">
              {new Date().toLocaleTimeString('es-EC', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })}
            </div>
          </div>
        </div>
        <div className="portal-page">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default PortalLayout;