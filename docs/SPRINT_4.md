# Sprint 4 — Exportación de estadísticas

**Proyecto:** Sistema Web Control de Plagas en Plátano  
**Materia:** Prácticas Aplicadas — Politécnico Grancolombiano, Tecnología en Desarrollo de Software  
**Fecha de elaboración:** 13 de octubre de 2026  
**Versión:** 1.0

## 1. Datos generales

| | |
|---|---|
| **Docente** | Edilberto Torres Ortiz |
| **Scrum Master** | Nicolás Abril Cárdenas |
| **Product Owner** | Juan Miguel Parra Garzón |
| **Equipo de desarrollo** | Santiago Cortez Mojica |
| **Periodo del sprint** | Por acordar con el equipo |
| **Estado** | Incremento implementado y probado; revisión y aceptación pendientes |

## 2. Objetivo del sprint

Permitir al profesional descargar las estadísticas de reportes en PDF y Excel, conservando los filtros de zona y tipo de plaga del panel, para consultar y compartir el resumen fuera de la demostración web.

## 3. Historia de usuario

**US10 — Exportar estadísticas.** Como profesional agrónomo, quiero descargar las estadísticas en PDF o Excel para conservar y compartir un resumen de la atención de los cultivos.

US10 continúa la candidata indicada en el README al finalizar el Sprint 3; su identificador y alcance quedan sujetos a ratificación del Product Owner. No se encontraron actas de sprints anteriores ni un Product Backlog independiente en este repositorio.

### Criterios de aceptación

| # | Criterio verificable |
|---|---|
| CA1 | Solo un usuario existente con rol profesional puede exportar. |
| CA2 | El panel ofrece descargas PDF y Excel (.xlsx). |
| CA3 | Ambos archivos contienen los cuatro estados, sus conteos y el total. |
| CA4 | El archivo refleja los mismos filtros exactos de zona y plaga del panel, sin distinguir mayúsculas. |
| CA5 | El archivo identifica los filtros y la fecha de generación en UTC. |
| CA6 | Sin reportes o sin coincidencias se descarga un archivo válido con conteos cero. |
| CA7 | Un formato inválido o filtros de más de 200 caracteres producen un mensaje claro; Excel conserva los filtros como texto y PDF escapa su contenido. |
| CA8 | La exportación no modifica reportes, diagnósticos ni notificaciones. |

## 4. Sprint Backlog

| ID | Tarea | Evidencia | Estado técnico |
|---|---|---|---|
| S4-01 | Definir US10 y sus criterios | Este documento | Elaborado; ratificación pendiente |
| S4-02 | Generar PDF y Excel desde los conteos de US9 | `app/exportaciones.py` | Implementado |
| S4-03 | Agregar filtros y descargas al panel | `demo_web.py` | Implementado |
| S4-04 | Probar archivos, permisos, filtros y respuesta HTTP | `tests/test_us10_exportaciones.py` | 18 pruebas pasan |
| S4-05 | Actualizar instalación y documentación | README, estándar, EPS y manual PDF | Actualizado |
| S4-06 | Preparar evidencias y cierre | Acta, plan de pruebas y retrospectiva | Elaborado; reunión pendiente |

Responsabilidades propuestas: Product Owner valida alcance y aceptación; desarrollo verifica la implementación; Scrum Master coordina el periodo, la revisión y la retrospectiva. No se asignan horas, puntos o compromisos que el equipo no haya confirmado.

## 5. Incremento y dependencias

Se agrega US10 sobre las estadísticas existentes de US9, sin cambiar el esquema SQLite. ReportLab genera PDF, openpyxl genera Excel y pypdf permite verificar el PDF en pruebas. Las dependencias están en `requirements.txt`.

## 6. Definition of Done

Se mantiene la lista de diez criterios del DoD. La ampliación a US10 se documenta en su anexo para revisión del equipo. La evidencia técnica está en `PLAN_PRUEBAS_SPRINT_4.md`; integración a main con revisión de otro integrante, ausencia de defectos críticos confirmada por el equipo, actualización del backlog oficial y aceptación en Sprint Review siguen pendientes. US10 no se declara formalmente Completada hasta cumplirlos.

## 7. Riesgos y fuera de alcance

La demo mantiene sesión por URL, datos en memoria y fotos temporales. Las descargas son resúmenes por estado, no informes individuales ni evidencia de producción. No se incluyen API definitiva, autenticación de producción, persistencia de fotos ni envío de archivos por correo.

## 8. Sprint Review y retrospectiva

Guion: iniciar como Laura, consultar estadísticas, filtrar por Acacías y Picudo negro, descargar ambos formatos, comprobar el total, probar una zona sin coincidencias y verificar que Carlos no pueda exportar. Registrar aceptación y observaciones en `ACTA_SPRINT_4.md`; registrar acuerdos de mejora en `RETROSPECTIVA_SPRINT_4.md` después de la reunión.
