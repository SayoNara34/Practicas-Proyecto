# Plan de pruebas del Sprint 4

**Proyecto:** Sistema Web Control de Plagas en Plátano  
**Versión:** 1.1 — 13 de octubre de 2026

## 1. Preparación

Desde la raíz: `python -m pip install -r requirements.txt`. Las pruebas usan SQLite en memoria.

## 2. Verificación automatizada

| Comando | Resultado observado | Alcance |
|---|---|---|
| `python -m pytest -q` | 95 passed | Regresión de US1–US11 |
| `python -m pytest tests/test_us10_exportaciones.py -q` | 18 passed | Archivos PDF/XLSX parseables, conteos, filtros, cero resultados, permisos, formato, longitud y texto seguro en Excel |
| `python -m pytest tests/test_us11_consulta_diagnostico.py -q` | 8 passed | Resultado propio, conservación tras cierre, permisos, inexistentes y HTML seguro |
| `python demo.py` | Sin errores | Flujo de US1–US9 |
| `python scripts/verificar_sprint_4.py` | Sin errores | Servidor real: panel filtrado, encabezados de descarga, lectura de ambos archivos y rechazo de campesino; consulta del resultado y conservación tras cierre |

CA8 se comprueba en el script comparando las tablas de conteos del panel antes y después de descargar; la exportación solo consulta la base de datos. Resultados obtenidos el 13 de octubre de 2026; reproducirlos antes de aceptar.

## 3. Guion de aceptación manual

1. Ejecutar `python demo_web.py` y abrir `http://localhost:8000`.
2. Entrar como `laura@agro.co`, contraseña `clave1234`.
3. En Estadísticas, dejar los filtros vacíos: hay dos reportes en Reportado y cero en los demás estados.
4. Filtrar zona Acacías y plaga Picudo negro: Reportado = 1 y total exportado = 1.
5. Descargar PDF y Excel, abrir ambos y comprobar filtros, fecha UTC, cuatro estados y total.
6. Filtrar Bogotá: ambos archivos deben contener total 0.
7. Entrar como Carlos: no debe ver controles de exportación. El script verifica también el rechazo de la ruta directa con su identificador.
8. Como Carlos, comprobar el aviso de espera en un reporte sin diagnóstico.
9. Como Laura, diagnosticarlo y escribir una recomendación.
10. Como Carlos, comprobar diagnóstico, recomendación, profesional y fecha en Mis reportes.
11. Como Laura, cerrar el caso; como Carlos, comprobar que el resultado sigue visible.
12. Volver a descargar como Laura y comprobar el nuevo conteo. El acceso al resultado de otro campesino se prueba en la suite US11.

## 4. Registro de aceptación

| Campo | Valor |
|---|---|
| Fecha / evaluador | Por registrar |
| Entorno y versión revisada | Por registrar |
| Resultado / defectos | Por registrar |
| Aceptación del Product Owner | Pendiente |
