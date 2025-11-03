# Gym Notebook

## Descripción del Proyecto

Gym Notebook es una aplicación web desarrollada con Django que facilita la gestión y el seguimiento de rutinas de entrenamiento personalizadas. Está diseñada para conectar a entrenadores con sus atletas, permitiendo a los entrenadores crear y asignar planes de ejercicio detallados, y a los atletas registrar su rendimiento, seguir su progreso y visualizar sus marcas personales.

## Características Principales

### Gestión de Usuarios y Roles
*   **Autenticación:** Registro, inicio y cierre de sesión de usuarios.
*   **Roles:** Distinción entre usuarios con rol de "Entrenador" y "Atleta".

### Funcionalidades para Entrenadores
*   **Creación de Ejercicios:** Añadir nuevos ejercicios al catálogo con detalles y enlaces a videos demostrativos.
*   **Diseño de Entrenamientos:** Crear rutinas de entrenamiento personalizadas para atletas específicos.
*   **Asignación de Ejercicios:** Incluir múltiples ejercicios en una rutina.
*   **Prescripción de Series:** Definir el número de series, repeticiones (o rangos) y peso recomendado para cada ejercicio dentro de un entrenamiento.
*   **Edición de Entrenamientos:** Modificar rutinas existentes, incluyendo la adición/eliminación de ejercicios y la actualización de series.

### Funcionalidades para Atletas
*   **Visualización de Rutinas:** Acceder a las rutinas de entrenamiento asignadas por su entrenador.
*   **Registro de Rendimiento:** Introducir el peso real levantado y las repeticiones realizadas para cada serie de un ejercicio.
*   **Seguimiento de Marcas Personales (PRs):** Ver sus récords personales por ejercicio y número de repeticiones.
*   **Análisis de Progresión:** Visualizar la evolución del rendimiento en ejercicios específicos a lo largo del tiempo, incluyendo el progreso del peso máximo levantado.

## Tecnologías Utilizadas

*   **Backend:** Python, Django (Framework Web)
*   **Base de Datos:** SQLite (por defecto para desarrollo)
*   **Frontend:** HTML, CSS (con Tailwind CSS para estilos), JavaScript
*   **Utilidades:** `django-browser-reload` (para recarga automática en desarrollo)

## Estructura del Proyecto (Alto Nivel)

*   `config/`: Configuración global del proyecto Django (settings, URLs principales).
*   `core/`: Aplicación principal que contiene los modelos de datos, vistas, URLs específicas de la aplicación y formularios.
*   `templates/`: Archivos HTML para la interfaz de usuario.
*   `theme/`: Aplicación Django para la gestión de activos estáticos y configuración de Tailwind CSS.

## Configuración e Instalación

Para poner en marcha el proyecto en tu entorno local, sigue los siguientes pasos:

### Prerrequisitos
*   Python 3.x
*   pip (gestor de paquetes de Python)
*   npm (gestor de paquetes de Node.js, necesario para Tailwind CSS)

### Pasos de Instalación

1.  **Clonar el Repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd gym_notebook
    ```
    *(Reemplaza `<URL_DEL_REPOSITORIO>` con la URL real de tu repositorio)*

2.  **Crear y Activar un Entorno Virtual:**
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instalar Dependencias de Python:**
    Instala las librerías de Django y otras dependencias. Si tienes un `requirements.txt`, úsalo:
    ```bash
    pip install -r requirements.txt
    ```
    Si no, instala las principales manualmente:
    ```bash
    pip install Django django-browser-reload tailwindcss
    ```
    *(Nota: Es recomendable generar un `requirements.txt` con `pip freeze > requirements.txt`)*

4.  **Configurar la Base de Datos:**
    Aplica las migraciones para crear las tablas en la base de datos SQLite:
    ```bash
    python manage.py migrate
    ```

5.  **Crear un Superusuario (Opcional):**
    Para acceder al panel de administración de Django:
    ```bash
    python manage.py createsuperuser
    ```
    Sigue las instrucciones para crear el usuario.

6.  **Configuración de Frontend (Tailwind CSS):**
    Navega al directorio `theme/static_src` e instala las dependencias de Node.js:
    ```bash
    cd theme/static_src
    npm install
    ```
    Luego, vuelve al directorio raíz del proyecto:
    ```bash
    cd ../../
    ```
    Para compilar los estilos de Tailwind CSS en desarrollo (se recomienda ejecutarlo en una terminal separada):
    ```bash
    npm run dev # o npm run watch si está configurado
    ```
    Para compilar los estilos para producción:
    ```bash
    npm run build
    ```

7.  **Ejecutar el Servidor de Desarrollo:**
    ```bash
    python manage.py runserver
    ```
    La aplicación estará disponible en `http://127.0.0.1:8000/`.

## Uso

### Para Entrenadores
1.  Regístrate o inicia sesión como "Entrenador".
2.  Desde el dashboard, puedes crear nuevos ejercicios y entrenamientos.
3.  Al crear un entrenamiento, asigna ejercicios y define las series y repeticiones.
4.  Puedes editar entrenamientos existentes para ajustar la prescripción.

### Para Atletas
1.  Regístrate o inicia sesión como "Atleta" y asegúrate de que un entrenador te haya asignado una rutina.
2.  En "Mis Rutinas", selecciona un entrenamiento para ver los ejercicios prescritos.
3.  Registra el peso real y las repeticiones que realizaste para cada serie.
4.  Consulta tus "Marcas Personales" y la "Progresión" de tus ejercicios para ver tu evolución.
