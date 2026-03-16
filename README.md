# Gym Notebook

## Descripción del Proyecto

Gym Notebook es una aplicación web avanzada desarrollada con Django y React que facilita la gestión y el seguimiento de rutinas de entrenamiento personalizadas. Está diseñada para conectar a entrenadores con sus atletas, permitiendo a los entrenadores planificar progresiones a largo plazo mediante mesociclos, y a los atletas registrar su rendimiento real (incluyendo el esfuerzo percibido) para asegurar una sobrecarga progresiva constante.

## Características Principales

### Gestión de Usuarios y Roles
* **Autenticación y Seguridad:** Registro, inicio/cierre de sesión y sistema completo de recuperación de contraseña vía correo electrónico.
* **Roles Especializados:** Distinción estructurada entre usuarios con rol de "Entrenador" y "Atleta".

### Funcionalidades para Entrenadores
* **Gestión del Roster de Atletas:** Vista completa de todos los clientes asignados, con acceso directo al historial y récords personales (PRs) de cada uno para evaluar su evolución.
* **Planificación por Mesociclos:** Capacidad para agrupar entrenamientos en bloques estructurados de varias semanas con objetivos específicos a largo plazo.
* **Diseño de Entrenamientos:** Crear rutinas personalizadas, añadiendo y configurando ejercicios desde el catálogo interactivo.
* **Prescripción Avanzada (RPE):** Definir no solo series, repeticiones y peso, sino también el RPE (Rate of Perceived Exertion / Esfuerzo Percibido) objetivo para cada serie.
* **Interfaz Interactiva (Drag & Drop):** Reordenamiento rápido e intuitivo de los ejercicios dentro de una rutina arrastrando y soltando las tarjetas (integración con `Sortable.js`).
* **Clonación de Semanas:** Herramienta automatizada para clonar una sesión a la semana siguiente, transfiriendo el peso levantado por el atleta en la semana anterior para usarlo como referencia.
* **Historial Visual Integrado:** Al editar rutinas de semanas avanzadas, el entrenador puede ver directamente en pantalla los pesos, repeticiones y RPE que logró el atleta la semana previa.

### Funcionalidades para Atletas
* **Visualización Estructurada:** Acceso a los programas asignados organizados de forma limpia mediante paneles desplegables (acordeones) para evitar el scroll infinito.
* **Registro de Rendimiento:** Introducir el peso real levantado, repeticiones logradas y el RPE real experimentado en cada serie para dar feedback directo al entrenador.
* **Seguimiento de Marcas Personales (PRs):** Visualización automática de récords personales por ejercicio y por número de repeticiones (ej. 1RM, max 5 reps).
* **Análisis de Progresión:** Historial detallado de la evolución del rendimiento a lo largo del tiempo.

## Tecnologías Utilizadas

* **Backend:** Python, Django, Django REST Framework
* **Frontend:** JavaScript, React, Vite, Tailwind CSS, Sortable.js
* **Base de Datos:** SQLite (por defecto para desarrollo) / PostgreSQL (recomendado para producción)

## Estructura del Proyecto

* `config/`: Configuración global del proyecto Django (settings, URLs principales).
* `core/`: Aplicación principal de Django que contiene modelos, vistas, lógica de negocio y servicios avanzados de clonación.
* `frontend/`: Código fuente de la aplicación de React para los componentes dinámicos.
* `templates/`: Plantillas HTML renderizadas por Django.
* `theme/`: Aplicación Django para la gestión de activos estáticos y configuración de Tailwind CSS.
* `build.sh`: Script de compilación automatizado para despliegues en entornos de producción.
* `package.json` y `vite.config.js`: Configuración del frontend y servidor de desarrollo de Vite.

## Configuración e Instalación (Desarrollo Local)

Para poner en marcha el proyecto en tu entorno local, sigue los siguientes pasos:

### Prerrequisitos
* Python 3.x
* Node.js y npm (gestor de paquetes de Node.js)

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

### 2. Configuración del Frontend (React + Vite + Tailwind)

1.  **Instalar Dependencias de Node.js:**
    En el directorio raíz del proyecto y en el directorio del theme, instala las dependencias:
    ```bash
    npm install
    cd theme/static_src
    npm install
    cd ../..
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
    Vite se encargará de compilar los assets del frontend de forma dinámica.

3.  **Acceder a la Aplicación:**
    Abre tu navegador y ve a `http://127.0.0.1:8000/`.

## Despliegue en Producción

El proyecto incluye un script `build.sh` diseñado para automatizar el proceso de despliegue en plataformas como Render, Railway o Heroku. Este script se encarga de:
1. Instalar las dependencias de Python y Node.js.
2. Compilar los assets del frontend (`npm run build`).
3. Recolectar los archivos estáticos de Django (`collectstatic`).
4. Aplicar las migraciones pendientes en la base de datos de producción.

## Uso Básico

### Para Entrenadores
1.  Inicia sesión y dirígete al Dashboard.
2.  Crea un nuevo **Mesociclo** asignándolo a uno de tus atletas.
3.  Añade rutinas a la Semana 1 del mesociclo, configurando los ejercicios, repeticiones y el **RPE objetivo**.
4.  Cuando el atleta termine la semana, utiliza el botón de **clonar sesión** para generar la Semana 2. El sistema transferirá automáticamente los pesos logrados para que puedas ajustar la progresión.

### Para Atletas
1.  Inicia sesión para ver tu programa actual.
2.  Abre la rutina del día correspondiente (la semana más reciente aparecerá siempre arriba).
3.  Observa tus marcas de la semana anterior, realiza tu entrenamiento y **registra el nuevo peso, las repeticiones logradas y tu RPE real**.
4.  Visita la sección de Marcas Personales para celebrar tus nuevos PRs y ver tus gráficas de progresión.