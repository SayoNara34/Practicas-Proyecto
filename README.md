# Savia · Control de plagas en plátano

Aplicación web para que agricultores del Llano Oriental colombiano reporten afectaciones con fotografías y ubicación, y un profesional agrónomo registre su diagnóstico y haga seguimiento hasta cerrar el caso.

La interfaz nueva se ejecuta con **`ejecutar.py`**. Tiene páginas independientes, registro por pasos, paneles por rol, reportes con evidencia privada, historial, notificaciones, cuenta y estadísticas descargables. Usuarios, reportes y fotografías se conservan al reiniciar.

**Guía completa de instalación y presentación: [INSTRUCCIONES_WEB.md](INSTRUCCIONES_WEB.md).**

## Inicio rápido en Windows

Requisito recomendado: Python 3.12 con pip. Desde la carpeta raíz:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe gestionar.py crear-profesional
.venv\Scripts\python.exe ejecutar.py
```

Abrir **http://127.0.0.1:8000**. El comando de administración pide los datos del profesional y una contraseña elegida por ti. Los agricultores se registran desde la web. No existen cuentas habilitadas ni contraseñas predeterminadas.

No necesitas MySQL, Node.js ni claves de servicios externos. Las fuentes, ilustraciones y estilos están incluidos; Internet solo es necesario para instalar dependencias. No es necesario activar el entorno virtual. Después de instalar también puedes iniciar con `INICIAR_WINDOWS.bat`.

## Linux y macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python gestionar.py crear-profesional
.venv/bin/python ejecutar.py
```

## Funciones

| Rol | Acciones |
|---|---|
| Agricultor (`campesino` en la lógica) | Registro con nombre, cédula, correo, teléfono y dirección; creación de reportes con fotos y ubicación; consulta de estados, historial, diagnóstico y recomendación; notificaciones y perfil. |
| Profesional agrónomo | Consulta y filtro de casos; revisión de evidencia; diagnóstico, recomendación y cierre; estadísticas y exportación PDF/XLSX; perfil. |

El registro público siempre crea agricultores. Las cuentas profesionales se crean mediante el comando del servidor. La consulta de casos e imágenes valida rol y propiedad; no hay identificadores de usuario en la URL que sustituyan la sesión.

Se mantiene el ciclo **Reportado → En revisión → Diagnosticado → Resuelto**, y se permite diagnosticar directamente desde Reportado. Cada transición válida notifica al dueño del caso. El diagnóstico permanece disponible después del cierre.

## Datos persistentes

Se prepara automáticamente `instance/` con la base `savia.db`, las fotografías en `evidencias/` y la clave privada en `secret_key`. **No borres ni publiques esta carpeta.** Está excluida de Git. Para un respaldo local, detén la aplicación y copia `instance/` completa a una ubicación privada.

`schema.sql` conserva las cinco tablas originales y añade perfil personal, sesiones, eventos del historial e intentos de acceso. Al inicializar una base anterior se crean las tablas nuevas sin borrar las existentes. Una cuenta antigua sin perfil completo requiere gestión del administrador para completar sus datos; las nuevas cuentas siempre lo crean.

## Pruebas

```powershell
.venv\Scripts\python.exe -m pytest -q
```

Resultado de esta entrega: **98 passed**. Incluye las 69 pruebas originales y 29 escenarios web parametrizados con CSRF activo, permisos, evidencias reales, persistencia, sesión revocable, diagnóstico, notificaciones, cierre y exportaciones. Las pruebas usan carpetas temporales y no modifican tus registros.

Se verificó la sintaxis JavaScript y las interacciones principales en un DOM aislado. No se realizó una inspección visual en un navegador real en el entorno de implementación. Recorre el guion de la guía antes de presentar al cliente.

## Estructura

```text
app/                  Reglas y consultas del dominio
web/                  Aplicación Flask, rutas y comandos
web/templates/        Vistas Jinja con escape automático
web/static/           CSS, JavaScript, SVG y fuentes locales
schema.sql            Esquema idempotente, compatible con las tablas anteriores
ejecutar.py           Servidor Waitress sin modo de depuración
gestionar.py          Creación de profesionales y restablecimiento de contraseña
INSTRUCCIONES_WEB.md   Instalación, manual de uso, respaldo y solución de problemas
requirements-lock.txt Versiones verificadas de las dependencias
requirements.txt      Rangos de compatibilidad
instance/             Datos privados de la instalación; no se versiona
tests/                Pruebas de dominio y de la aplicación web
demo.py               Demostración histórica en consola
demo_web.py           Demostración web histórica, con datos en memoria
```

## Demostraciones anteriores y documentación

`python demo.py` y `python demo_web.py` siguen disponibles como demostraciones históricas. Sus datos en memoria y fotos temporales no son los registros de la aplicación nueva. Para la presentación utiliza `python ejecutar.py`.

El manual de la nueva web es [INSTRUCCIONES_WEB.md](INSTRUCCIONES_WEB.md). Los PDF de demo, actas y diagramas del equipo se conservan como documentación histórica. [ENTREGA_WEB.md](docs/ENTREGA_WEB.md) registra el alcance y las verificaciones de esta implementación, sin atribuir aceptación del cliente ni reuniones no realizadas.

El README anterior mencionaba exportaciones y consulta de diagnóstico que no estaban en el código de main revisado. Esta entrega recupera esas funciones de US10 y US11 y las integra en la interfaz nueva. No equivale a cerrar formalmente el Sprint 4.

## Equipo y metodología

Proyecto académico del Politécnico Grancolombiano, Tecnología en Desarrollo de Software, desarrollado con Scrum.

| Rol | Integrante |
|---|---|
| Docente | Edilberto Torres Ortiz |
| Scrum Master | Nicolás Abril Cárdenas |
| Product Owner | Juan Miguel Parra Garzón |
| Desarrollo | Santiago Cortez Mojica |

El estándar está en [ESTANDAR_DOCUMENTACION.md](docs/ESTANDAR_DOCUMENTACION.md). El cumplimiento del DoD y la aceptación se registran por el equipo.

## Alcance para presentación

Versión funcional ejecutable localmente. La identidad Savia es una propuesta visual del proyecto y no representa afiliación gubernamental. El diagnóstico es profesional, no automático. No se incluyen dominio público, correo transaccional ni verificación documental de personas o profesionales. Para operación pública con datos reales se requiere configurar HTTPS, disco persistente, respaldos y el responsable/canal de privacidad; la guía explica la configuración opcional.

Las fuentes Manrope y Lora se distribuyen con sus licencias OFL en `web/static/fuentes/`. La iconografía e ilustraciones SVG se incluyen como recursos locales editables.
