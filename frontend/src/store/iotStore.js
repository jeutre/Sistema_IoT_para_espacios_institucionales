import { create } from 'zustand';
import api from '../axiosConfig';

const useIotStore = create((set) => ({
  dispositivos: [],
  ocupacion: [],
  historialOcupacion: [],
  alertas: [],
  loading: false,
  error: null,

  fetchDispositivos: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get('/dispositivos/esp32/');
<<<<<<< HEAD
      // Manejar respuesta paginada de Django REST Framework (response.data.results)
      let data = response.data.results !== undefined ? response.data.results : response.data;
      if (!Array.isArray(data)) data = [];
=======
      const data = response.data.results !== undefined ? response.data.results : response.data;
>>>>>>> 279187066aac9c54dcb78600412b21d320b04528
      set({ dispositivos: data, loading: false });
    } catch (err) {
      console.error('Error al cargar dispositivos:', err);
      set({ dispositivos: [], loading: false, error: 'No se pudieron cargar los dispositivos.' });
    }
  },

<<<<<<< HEAD
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
=======
  // HU-10: estado de ocupacion en tiempo real, un registro por dispositivo
  fetchOcupacion: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get('/ocupacion/tiempo-real/');
      set({ ocupacion: response.data, loading: false });
    } catch (err) {
      console.error('Error al cargar ocupacion:', err);
      set({ ocupacion: [], loading: false, error: 'No se pudo cargar la ocupacion.' });
    }
  },

  // HU-11: historial de ocupacion con filtros (dispositivo, desde, hasta)
  fetchHistorialOcupacion: async (filtros = {}) => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams();
      if (filtros.dispositivo) params.append('dispositivo', filtros.dispositivo);
      if (filtros.desde) params.append('desde', filtros.desde);
      if (filtros.hasta) params.append('hasta', filtros.hasta);
      const response = await api.get(`/ocupacion/?${params.toString()}`);
      const data = response.data.results !== undefined ? response.data.results : response.data;
      set({ historialOcupacion: data, loading: false });
    } catch (err) {
      console.error('Error al cargar historial:', err);
      set({ historialOcupacion: [], loading: false, error: 'No se pudo cargar el historial.' });
>>>>>>> 279187066aac9c54dcb78600412b21d320b04528
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
<<<<<<< HEAD
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
=======
      console.error('Error al cargar alertas:', err);
      set({ alertas: [], loading: false, error: 'No se pudieron cargar las alertas.' });
>>>>>>> 279187066aac9c54dcb78600412b21d320b04528
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