// frontend/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import EjercicioApp from './EjercicioApp.jsx';

// 1. Busca el 'div' contenedor en nuestro template de Django
const container = document.getElementById('react-ejercicio-app');

// 2. Si existe, renderiza la app dentro de él
if (container) {
    const root = ReactDOM.createRoot(container);
    root.render(
        <React.StrictMode>
            <EjercicioApp />
        </React.StrictMode>
    );
}