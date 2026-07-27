import { create } from 'zustand';
import api from '../axiosConfig';

const useIotStore = create((set) => ({
  dispositivos: [],
  ocupacion: [],
  historialOcupacion: [],
  alertas: [],
  laboratorios: [],
  equipos: [],
  equiposActivos: 0,
  equiposInactivos: 0,
  horasPico: null,
  loading: false,
  error: null,

  fetchDispositivos: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get('/dispositivos/esp32/');
      const data = response.data?.results ?? response.data;
      set({
        dispositivos: Array.isArray(data) ? data : [],
        loading: false,
        error: null,
      });
    } catch (err) {
      console.error('Error al cargar dispositivos:', err);
      set({ dispositivos: [], loading: false, error: 'No se pudieron cargar los dispositivos.' });
    }
  },

  fetchOcupacion: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get('/ocupacion/tiempo-real/');
      const data = Array.isArray(response.data) ? response.data : [];
      set({ ocupacion: data, loading: false, error: null });
    } catch (err) {
      console.error('Error al cargar ocupacion:', err);
      set({ ocupacion: [], loading: false, error: 'No se pudo cargar la ocupacion.' });
    }
  },

  fetchHistorialOcupacion: async (filtros = {}) => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams();
      if (filtros.dispositivo) params.append('dispositivo', filtros.dispositivo);
      if (filtros.desde) params.append('desde', filtros.desde);
      if (filtros.hasta) params.append('hasta', filtros.hasta);
      const response = await api.get(`/ocupacion/?${params.toString()}`);
      const data = response.data?.results ?? response.data;
      set({
        historialOcupacion: Array.isArray(data) ? data : [],
        loading: false,
        error: null,
      });
    } catch (err) {
      console.error('Error al cargar historial:', err);
      set({ historialOcupacion: [], loading: false, error: 'No se pudo cargar el historial.' });
    }
  },

  fetchHorasPico: async (desde, hasta) => {
    set({ error: null });
    try {
      let url = '/ocupacion/horas-pico/';
      if (desde && hasta) {
        url += `?desde=${desde}&hasta=${hasta}`;
      }
      const response = await api.get(url);
      set({ horasPico: response.data ?? null });
    } catch (err) {
      console.error('Error al cargar horas pico:', err);
      set({ horasPico: null, error: 'No se pudieron cargar las horas pico.' });
    }
  },

  fetchEquipos: async () => {
    set({ error: null });
    try {
      const response = await api.get('/equipos/');
      const data = response.data?.results ?? response.data;
      set({ equipos: Array.isArray(data) ? data : [] });
    } catch (err) {
      console.error('Error al cargar equipos:', err);
      set({ equipos: [], error: 'No se pudieron cargar los equipos.' });
    }
  },

  createEquipo: async (equipo) => {
    try {
      const response = await api.post('/equipos/', equipo);
      set((state) => ({ equipos: [...state.equipos, response.data] }));
    } catch (err) {
      console.error(err);
      throw err;
    }
  },

  updateEquipo: async (id, data) => {
    try {
      const response = await api.patch(`/equipos/${id}/`, data);
      set((state) => ({
        equipos: state.equipos.map((eq) => (eq.id === id ? response.data : eq)),
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
        equiposInactivos: response.data.total_inactivos,
      });
      const listResp = await api.get('/equipos/');
      const data = listResp.data?.results ?? listResp.data;
      set({ equipos: Array.isArray(data) ? data : [] });
    } catch (err) {
      console.error('Error pinging todos:', err);
    }
  },

  fetchAlertas: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get('/alertas/?leida=false');
      const data = response.data?.results ?? response.data;
      set({
        alertas: Array.isArray(data) ? data : [],
        loading: false,
        error: null,
      });
    } catch (err) {
      console.error('Error al cargar alertas:', err);
      set({ alertas: [], loading: false, error: 'No se pudieron cargar las alertas.' });
    }
  },

  atenderAlerta: async (id) => {
    try {
      await api.patch(`/alertas/${id}/`, { leida: true });
      set((state) => ({
        alertas: state.alertas.filter((a) => a.id !== id),
      }));
    } catch (err) {
      console.error('Error al atender alerta:', err);
    }
  },

  fetchLaboratorios: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get('/laboratorio/');
      const data = response.data?.results ?? response.data;
      set({
        laboratorios: Array.isArray(data) ? data : [],
        loading: false,
        error: null,
      });
    } catch (err) {
      console.error('Error al cargar laboratorios:', err);
      set({
        laboratorios: [],
        loading: false,
        error: 'No se pudieron cargar los laboratorios.',
      });
    }
  },

  createLaboratorio: async (labData) => {
    set({ loading: true, error: null });
    try {
      const response = await api.post('/laboratorio/', labData);
      set((state) => ({
        laboratorios: [...state.laboratorios, response.data],
        loading: false,
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
      set((state) => ({
        laboratorios: state.laboratorios.map((l) => (l.id === id ? response.data : l)),
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: 'Error al actualizar laboratorio', loading: false });
      return false;
    }
  },
}));

export default useIotStore;