import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useThemeStore = create(
  persist(
    (set, get) => ({
      theme: 'system', // 'light', 'dark', or 'system'
      
      setTheme: (theme) => {
        set({ theme });
        get().applyTheme();
      },
      
      toggleTheme: () => {
        const currentTheme = get().theme;
        let newTheme;
        
        if (currentTheme === 'system') {
          newTheme = 'dark';
        } else if (currentTheme === 'dark') {
          newTheme = 'light';
        } else {
          newTheme = 'system';
        }
        
        set({ theme: newTheme });
        get().applyTheme();
      },
      
      applyTheme: () => {
        const theme = get().theme;
        const root = document.documentElement;
        
        if (theme === 'system') {
          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          root.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
        } else {
          root.setAttribute('data-theme', theme);
        }
      },
      
      getCurrentTheme: () => {
        const theme = get().theme;
        if (theme === 'system') {
          return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return theme;
      },
      
      isDarkMode: () => {
        return get().getCurrentTheme() === 'dark';
      }
    }),
    {
      name: 'iot-theme-storage',
    }
  )
);

export default useThemeStore;