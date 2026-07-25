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
      const data = response.data.results !== undefined ? response.data.results : response.data;
      set({ dispositivos: data, loading: false });
    } catch (err) {
      console.error('Error al cargar dispositivos:', err);
      set({ dispositivos: [], loading: false, error: 'No se pudieron cargar los dispositivos.' });
    }
  },

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
    }
  },

  fetchAlertas: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get('/alertas/');
      const data = response.data.results !== undefined ? response.data.results : response.data;
      set({ alertas: data, loading: false });
    } catch (err) {
      console.error('Error al cargar alertas:', err);
      set({ alertas: [], loading: false, error: 'No se pudieron cargar las alertas.' });
    }
  }
}));

export default useIotStore;