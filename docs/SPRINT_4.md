# Sprint 4 · Correcciones para la segunda entrega

**Proyecto:** Sistema Web Control de Plagas en Plátano (interfaz Savia)  
**Materia:** Prácticas Aplicadas · Politécnico Grancolombiano, Tecnología en Desarrollo de Software  
**Rama de entrega:** `app_webb`  
**Fecha de elaboración:** 12 de noviembre de 2026  
**Fecha de la segunda entrega:** martes 17 de noviembre de 2026  
**Versión:** 2.0 (reemplaza la versión 1.2 del 13 de octubre de 2026; ver [Historial de versiones](#10-historial-de-versiones))  

## 1. Datos generales

| Rol | Integrante |
|---|---|
| Docente | Edilberto Torres Ortiz |
| Scrum Master | Nicolás Abril Cárdenas |
| Product Owner | Juan Miguel Parra Garzón |
| Equipo de desarrollo | Santiago Cortez Mojica |

| Dato | Valor |
|---|---|
| Base de la primera entrega | commit `11429dc` de `main` (14 de octubre de 2026) |
| Periodo de correcciones | 14 de octubre al 12 de noviembre de 2026, según los commits de la rama (último revisado: `6ce7fc6`) |
| Estado | Correcciones integradas en `app_webb` y verificadas técnicamente; aceptación del Product Owner y del docente por registrar |

## 2. Objetivo del sprint

Corregir lo observado en la primera entrega y presentar en la segunda una versión coherente del producto:

1. Pasar de la demostración en memoria a una **aplicación web persistente** que conserve usuarios, reportes y fotografías.
2. Hacer que **US10 y US11 existan en el código**, y no solo en la documentación.
3. **Corregir los diagramas** del proyecto y reunirlos en `docs/Diagramas/`.
4. Actualizar instalación, manual, estándar y evidencias para que describan la aplicación real.

## 3. Situación de partida (primera entrega)

Revisando el commit `11429dc` se encontró lo siguiente:

| # | Hallazgo en la primera entrega | Evidencia |
|---|---|---|
| H1 | El README, el Sprint 4 v1.2 y el acta mencionaban `app/exportaciones.py` (US10), la consulta de diagnóstico (US11), `tests/test_us10_exportaciones.py`, `tests/test_us11_consulta_diagnostico.py` y `scripts/verificar_sprint_4.py`, pero esos archivos no estaban en el repositorio. | `git ls-tree 11429dc` solo contiene 9 módulos en `app/` y 7 archivos en `tests/` |
| H2 | La documentación afirmaba 95 pruebas aprobadas; el repositorio tenía 69. | Mismo commit |
| H3 | La interfaz era una demo con sesión por URL, datos en memoria y fotos en una carpeta temporal: se perdía todo al reiniciar. | `demo_web.py`, Acta EPS |
| H4 | Los diagramas de estados, paquetes y secuencia necesitaban corrección; los de arquitectura y componentes no estaban en la carpeta de diagramas. | Historial de `docs/Diagramas/` |
| H5 | El diagrama de clases de entidades se corrigió en `main`, pero no en la rama de entrega. | commit `a5ef42f` (solo en `main`) |

## 4. Correcciones realizadas

### 4.1 Aplicación y código

Commit `96bc504` (14 de octubre de 2026), *US1: integrar portal web persistente y atención de casos US2-US11*.

| Área | Corrección | Dónde |
|---|---|---|
| Aplicación web | Nueva aplicación Flask con páginas independientes: inicio, registro por pasos, ingreso, panel por rol, listado filtrable y paginado, nuevo reporte, ficha del caso, notificaciones, cuenta y estadísticas. | `web/`, `web/templates/`, `web/static/` |
| Persistencia (H3) | SQLite en archivo y fotografías en disco dentro de `instance/`. Los datos se conservan al reiniciar. Se mantienen las 5 tablas originales y se agregan perfil, sesión, evento e intentos de acceso, sin borrar datos anteriores. | `schema.sql`, `app/db.py` |
| US10 (H1) | Exportación real de estadísticas a PDF y Excel con los filtros del panel. Solo el profesional puede exportar. | `app/exportaciones.py`, ruta `/estadisticas/exportar/<formato>` |
| US11 (H1) | El agricultor consulta diagnóstico, recomendación, profesional y fecha de sus propios reportes, también después del cierre. | `consultar_diagnostico` en `app/diagnosticos.py`, ficha del caso |
| Registro y acceso | Perfil con cédula única, contacto y autorización de datos; contraseña confirmada; registro público siempre como agricultor; profesionales creados por comando. | `app/perfiles.py`, `gestionar.py`, `web/comandos.py` |
| Seguridad | Sesión revocable de 8 horas en lugar de sesión por URL; CSRF en formularios; contraseñas PBKDF2-SHA256 (600.000 iteraciones); límite de intentos de ingreso; redirecciones solo internas. | `app/sesiones.py`, `web/__init__.py` |
| Evidencias | Solo JPG/PNG reales, máximo 6 fotos y 10 MB, nombres internos aleatorios, metadatos eliminados y acceso privado por rol y propiedad. | `app/archivos.py` |
| Ejecución | Servidor Waitress sin modo depuración, script de inicio para Windows y versiones de dependencias fijadas. | `ejecutar.py`, `INICIAR_WINDOWS.bat`, `requirements-lock.txt` |
| Pruebas (H2) | De 69 a **98 pruebas**: las 69 originales y 29 escenarios web. | `tests/test_web_portal.py` |

### 4.2 Diagramas

| Diagrama | Corrección | Commit · autor · fecha |
|---|---|---|
| Estados | Diagrama corregido | `fafbdf5` · Kerubin · 15 oct 2026 |
| Paquetes | Diagrama corregido | `fafbdf5` · Kerubin · 15 oct 2026 |
| Arquitectura | Diagrama corregido y movido a `docs/Diagramas/` | `d8c8242`, `3b14251` · SantrixCun · 27 oct 2026 |
| Componentes | Diagrama corregido y movido a `docs/Diagramas/` | `7bd9400`, `4cf0771` · SantrixCun · 27 oct 2026 |
| Secuencia (UML) | Nueva versión corregida y actualizada | `80d99e2` · Kerubin · 28 oct 2026 |
| Secuencia simplificado | Versión en 6 fases (crear cuenta → resolver). Se subió en la raíz y se movió a `docs/Diagramas/diagrama_secuencia.png` | `86ae1bd`, `99d9d5c` · Kerubin · 12 nov 2026 |
| Secuencia (archivo `Secuencia corregido.png`) | Subido como "ultima corrección" de la secuencia, pero la imagen contiene un **diagrama de clases de entidades**, no de secuencia (ver P7) | `6ce7fc6` · Kerubin · 12 nov 2026 |
| Clases de entidades (H5) | Versión corregida en PNG, traída de `main` a la rama de entrega; se retira el JPEG anterior | `a5ef42f` · Juan Miguel Parra Garzón · 12 nov 2026 |

### 4.3 Documentación

| Documento | Corrección |
|---|---|
| `README.md` | Reescrito para la aplicación persistente: instalación en Windows, Linux y macOS, funciones por rol, datos persistentes, pruebas y estructura. |
| `INSTRUCCIONES_WEB.md` | Nuevo manual de instalación, uso, respaldo y solución de problemas. El PDF `MANUAL_USUARIO_PLANTAS.pdf` queda como documento histórico de la demo. |
| `docs/ENTREGA_WEB.md` | Registro del alcance y las verificaciones de la aplicación web. |
| `docs/ESTANDAR_DOCUMENTACION.md` | Versión 1.4: reglas para la capa web, CSRF, sesiones, evidencias privadas y pruebas. |
| `docs/SPRINT_4.md` | Este documento (versión 2.0). |

## 5. Historias de usuario del sprint

Se mantienen US10 y US11 con los criterios de la versión 1.2. Su estado se actualiza con la implementación real.

| Historia | Criterios | Implementación | Verificación |
|---|---|---|---|
| **US10**<br>Exportar<br>estadísticas<br>(profesional) | CA1 a CA8: solo el profesional exporta; PDF y Excel; cuatro estados, conteos y total; mismos filtros del panel; filtros y fecha UTC en el archivo; archivo válido sin coincidencias; errores claros en formato o filtros largos; no modifica datos. | `app/exportaciones.py`, ruta de descarga | Recorrido profesional de `tests/test_web_portal.py` (descargas PDF/XLSX, filtros, rechazo al agricultor y a formatos inválidos) y regresión completa |
| **US11**<br>Consultar<br>diagnóstico y<br>recomendación<br>(agricultor) | CA11-1 a CA11-6: solo reportes propios; diagnóstico, recomendación, profesional y fecha; aviso de espera; disponible tras el cierre; rechaza otros usuarios y roles; texto escapado y solo lectura. | `consultar_diagnostico`, ficha del caso | Recorrido profesional de `tests/test_web_portal.py` (diagnóstico visible y escapado tras el cierre), prueba de reporte privado y regresión completa |

## 6. Sprint Backlog

| ID | Tarea | Evidencia | Estado |
|---|---|---|---|
| S4-01 | Definir US10 y US11 y sus criterios | Sección 5 | Hecho; ratificación del PO pendiente |
| S4-02 | Implementar la exportación PDF/Excel | `app/exportaciones.py` | Hecho |
| S4-03 | Implementar la consulta de diagnóstico propio | `app/diagnosticos.py` | Hecho |
| S4-04 | Construir la aplicación web persistente | `web/`, `schema.sql`, `ejecutar.py` | Hecho |
| S4-05 | Probar la web: permisos, evidencias, persistencia, sesión, exportación | `tests/test_web_portal.py` (29 pruebas) | Hecho |
| S4-06 | Corregir diagramas | `docs/Diagramas/` | Hecho; revisar los pendientes de la sección 8 |
| S4-07 | Actualizar README, manual y estándar | Sección 4.3 | Hecho |
| S4-08 | Documentar las correcciones del sprint | `docs/SPRINT_4.md` | Hecho |
| S4-09 | Revisión, aceptación e integración a `main` | Acta del Sprint 4 | Pendiente |

## 7. Evidencia técnica

Verificación ejecutada el 12 de noviembre de 2026 sobre la rama `app_webb`, con un entorno limpio instalado desde `requirements-lock.txt`:

```bash
python -m pytest -q
```

Resultado: **98 passed**.

| Archivo de pruebas | Pruebas |
|---|---|
| `tests/test_us1_registro.py` | 11 |
| `tests/test_us2_us3_reportes.py` | 20 |
| `tests/test_us4_us6_listados.py` | 5 |
| `tests/test_us5_us8_diagnostico_cierre.py` | 10 |
| `tests/test_us7_estados_notificaciones.py` | 16 |
| `tests/test_us9_estadisticas.py` | 7 |
| `tests/test_web_portal.py` | 29 |
| **Total** | **98** |

Las pruebas usan bases y carpetas temporales con personas ficticias; no modifican `instance/`.

### Cumplimiento del Definition of Done

| # | Criterio | Estado |
|---|---|---|
| 1 | Criterios de aceptación | Verificados técnicamente; ratificación del PO pendiente |
| 2 | Código integrado y revisado | Pendiente: revisión de otro integrante e integración a `main` |
| 3 | Estándar de código | Cumple según el estándar 1.4 |
| 4 | Pruebas unitarias | Cumple: 98 pruebas aprobadas |
| 5 | Prueba de flujo | Cumple técnicamente: recorrido web registro → reporte → diagnóstico → cierre → exportación |
| 6 | Validaciones y errores | Cumple técnicamente |
| 7 | Sin defectos críticos | Por confirmar por el equipo |
| 8 | Backlog actualizado | Pendiente en `Product_Backlog.xlsx` |
| 9 | Sprint Review | Por realizar en la entrega del 17 de noviembre de 2026 |
| 10 | Documentación | Cumple, salvo los pendientes de la sección 8 |

## 8. Pendientes antes de la entrega del martes

| # | Pendiente | Responsable sugerido |
|---|---|---|
| P1 | Los diagramas de **arquitectura** y **secuencia simplificado** siguen mostrando `demo_web.py`, sesión por URL, SQLite en memoria y carpeta temporal. La aplicación actual usa `web/` + `ejecutar.py`, sesión revocable y SQLite y fotos en `instance/`. Hay que actualizarlos, o rotularlos como diagramas de la demo. Conviene revisar lo mismo en componentes y paquetes. | Equipo de diagramas |
| P2 | La sección de trazabilidad de `ESTANDAR_DOCUMENTACION.md` sigue citando archivos que no existen: `tests/test_us10_exportaciones.py`, `tests/test_us11_consulta_diagnostico.py`, `scripts/verificar_sprint_4.py`, `PRODUCT_BACKLOG.md`, `PLAN_PRUEBAS_SPRINT_4.md`, `RETROSPECTIVA_SPRINT_4.md` y `ACTA_SPRINT_4.md`. | Product Owner |
| P3 | `ACTA_SPRINT_4.pdf` (v1.2) dice 95 pruebas y deja la aceptación sin registrar. Hay que actualizarla con 98 pruebas y el resultado de la revisión. | Scrum Master |
| P4 | Recorrer la aplicación en un navegador real antes de presentar. `ENTREGA_WEB.md` indica que no se hizo inspección visual. | Desarrollo |
| P5 | Integrar `app_webb` en `main` mediante revisión (pull request), para que la entrega quede en la rama principal. | Equipo |
| P6 | Unificar la escritura del apellido del desarrollador: aparece como "Cortez" y como "Cortes" en distintos documentos. | Product Owner |
| P7 | `docs/Diagramas/Secuencia corregido.png` (commit `6ce7fc6`) muestra el diagrama de clases de entidades, no un diagrama de secuencia. Hay que subir la imagen correcta, o renombrarla si era un diagrama de clases. Después, dejar un solo diagrama de secuencia vigente: ahora hay tres (`diagrama_secuencia.png`, `diagrama_secuencia_uml.png` y este). | Autor del diagrama |

## 9. Guion para la segunda entrega

1. Instalar y crear el profesional: `python -m pip install -r requirements-lock.txt` y luego `python gestionar.py crear-profesional`.
2. Iniciar con `python ejecutar.py` y abrir http://127.0.0.1:8000.
3. Registrar un agricultor desde la web y crear un reporte con fotos y ubicación.
4. Ingresar como profesional: revisar el caso, registrar diagnóstico y recomendación.
5. Volver como agricultor: ver la notificación y el diagnóstico (US11).
6. Como profesional, cerrar el caso; comprobar que el agricultor sigue viendo el diagnóstico.
7. Filtrar estadísticas y descargar el PDF y el Excel (US10). Comprobar que el agricultor no puede exportar.
8. Detener y reiniciar la aplicación: los usuarios, reportes y fotos siguen ahí.
9. Mostrar las pruebas con `python -m pytest -q` (98 passed).

Resultado US10 (aceptado / requiere ajustes): **por registrar**.
Resultado US11 (aceptado / requiere ajustes): **por registrar**.
Observaciones del docente: **por registrar**.

## 10. Historial de versiones

| Versión | Fecha | Cambios |
|---|---|---|
| 1.2 | 13 de octubre de 2026 | Planeación inicial de US10 y US11 (PDF) |
| 2.0 | 12 de noviembre de 2026 | Correcciones para la segunda entrega: aplicación web persistente, US10/US11 implementadas, 98 pruebas, diagramas corregidos, documentación actualizada y pendientes para el martes |
