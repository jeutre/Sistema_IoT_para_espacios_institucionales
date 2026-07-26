import React from 'react';
import useThemeStore from '../store/themeStore';
import './ThemeToggle.css';

const ThemeToggle = () => {
  const { theme, toggleTheme, getCurrentTheme } = useThemeStore();
  const currentTheme = getCurrentTheme();

  const getThemeIcon = () => {
    return currentTheme === 'dark' ? '🌙' : '☀️';
  };

  const getThemeLabel = () => {
    return currentTheme === 'dark' ? 'Oscuro' : 'Claro';
  };

  return (
    <button 
      className="theme-toggle"
      onClick={toggleTheme}
      aria-label={`Cambiar tema. Tema actual: ${getThemeLabel()}`}
      title={`Tema: ${getThemeLabel()}`}
    >
      <span className="theme-icon">{getThemeIcon()}</span>
      <span className="theme-label">{getThemeLabel()}</span>
    </button>
  );
};

export default ThemeToggle;