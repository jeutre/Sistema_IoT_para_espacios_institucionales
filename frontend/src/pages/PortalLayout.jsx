import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import ThemeToggle from '../components/ThemeToggle';
import './PortalLayout.css';

const PortalLayout = () => {
  const logout = useAuthStore((state) => state.logout);

  return (
    <div className="portal-wrapper">
      <aside className="portal-sidebar glass-container">
        <h2 className="sidebar-brand">IoT Inst.</h2>
        <nav className="sidebar-nav">
          <NavLink to="/dashboard" end className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
            Dashboard Principal
          </NavLink>
          <NavLink to="/dashboard/perfil" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
            Perfil
          </NavLink>
          <NavLink to="/dashboard/dispositivos" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
            Dispositivos ESP32
          </NavLink>
          <NavLink to="/dashboard/ocupacion" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
            Monitoreo Ocupación
          </NavLink>
          <NavLink to="/dashboard/alertas" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
            Alertas IoT
          </NavLink>
          
          {/* Separador para Admin */}
          <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', margin: '1rem 0' }}></div>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8', paddingLeft: '1.2rem', textTransform: 'uppercase' }}>Administración</span>
          
          <NavLink to="/dashboard/reportes" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
            Reportes
          </NavLink>
          <NavLink to="/dashboard/auditoria" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
            Auditoría
          </NavLink>
        </nav>
        
        <div className="sidebar-footer">
          <ThemeToggle />
          <button className="btn-secondary logout-btn" onClick={() => logout()}>
            Cerrar Sesión
          </button>
        </div>
      </aside>

      <main className="portal-content">
        <Outlet />
      </main>
    </div>
  );
};

export default PortalLayout;
