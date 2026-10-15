# Estándar de comentarios y documentación del código

**Proyecto:** Sistema Web Control de Plagas en Plátano  
**Aplica a:** todo el código Python y SQL del repositorio. Es parte del Definition of Done.  
**Versión:** 1.4 – aplicación web persistente (ver [Historial de cambios](#historial-de-cambios))

## 1. Idioma y nombres

- Comentarios, docstrings y mensajes de error para el usuario: **en español**.
- Nombres de funciones y variables: `snake_case` en español, descriptivos (`registrar_diagnostico`, no `reg_diag`).
- Constantes en `MAYUSCULAS` (`ESTADOS`, `EXTENSIONES_VALIDAS`). Nombres privados con guion bajo inicial (`_hashear`).
- Tablas y columnas SQL en minúscula y singular (`reporte`, `usuario_id`).

## 2. Docstring de módulo

Cada archivo `.py` inicia con una línea que dice qué hace e indica la historia de usuario que implementa.

```python
"""US7 - Máquina de estados del reporte y notificaciones por cambio de estado."""
```

## 3. Docstring de función

Toda función pública lleva docstring con estilo Google. Resumen en una línea; luego, solo las secciones que apliquen:

| Sección | Cuándo se incluye |
|---|---|
| `Args:` | Si hay parámetros que no se explican solos |
| `Returns:` | Si devuelve algo distinto de `None` |
| `Raises:` | Siempre que lance excepciones de dominio |

```python
def marcar_resuelto(conn: sqlite3.Connection, reporte_id: int, profesional_id: int) -> None:
    """Cierra un caso diagnosticado como "Resuelto" (US8).

    Raises:
        ErrorPermiso: El usuario no es profesional.
        ErrorTransicion: El reporte no está en estado "Diagnosticado".
    """
```

Las funciones privadas cortas (`_verificar`) no necesitan docstring si el nombre es claro.

## 4. Anotaciones de tipo

Todos los parámetros y retornos de funciones públicas llevan anotaciones (`usuario_id: int`, `-> list[sqlite3.Row]`).

## 5. Comentarios en línea

- Explican el **porqué**, no el qué. Mal: `# suma 1 al contador`. Bien: `# El PRAGMA es necesario: SQLite no activa las llaves foráneas por defecto.`
- Van en su propia línea, encima del código que explican.
- Si una regla de negocio viene de una historia o de una decisión del equipo, se cita: `# US4: los más antiguos primero, son los más urgentes.`
- No se deja código comentado ni `TODO` sin responsable y fecha.

## 6. SQL

- Siempre consultas **parametrizadas** (`?`), nunca datos del usuario concatenados en el texto SQL.
- Las restricciones (`CHECK`, `UNIQUE`, `REFERENCES`) se definen en `schema.sql` y llevan un comentario `--` si no son evidentes.

## 7. Errores

- La lógica lanza excepciones de `app/errores.py` (`ErrorValidacion`, `ErrorPermiso`, `ErrorTransicion`, `ErrorNoEncontrado`, `ErrorAutenticacion`).
- El mensaje debe poder mostrarse tal cual al usuario y decir qué corregir.

## 8. Pruebas

- Un archivo por área: `tests/test_us<N>_<tema>.py`.
- Nombre de la prueba = comportamiento esperado: `test_no_se_puede_resolver_un_reporte_sin_diagnosticar`.
- Cada historia con lógica de negocio tiene al menos una prueba del caso válido y una de cada regla de rechazo.

## 9. Commits

Formato: `US<N>: qué se hizo`, en presente e imperativo, por ejemplo `US9: filtrar estadísticas por zona`.

## 10. Capa de presentación web y demostraciones

Aplica a `web/`, `ejecutar.py`, `demo_web.py` y a cualquier código que exponga la lógica de `app/` por HTTP. Las convenciones siguientes distinguen la aplicación persistente de las demos históricas.

- La capa web **no contiene reglas de negocio**: solo lee datos del formulario, llama a una función de `app/` y muestra el resultado. Si una regla falta, se agrega en `app/` con su prueba, nunca en el manejador.
- Todo texto del usuario o la base se escapa: Jinja mantiene el escape automático en `web/templates/`; la demo manual usa `html.escape`. No se usa `|safe` para texto de usuarios ni `innerHTML` con nombres o datos de formularios.
- Los `ErrorDominio` se capturan en un solo lugar y su mensaje se muestra tal cual (sección 7); los demás errores no se ocultan.
- Cada ruta (`/reportar`, `/diagnosticar`, …) se documenta en el docstring del módulo con la historia que ejercita.
- Las demos usan memoria y datos de ejemplo; la nueva web usa SQLite y fotos persistentes en `instance/`, excluida de Git junto a claves y archivos auxiliares. No se distribuyen registros de usuarios ni contraseñas predeterminadas.
- La demo no es un entregable de producción: la sesión por URL, los datos en memoria y las fotos guardadas en una carpeta temporal se declaran como limitaciones en el Acta EPS. Los reportes de ejemplo solo incluyen nombres de fotos.
- US10: `/exportar` entrega PDF o Excel (.xlsx) con los mismos filtros y conteos del panel. `app/exportaciones.py` valida el rol profesional, formato y longitud de los filtros; la capa HTTP agrega el tipo MIME, nombre de archivo y longitud del contenido.
- US11: el panel del campesino muestra diagnóstico, recomendación, profesional y fecha. `consultar_diagnostico` en `app/diagnosticos.py` valida el rol y la propiedad del reporte; la vista muestra un aviso si no existe diagnóstico y conserva el resultado después del cierre.

### Aplicación persistente

- `INSTRUCCIONES_WEB.md` es el manual de instalación y uso de la nueva web. El PDF del manual de la demo se conserva como documento histórico y no debe presentarse como la guía de las pantallas nuevas.
- Los formularios usan CSRF. El usuario se resuelve desde una sesión revocable, nunca de un parámetro de URL. Registro público con rol campesino fijado en el servidor; creación profesional mediante comando local.
- Las imágenes se validan por contenido, cantidad, tamaño y dimensiones, se normalizan y se sirven con autorización de rol/propiedad. La carpeta privada no se monta como recurso estático.
- La creación de usuario y perfil es transaccional. Se preserva la compatibilidad con las tablas y hashes anteriores. No se borran datos durante la inicialización.
- Recursos visuales y fuentes locales; sin emojis ni símbolos de afiliación oficial. Las animaciones respetan movimiento reducido y la funcionalidad dispone de validación del servidor.
- Las pruebas web mantienen CSRF activo y usan base/carpetas temporales. Se informa por separado la verificación funcional y la inspección visual en navegador.

## 11. Documentos de entrega

- Las actas de entrega parcial (`ACTA_EPS.md`) se guardan en `docs/`, en español, con las secciones: datos generales, alcance, evidencias verificables (comando y resultado), cumplimiento del DoD, limitaciones conocidas y firmas.
- Toda cifra del acta (pruebas, historias) debe poder reproducirse con un comando indicado en el mismo documento.
- Si una entrega cambia la instalación, la ejecución o el uso, el README se actualiza en el mismo commit (criterio 10 del DoD).

- Para cada sprint nuevo, conservar objetivo, criterios, backlog, evidencias y acta en `docs/`; no registrar reuniones ni aceptación sin evidencia.
- Las exportaciones devuelven bytes desde `app/`; la capa HTTP agrega el tipo MIME y el encabezado de descarga. Se reutilizan los conteos del panel.
- PDF escapa los textos de filtros y Excel los conserva como texto, sin ejecutar fórmulas. Los formatos, filtros y permisos llevan pruebas.
- Toda consulta de diagnóstico del campesino valida el rol y la propiedad del reporte en `app/`; la presentación escapa el texto y conserva el resultado después del cierre.
- El manual PDF conserva su diseño y se amplía cuando cambia el uso. Su actualización debe revisarse visualmente.
- Las historias nuevas se agregan a la **tabla principal del manual**, además de sus instrucciones. Para el Sprint 4, US10 figura en la página 1 y su guía está en las páginas 6 y 7; US11 figura en la página 1 y su guía está en la página 8.
- El alcance de la **primera página del DoD** incluye US1–US11 y Sprints 1–4. Se conserva la lista de diez criterios; una ampliación en un anexo no sustituye la actualización del alcance principal.
- La fecha de reunión se registra cuando el equipo o el solicitante confirma su realización. La reunión del Sprint 4 se realizó el **13 de octubre de 2026**. La fecha no acredita por sí sola asistentes, decisiones de aceptación, firmas ni integración a la rama principal.

**Trazabilidad del Sprint 4:**

| Historia / entregable | Archivo | Verificación |
|---|---|---|
| US10 — Exportación PDF y Excel | `app/exportaciones.py`, `demo_web.py` | `python -m pytest tests/test_us10_exportaciones.py -q` → 18 passed |
| US11 — Consulta de diagnóstico propio | `app/diagnosticos.py`, `demo_web.py` | `python -m pytest tests/test_us11_consulta_diagnostico.py -q` → 8 passed |
| Regresión completa | `tests/` | `python -m pytest -q` → 95 passed |
| Flujo HTTP de US10 y US11 | `scripts/verificar_sprint_4.py` | Descargas válidas, permisos y resultado visible antes y después del cierre |
| Planeación y reunión | `docs/SPRINT_4.md`, `docs/ACTA_SPRINT_4.md` y sus versiones PDF | Objetivo, criterios, tareas y reunión del 13 de octubre de 2026 |
| Backlog, pruebas y retrospectiva | `docs/PRODUCT_BACKLOG.md`, `docs/PLAN_PRUEBAS_SPRINT_4.md`, `docs/RETROSPECTIVA_SPRINT_4.md` | Estado de cada historia y pendientes de aceptación |
| Manual de usuario | `docs/MANUAL_USUARIO_PLANTAS.pdf` | Tabla principal con US10 y US11; guías de descarga y consulta |
| Definition of Done | `docs/DoD_Control_Plagas_Platano.pdf` | Alcance US1–US11 y Sprints 1–4 desde la primera página |

Los resultados de pruebas corresponden a la verificación técnica del 13 de octubre de 2026. Deben volver a comprobarse si cambia el código. El estándar conserva sus doce secciones y su historial; no sustituye las actas ni el manual.

## 12. Lista de revisión rápida

- [ ] Docstring de módulo con la historia
- [ ] Docstring en funciones públicas, con `Raises:` si aplica
- [ ] Anotaciones de tipo
- [ ] Comentarios que explican el porqué
- [ ] SQL parametrizado
- [ ] Pruebas nuevas o actualizadas y `python -m pytest` en verde
- [ ] Código web sin reglas de negocio y con texto escapado (sección 10)
- [ ] README y documentos de entrega actualizados (sección 11)
- [ ] Historias nuevas incluidas en la tabla principal del manual y en sus guías
- [ ] Alcance principal del DoD coherente con el sprint y el backlog
- [ ] Fecha de reunión y aceptación registradas por separado, sin atribuir acuerdos no confirmados

## Historial de cambios

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0 | 29 de septiembre de 2026 | Versión inicial (secciones 1 a 10 originales) |
| 1.1 | 30 de septiembre de 2026 | Se agregan la sección 10 (interfaz web de demostración) y la 11 (documentos de entrega); la lista de revisión pasa a ser la sección 12 y suma dos ítems |
| 1.2 | 13 de octubre de 2026 | Se documentan entregables de sprint, exportaciones y actualización del manual para US10 y US11 |
| 1.3 | 13 de octubre de 2026 | Se agrega trazabilidad de US10 y US11, verificación de 95 pruebas, actualización del alcance principal del manual y DoD y registro de la reunión; se corrige la limitación de fotos temporales |

| 1.4 | Entrega web persistente | Se documentan Flask/Jinja, sesiones revocables, perfiles, evidencias privadas, manual Markdown vigente y conservación de los documentos históricos de la demo. |
