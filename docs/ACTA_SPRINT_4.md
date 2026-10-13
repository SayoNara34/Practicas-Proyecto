# Acta del Sprint 4

**Proyecto:** Sistema Web Control de Plagas en Plátano  
**Materia:** Prácticas Aplicadas — Politécnico Grancolombiano, Tecnología en Desarrollo de Software  
**Fecha de elaboración:** 13 de octubre de 2026  
**Versión del acta:** 1.0  
**Estado:** Preparada para Sprint Review; pendiente de aceptación y firmas

## 1. Datos generales

| | |
|---|---|
| **Docente** | Edilberto Torres Ortiz |
| **Scrum Master** | Nicolás Abril Cárdenas |
| **Product Owner** | Juan Miguel Parra Garzón |
| **Equipo de desarrollo** | Santiago Cortez Mojica |
| **Repositorio** | https://github.com/SayoNara34/Practicas-Proyecto |
| **Periodo del sprint / fecha de reunión** | Por confirmar por el equipo |
| **Asistentes reales** | Por registrar en la reunión |

## 2. Objetivo y alcance

Se prepara el incremento US10: exportar las estadísticas del profesional a PDF y Excel (.xlsx), con filtros de zona y tipo de plaga, los cuatro estados, total y fecha de generación. Mantiene el alcance de demostración del producto.

## 3. Entregables

| Entregable | Ubicación |
|---|---|
| Planeación, US10, criterios y Sprint Backlog | `docs/SPRINT_4.md` |
| Exportación PDF y Excel | `app/exportaciones.py` |
| Panel con filtros y descargas | `demo_web.py` |
| Pruebas de US10 | `tests/test_us10_exportaciones.py` |
| Evidencias y guion de aceptación | `docs/PLAN_PRUEBAS_SPRINT_4.md` |
| Backlog documental | `docs/PRODUCT_BACKLOG.md` |
| Retrospectiva para completar en reunión | `docs/RETROSPECTIVA_SPRINT_4.md` |
| Documentación y manual actualizados | README, estándar, EPS, DoD y manual PDF en `docs/` |

## 4. Evidencias verificables

Verificación técnica realizada el 13 de octubre de 2026. Ejecutar desde la raíz tras instalar `requirements.txt`.

| Evidencia | Comando | Resultado observado |
|---|---|---|
| Regresión completa | `python -m pytest -q` | 87 passed |
| US10 | `python -m pytest tests/test_us10_exportaciones.py -q` | 18 passed |
| Flujo previo | `python demo.py` | Registro a cierre y estadísticas sin errores |
| Descargas de extremo a extremo | `python scripts/verificar_sprint_4.py` | Panel filtrado, PDF y XLSX válidos; total 1 en ambos; acceso de campesino rechazado |
| Recorrido manual | `python demo_web.py` | Seguir el plan de pruebas para aceptación del Product Owner |

## 5. Cumplimiento del Definition of Done

| # | Criterio | Estado | Evidencia / pendiente |
|---|---|---|---|
| 1 | Criterios de aceptación | Verificados técnicamente; ratificación pendiente | US10 y plan de pruebas |
| 2 | Código integrado y revisado | Pendiente | Revisión de otro integrante e integración a main |
| 3 | Estándar de código | Verificado técnicamente | Docstrings, tipos y reglas en `app/exportaciones.py` |
| 4 | Pruebas unitarias | Cumple | 87 pruebas pasan |
| 5 | Prueba de flujo | Cumple técnicamente | Consola y verificación HTTP real |
| 6 | Validaciones y errores | Cumple técnicamente | Permisos, formato y longitud cubiertos |
| 7 | Sin defectos críticos | Por confirmar por el equipo | No hubo fallos en las verificaciones ejecutadas; no sustituye el registro de defectos |
| 8 | Backlog actualizado | Propuesta documental disponible | Ratificar en el backlog oficial |
| 9 | Sprint Review | Pendiente | Reunión y aceptación del Product Owner |
| 10 | Documentación | Cumple técnicamente | README, EPS, estándar, DoD y manual actualizados |

## 6. Limitaciones conocidas

La sesión por URL no ofrece seguridad de producción. Los datos se pierden al reiniciar y las fotos son temporales. PDF y Excel son archivos descargados al equipo del usuario; no se guardan automáticamente en un historial del sistema.

## 7. Acuerdos y próximos pasos

Propuestas para la reunión: ratificar US10 y el periodo; revisar la rama de entrega; ejecutar el guion; registrar defectos, aceptación o ajustes; confirmar el alcance actualizado del DoD; completar retrospectiva e integrar después de revisión. No son acuerdos ya aprobados.

## 8. Aceptación

| Rol | Nombre | Firma | Fecha |
|---|---|---|---|
| Docente | Edilberto Torres Ortiz | | |
| Product Owner | Juan Miguel Parra Garzón | | |
| Scrum Master | Nicolás Abril Cárdenas | | |
| Equipo de desarrollo | Santiago Cortez Mojica | | |

**Resultado de la revisión (aceptado / requiere ajustes):** Por registrar.  
**Observaciones:** Por registrar durante la reunión.
