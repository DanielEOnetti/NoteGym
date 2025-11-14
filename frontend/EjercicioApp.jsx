import React, { useState, useEffect } from 'react';

// --- (IMPORTANTE) Helper para el CSRF Token ---
// Ahora lo obtenemos de una variable global que definiremos en el template
function getCsrfToken() {
    return window.CSRF_TOKEN;
}
// --- Fin del Helper ---


// --- Componente de un solo Ejercicio (Item) ---
function EjercicioItem({ ejercicio, onDelete }) {
    
    const handleDelete = () => {
        if (!confirm('¿Estás seguro de que quieres eliminar este ejercicio?')) {
            return;
        }

        fetch(`/api/ejercicios/${ejercicio.id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken(), // <-- Usa la función helper
                'Content-Type': 'application/json'
            },
        })
        .then(response => {
            if (response.ok) {
                onDelete(ejercicio.id);
            } else {
                alert("Error al eliminar el ejercicio.");
            }
        });
    };

    return (
        <li className="py-4 px-6 flex flex-col sm:flex-row justify-between items-start sm:items-center hover:bg-gray-800 transition duration-150">
            <div className="flex flex-col mb-2 sm:mb-0">
                <span className="text-lg font-medium text-white">{ejercicio.nombre}</span>
                {ejercicio.video ? (
                    <a href={ejercicio.video} target="_blank" rel="noopener noreferrer" className="text-sm text-indigo-300 hover:text-indigo-200 transition flex items-center gap-1">
                        Ver Video
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                    </a>
                ) : (
                    <span className="text-sm text-gray-500 italic">Sin video</span>
                )}
            </div>
            <div className="flex-shrink-0">
                <button 
                    type="button"
                    onClick={handleDelete}
                    className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-red-300 bg-red-800 hover:bg-red-700 transition"
                >
                    Eliminar
                </button>
            </div>
        </li>
    );
}

// --- Componente Principal de la App ---
// Usamos 'export default' para que 'main.jsx' pueda importarlo
export default function EjercicioApp() {
    // Ahora podemos usar useState, useEffect directamente
    const [ejercicios, setEjercicios] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('/api/ejercicios/', {
            credentials: 'same-origin' // Incluye cookies de sesión
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Fallo al cargar los datos (${response.status})`);
                }
                return response.json();
            })
            .then(data => {
                const ejerciciosLista = data.results || data;
                setEjercicios(ejerciciosLista); 
                setIsLoading(false);
            })
            .catch(err => {
                console.error("Error en React.useEffect:", err);
                setError(err.message);
                setIsLoading(false);
            });
    }, []); 

    const handleEjercicioDeleted = (deletedId) => {
        setEjercicios(prevEjercicios => 
            prevEjercicios.filter(ejercicio => ejercicio.id !== deletedId)
        );
    };

    // --- Renderizado condicional ---
    if (isLoading) {
        return (
             <div className="py-10 px-6 text-center bg-[#252959] shadow-xl rounded-xl">
                 <p className="text-lg font-medium text-white">Cargando ejercicios...</p>
             </div>
        );
    }

    if (error) {
        return (
            <div className="py-10 px-6 text-center bg-red-900 shadow-xl rounded-xl">
                 <p className="text-lg font-medium text-white">Error: {error}</p>
            </div>
        );
    }

    // --- Renderizado Exitoso ---
    return (
        <div className="bg-[#252959] shadow-xl rounded-xl overflow-hidden">
            <ul role="list" className="divide-y divide-gray-700">
                {ejercicios.length === 0 ? (
                    <li className="py-10 px-6 text-center">
                        <svg className="w-12 h-12 mx-auto text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                        <h3 className="mt-2 text-lg font-medium text-white">No hay ejercicios creados</h3>
                    </li>
                ) : (
                    ejercicios.map(ejercicio => (
                        <EjercicioItem 
                            key={ejercicio.id} 
                            ejercicio={ejercicio} 
                            onDelete={handleEjercicioDeleted}
                        />
                    ))
                )}
            </ul>
        </div>
    );
}