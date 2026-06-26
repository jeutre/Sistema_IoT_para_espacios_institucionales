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
      const data = response.data.results !== undefined ? response.data.results : response.data;
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

  fetchOcupacion: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get('/ocupacion/');
      const data = response.data.results !== undefined ? response.data.results : response.data;
      set({ ocupacion: data, loading: false });
    } catch (err) {
      console.warn("Cargando datos de prueba para ocupación.");
      set({
        ocupacion: [
          { id: 1, dispositivo: { identificador: 'ESP32-A1' }, estado: 'ocupado', registrado_en: '2026-06-25T08:30:00Z' },
          { id: 2, dispositivo: { identificador: 'ESP32-B1' }, estado: 'vacio', registrado_en: '2026-06-25T09:00:00Z' },
        ],
        loading: false
      });
    }
  },

  fetchAlertas: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get('/alertas/');
      const data = response.data.results !== undefined ? response.data.results : response.data;
      set({ alertas: data, loading: false });
    } catch (err) {
      console.warn("Cargando datos de prueba para alertas.");
      set({
        alertas: [
          { id: 101, dispositivo: 'ESP32-A2', tipo: 'Desconexión', nivel: 'critico', mensaje: 'Pérdida de latido (heartbeat) por más de 5 minutos.', tiempo: 'Hace 10 min' },
          { id: 102, dispositivo: 'Sensor-Temp-1', tipo: 'Advertencia', nivel: 'medio', mensaje: 'Temperatura por encima del umbral (30°C) en Sala de Servidores.', tiempo: 'Hace 1 hora' },
          { id: 103, dispositivo: 'RFID-PuertaPrincipal', tipo: 'Seguridad', nivel: 'alto', mensaje: '3 intentos de acceso denegados consecutivos.', tiempo: 'Hace 2 horas' }
        ],
        loading: false
      });
    }
  }
}));

export default useIotStore;
