# Gym Notebook

## Descripción del Proyecto

Gym Notebook es una aplicación web desarrollada con Django y React que facilita la gestión y el seguimiento de rutinas de entrenamiento personalizadas. Está diseñada para conectar a entrenadores con sus atletas, permitiendo a los entrenadores crear y asignar planes de ejercicio detallados, y a los atletas registrar su rendimiento, seguir su progreso y visualizar sus marcas personales.

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

*   **Backend:** Python, Django, Django REST Framework
*   **Frontend:** JavaScript, React, Vite, Tailwind CSS
*   **Base de Datos:** SQLite (por defecto para desarrollo)

## Estructura del Proyecto

*   `config/`: Configuración global del proyecto Django (settings, URLs principales).
*   `core/`: Aplicación principal de Django que contiene modelos, vistas, APIs y lógica de negocio.
*   `frontend/`: Código fuente de la aplicación de React para los componentes dinámicos.
*   `templates/`: Plantillas HTML renderizadas por Django.
*   `theme/`: Aplicación Django para la gestión de activos estáticos y configuración de Tailwind CSS.
*   `package.json` y `vite.config.js`: Configuración del frontend (dependencias y servidor de desarrollo de Vite).

## Configuración e Instalación

Para poner en marcha el proyecto en tu entorno local, sigue los siguientes pasos.

### Prerrequisitos
*   Python 3.x
*   Node.js y npm (gestor de paquetes de Node.js)

### 1. Configuración del Backend (Django)

1.  **Clonar el Repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd gym_notebook
    ```

2.  **Crear y Activar un Entorno Virtual:**
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instalar Dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Aplicar Migraciones de la Base de Datos:**
    ```bash
    python manage.py migrate
    ```

5.  **Crear un Superusuario (Opcional):**
    Para acceder al panel de administración de Django:
    ```bash
    python manage.py createsuperuser
    ```

### 2. Configuración del Frontend (React + Vite)

1.  **Instalar Dependencias de Node.js:**
    En el directorio raíz del proyecto, ejecuta:
    ```bash
    npm install
    ```

## Cómo Ejecutar el Proyecto

Para trabajar en el entorno de desarrollo, necesitas ejecutar tanto el servidor de Django como el de Vite simultáneamente.

1.  **Iniciar el Servidor de Backend (Django):**
    ```bash
    python manage.py runserver
    ```
    El backend estará disponible en `http://127.0.0.1:8000/`.

2.  **Iniciar el Servidor de Frontend (Vite):**
    Abre una **nueva terminal** y, desde el directorio raíz, ejecuta:
    ```bash
    npm run dev
    ```
    Vite se encargará de compilar los assets del frontend y servirlos para que Django los pueda utilizar.

3.  **Acceder a la Aplicación:**
    Abre tu navegador y ve a `http://127.0.0.1:8000/`.

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