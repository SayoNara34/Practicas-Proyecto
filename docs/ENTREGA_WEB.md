# Entrega de la aplicación web persistente

**Proyecto:** Sistema Web Control de Plagas en Plátano
**Interfaz:** Savia
**Base revisada:** commit `11429dc3cde716059c7da5abfa1b98586515c3a2` de `main`
**Naturaleza:** implementación web solicitada; no constituye un acta de aceptación del cliente ni un cierre de sprint.

## Cambios funcionales

| Área | Implementación |
|---|---|
| Registro y acceso | Perfil con cédula única, contacto y autorización; contraseña confirmada; sesión revocable; recuperación administrativa. |
| Presentación | Inicio público, registro por pasos, ingreso, panel, listado filtrable/paginado, reporte por pasos, ficha de caso, notificaciones, cuenta y estadísticas. |
| Evidencias | JPG/PNG reales, máximo seis y 10 MB, nombres internos aleatorios, eliminación de metadatos y acceso privado por rol/propiedad. |
| Atención | Revisión, diagnóstico y recomendación, cierre, historial y notificaciones por cambio de estado. |
| US10/US11 | Recupera las funciones de exportación y consulta propia que la documentación mencionaba y que faltaban en el código de la base revisada. Se exponen en la nueva interfaz. |
| Persistencia | SQLite en archivo y fotografías en disco. Las tablas originales se conservan; se agregan perfil, sesión, evento e intentos de acceso. |
| Identidad visual | Paleta verde, tipografías locales, ilustraciones SVG, iconografía vectorial y animaciones con respeto por movimiento reducido. Sin emojis ni emblemas oficiales. |

## Evidencia técnica

- `python -m pytest -q`: 98 pruebas aprobadas (69 anteriores y 29 escenarios web parametrizados).
- `node --check web/static/app.js`: sintaxis válida; Node solo se utilizó durante esta verificación, no es requisito para ejecutar el producto.
- Verificación adicional en DOM aislado: pasos del registro, rechazo de contraseñas diferentes, vista previa/eliminación de archivos, límites de selección, ubicación y apertura/cierre de menú móvil.
- Los ensayos usan personas ficticias, archivos temporales y una base aislada. La instalación distribuida no trae cuentas ni datos personales.
- No se ejecutó inspección visual en navegador real ni se validó un alojamiento público en este entorno.

## Organización del código

`app/` mantiene las reglas y consultas del dominio. `web/` integra Flask, sesiones, formularios y plantillas Jinja con escape automático. `ejecutar.py` inicia Waitress; `gestionar.py` expone los comandos administrativos. No se sustituyen `demo.py` ni `demo_web.py`.

Las nuevas cuentas guardan PBKDF2-SHA256 con 600.000 iteraciones y sal aleatoria. El verificador también acepta el formato anterior para conservar compatibilidad. Los identificadores de sesión se almacenan como huellas SHA256 y expiran a las ocho horas. El cierre y el cambio/restablecimiento de contraseña revocan los accesos correspondientes.

## Documentación de uso

El manual de esta aplicación es [`INSTRUCCIONES_WEB.md`](../INSTRUCCIONES_WEB.md). El PDF `MANUAL_USUARIO_PLANTAS.pdf` conserva la documentación histórica de la demo y no sustituye esta guía. README y estándar apuntan al nuevo manual sin presentar las pantallas de la demo como la aplicación actual.

La presentación al cliente, su aceptación, la configuración de un servidor público, los respaldos operativos y el responsable/canal de tratamiento de datos deben registrarse por el equipo cuando efectivamente se realicen.
