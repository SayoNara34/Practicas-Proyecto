# Acta del Sprint 4

**Proyecto:** Sistema Web Control de Plagas en Plátano  
**Materia:** Prácticas Aplicadas — Politécnico Grancolombiano, Tecnología en Desarrollo de Software  
**Fecha de elaboración:** 13 de octubre de 2026  
**Versión del acta:** 1.2  
**Estado:** Reunión realizada el 13 de octubre de 2026; resultados de aceptación y firmas por completar

## 1. Datos generales

| | |
|---|---|
| **Docente** | Edilberto Torres Ortiz |
| **Scrum Master** | Nicolás Abril Cárdenas |
| **Product Owner** | Juan Miguel Parra Garzón |
| **Equipo de desarrollo** | Santiago Cortez Mojica |
| **Repositorio** | https://github.com/SayoNara34/Practicas-Proyecto |
| **Fecha de reunión** | 13 de octubre de 2026 |
| **Periodo del sprint** | Fecha de inicio por confirmar; reunión realizada el 13 de octubre de 2026 |
| **Asistentes reales** | Por completar por el equipo |

La realización de la reunión el 13 de octubre de 2026 fue confirmada por el solicitante. No se suministraron hora, modalidad, listado de asistentes ni decisiones específicas; estos campos quedan por completar.

## 2. Objetivo y alcance

Se preparan dos historias: US10 exporta las estadísticas del profesional a PDF y Excel (.xlsx), con filtros, estados, total y fecha; US11 permite al campesino consultar diagnóstico, recomendación, profesional y fecha en sus reportes, incluso después del cierre. Mantiene el alcance de demostración del producto.

## 3. Entregables

| Entregable | Ubicación |
|---|---|
| Planeación, US10 y US11, criterios y Sprint Backlog | `docs/SPRINT_4.md` |
| Exportación PDF y Excel | `app/exportaciones.py` |
| Panel con filtros y descargas | `demo_web.py` |
| Pruebas de US10 | `tests/test_us10_exportaciones.py` |
| Consulta de diagnóstico propio y pruebas de US11 | `app/diagnosticos.py`, `tests/test_us11_consulta_diagnostico.py` |
| Evidencias y guion de aceptación | `docs/PLAN_PRUEBAS_SPRINT_4.md` |
| Backlog documental | `docs/PRODUCT_BACKLOG.md` |
| Registro de retrospectiva y seguimiento | `docs/RETROSPECTIVA_SPRINT_4.md` |
| Documentación y manual actualizados | README, estándar, EPS, DoD y manual PDF en `docs/` |

## 4. Evidencias verificables

Verificación técnica realizada el 13 de octubre de 2026. Ejecutar desde la raíz tras instalar `requirements.txt`.

| Evidencia | Comando | Resultado observado |
|---|---|---|
| Regresión completa | `python -m pytest -q` | 95 passed |
| US10 | `python -m pytest tests/test_us10_exportaciones.py -q` | 18 passed |
| US11 | `python -m pytest tests/test_us11_consulta_diagnostico.py -q` | 8 passed |
| Flujo previo | `python demo.py` | Registro a cierre y estadísticas sin errores |
| Descargas de extremo a extremo | `python scripts/verificar_sprint_4.py` | US10: archivos y permisos; US11: espera, consulta de resultado propio y conservación tras cierre |
| Recorrido manual | `python demo_web.py` | Seguir el plan de pruebas para aceptación del Product Owner |

## 5. Cumplimiento del Definition of Done

| # | Criterio | Estado | Evidencia / pendiente |
|---|---|---|---|
| 1 | Criterios de aceptación | Verificados técnicamente; ratificación pendiente | US10, US11 y plan de pruebas |
| 2 | Código integrado y revisado | Pendiente | Revisión de otro integrante e integración a main |
| 3 | Estándar de código | Verificado técnicamente | Docstrings, tipos y reglas en `app/exportaciones.py` |
| 4 | Pruebas unitarias | Cumple | 95 pruebas pasan |
| 5 | Prueba de flujo | Cumple técnicamente | Consola y verificación HTTP real |
| 6 | Validaciones y errores | Cumple técnicamente | Permisos, formato, longitud y consulta propia cubiertos |
| 7 | Sin defectos críticos | Por confirmar por el equipo | No hubo fallos en las verificaciones ejecutadas; no sustituye el registro de defectos |
| 8 | Backlog actualizado | Propuesta documental disponible | Ratificar en el backlog oficial |
| 9 | Sprint Review | Reunión registrada; aceptación por completar | Reunión del 13 de octubre de 2026 confirmada por el solicitante; falta registrar el resultado del Product Owner |
| 10 | Documentación | Cumple técnicamente | README, EPS, estándar, DoD y manual actualizados |

## 6. Limitaciones conocidas

La sesión por URL no ofrece seguridad de producción. Los datos se pierden al reiniciar y las fotos son temporales. PDF y Excel son archivos descargados al equipo del usuario; no se guardan automáticamente en un historial del sistema.

## 7. Acuerdos y próximos pasos

Seguimiento después de la reunión del 13 de octubre de 2026: ratificar US10 y US11 y el periodo; revisar la rama de entrega; ejecutar el guion; registrar defectos, aceptación o ajustes; confirmar el alcance actualizado del DoD; completar retrospectiva e integrar después de revisión. La fecha de reunión está confirmada; estas acciones son pendientes propuestos y no decisiones atribuidas al equipo.

## 8. Aceptación

| Rol | Nombre | Firma | Fecha |
|---|---|---|---|
| Docente | Edilberto Torres Ortiz | | |
| Product Owner | Juan Miguel Parra Garzón | | |
| Scrum Master | Nicolás Abril Cárdenas | | |
| Equipo de desarrollo | Santiago Cortez Mojica | | |

**Resultado US10 (aceptado / requiere ajustes):** Por registrar.  
**Resultado US11 (aceptado / requiere ajustes):** Por registrar.  
**Observaciones de la reunión:** Por completar por el equipo.
