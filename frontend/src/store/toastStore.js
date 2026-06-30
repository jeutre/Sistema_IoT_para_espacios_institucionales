import { create } from 'zustand';

const useToastStore = create((set, get) => ({
  toasts: [],
  
  addToast: (message, type = 'info', duration = 5000) => {
    const id = Date.now();
    const newToast = { id, message, type, duration };
    
    set((state) => ({
      toasts: [...state.toasts, newToast]
    }));
    
    // Auto-remove after duration
    setTimeout(() => {
      get().removeToast(id);
    }, duration);
    
    return id;
  },
  
  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter(toast => toast.id !== id)
    }));
  },
  
  clearToasts: () => {
    set({ toasts: [] });
  },
  
  // Helper methods for common toast types
  success: (message, duration = 5000) => {
    return get().addToast(message, 'success', duration);
  },
  
  error: (message, duration = 5000) => {
    return get().addToast(message, 'error', duration);
  },
  
  warning: (message, duration = 5000) => {
    return get().addToast(message, 'warning', duration);
  },
  
  info: (message, duration = 5000) => {
    return get().addToast(message, 'info', duration);
  }
}));

export default useToastStore;