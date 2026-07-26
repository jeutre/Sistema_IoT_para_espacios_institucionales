import { create } from 'zustand';
import api from '../axiosConfig';

const useIotStore = create((set) => ({
  dispositivos: [],
  ocupacion: [],
  alertas: [],
  loading: false,
  error: null,

  fetchDispositivos: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get('/dispositivos/esp32/');
      // Manejar respuesta paginada de Django REST Framework (response.data.results)
      let data = response.data.results !== undefined ? response.data.results : response.data;
      if (!Array.isArray(data)) data = [];
      set({ dispositivos: data, loading: false });
    } catch (err) {
      console.warn("No se pudo conectar a /api/v1/dispositivos/esp32/. Cargando datos de prueba.");
      set({
        dispositivos: [
          { id: 1, identificador: 'ESP32-A1', ip: '192.168.1.50', estado: 'conectado', laboratorio: { nombre: 'Lab de Redes' } },
          { id: 2, identificador: 'ESP32-A2', ip: '192.168.1.51', estado: 'desconectado', laboratorio: { nombre: 'Lab de Redes' } },
          { id: 3, identificador: 'ESP32-B1', ip: '192.168.1.52', estado: 'conectado', laboratorio: { nombre: 'Taller de Electrónica' } },
        ],
        loading: false
      });
    }
  },

  ocupacion: [],
  ocupacionTiempoReal: [],
  horasPico: null,
  
  fetchOcupacion: async (desde, hasta) => {
    set({ loading: true, error: null });
    try {
      let url = '/ocupacion/';
      if (desde && hasta) {
        url += `?desde=${desde}&hasta=${hasta}`;
      }
      const response = await api.get(url);
      let data = response.data.results !== undefined ? response.data.results : response.data;
      if (!Array.isArray(data)) data = [];
      set({ ocupacion: data, loading: false });
    } catch (err) {
      console.warn("Cargando datos de prueba para ocupación historial.");
      set({ loading: false });
    }
  },

  fetchOcupacionTiempoReal: async () => {
    try {
      const response = await api.get('/ocupacion/tiempo-real/');
      set({ ocupacionTiempoReal: response.data });
    } catch (err) {
      console.warn("Cargando datos de prueba para ocupación tiempo real.");
      set({
        ocupacionTiempoReal: [
          { dispositivo: 'ESP32-A1', laboratorio: 'Lab Redes', estado: 'ocupado', ultima_vez: new Date().toISOString() }
        ]
      });
    }
  },

  fetchHorasPico: async (desde, hasta) => {
    try {
      let url = '/ocupacion/horas-pico/';
      if (desde && hasta) {
        url += `?desde=${desde}&hasta=${hasta}`;
      }
      const response = await api.get(url);
      set({ horasPico: response.data });
    } catch (err) {
      console.warn("Cargando datos de prueba para horas pico.");
      set({ horasPico: { detalle_por_hora: [{ hora: 10, total_eventos_ocupado: 5 }, { hora: 14, total_eventos_ocupado: 8 }] } });
    }
  },

  equipos: [],
  equiposActivos: 0,
  equiposInactivos: 0,

  fetchEquipos: async () => {
    try {
      const response = await api.get('/equipos/');
      set({ equipos: response.data.results || response.data });
    } catch (err) {
      console.warn("Error fetching equipos.");
    }
  },

  createEquipo: async (equipo) => {
    try {
      const response = await api.post('/equipos/', equipo);
      set(state => ({ equipos: [...state.equipos, response.data] }));
    } catch (err) {
      console.error(err);
      throw err;
    }
  },

  updateEquipo: async (id, data) => {
    try {
      const response = await api.patch(`/equipos/${id}/`, data);
      set(state => ({
        equipos: state.equipos.map(eq => eq.id === id ? response.data : eq)
      }));
    } catch (err) {
      console.error(err);
      throw err;
    }
  },

  pingTodos: async () => {
    try {
      const response = await api.get('/equipos/ping-todos/');
      set({ 
        equiposActivos: response.data.total_activos,
        equiposInactivos: response.data.total_inactivos
      });
      // Refresh list to get updated states
      const listResp = await api.get('/equipos/');
      set({ equipos: listResp.data.results || listResp.data });
    } catch (err) {
      console.error("Error pinging todos:", err);
    }
  },

  fetchAlertas: async () => {
    set({ loading: true, error: null });
    try {
      // Only fetch active (unread) alerts by default
      const response = await api.get('/alertas/?leida=false');
      let data = response.data.results !== undefined ? response.data.results : response.data;
      if (!Array.isArray(data)) data = [];
      set({ alertas: data, loading: false });
    } catch (err) {
      console.warn("No se pudo conectar a /alertas/.");
      set({ alertas: [], loading: false, error: err.message });
    }
  },

  atenderAlerta: async (id) => {
    try {
      await api.patch(`/alertas/${id}/`, { leida: true });
      // Remove it from the local state
      set(state => ({
        alertas: state.alertas.filter(a => a.id !== id)
      }));
    } catch (err) {
      console.error("Error al atender alerta:", err);
    }
  },

  laboratorios: [],
  fetchLaboratorios: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get('/laboratorio/');
      const data = response.data.results !== undefined ? response.data.results : response.data;
      set({ laboratorios: data, loading: false });
    } catch (err) {
      console.warn("Cargando datos de prueba para laboratorios.");
      set({
        laboratorios: [
          { id: 1, nombre: 'Lab de Redes', ubicacion: 'Edificio A, Piso 2', capacidad: 30, activo: true },
          { id: 2, nombre: 'Taller de Electrónica', ubicacion: 'Edificio B, PB', capacidad: 20, activo: true },
        ],
        loading: false
      });
    }
  },
  
  createLaboratorio: async (labData) => {
    set({ loading: true, error: null });
    try {
      const response = await api.post('/laboratorio/', labData);
      set(state => ({ 
        laboratorios: [...state.laboratorios, response.data],
        loading: false 
      }));
      return true;
    } catch (err) {
      set({ error: 'Error al crear laboratorio', loading: false });
      return false;
    }
  },

  updateLaboratorio: async (id, labData) => {
    set({ loading: true, error: null });
    try {
      const response = await api.put(`/laboratorio/${id}/`, labData);
      set(state => ({
        laboratorios: state.laboratorios.map(l => l.id === id ? response.data : l),
        loading: false
      }));
      return true;
    } catch (err) {
      set({ error: 'Error al actualizar laboratorio', loading: false });
      return false;
    }
  }
}));

export default useIotStore;
