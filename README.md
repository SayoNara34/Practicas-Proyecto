# Sistema Web Control de Plagas en Plátano

Aplicación para que campesinos del Llano Oriental reporten afectaciones en sus cultivos de plátano con fotos y ubicación, y para que un profesional agrónomo las diagnostique y haga seguimiento hasta resolverlas.

Proyecto académico — Politécnico Grancolombiano, Tecnología en Desarrollo de Software, desarrollado con Scrum.
|||
|---|---|
| **Docente** | Edilberto Torres Ortiz |
| **Scrum Master** | Nicolás Abril Cárdenas |
| **Product Owner** | Juan Miguel Parra Garzón |
| **Equipo de desarrollo** | Santiago Cortez Mojica |

## Estado del proyecto

Sprints 0 a 3 completados según la documentación previa. Sprint 4 implementado y probado; reunión realizada el 13 de octubre de 2026; integración y aceptación formal por completar:

| Sprint | Historias | Contenido |
|---|---|---|
| 1 | US1, US2, US3 | Registro del campesino, reporte con fotos, ubicación del cultivo |
| 2 | US4, US5, US6 | Reportes pendientes, diagnóstico del profesional, estado del reporte |
| 3 | US7, US8, US9 | Notificaciones, cierre de caso, panel de estadísticas |
| 4 | US10, US11 | Exportación PDF/Excel y consulta de diagnóstico propio; aceptación pendiente |

Planeación y criterios: [Sprint 4](docs/SPRINT_4.md). Entrega y aceptación: [Acta del Sprint 4](docs/ACTA_SPRINT_4.md).

> **Nota:** el repositorio contiene la lógica de negocio y la base de datos, con sus pruebas unitarias, un recorrido en consola y una demo web de demostración. La interfaz web de producción (API y pantallas definitivas) se construye sobre esta misma lógica.

## Requisitos

- Python 3.10 o superior (probado con 3.14)
- `pip`
- No se necesita instalar una base de datos: se usa SQLite, que ya viene con Python.

## Instalación

```bash
git clone https://github.com/SayoNara34/Practicas-Proyecto.git
cd Practicas-Proyecto

# Opcional pero recomendado: entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

python -m pip install -r requirements.txt
python -m pytest                #95 passed
```

## Cómo correr el proyecto

Todos los comandos se ejecutan desde la carpeta raíz (la que contiene `app`, `tests` y `schema.sql`).

Para ver la **demo web** (pantallas de campesino y profesional, sobre la misma lógica):

```bash
python demo_web.py          # abrir http://localhost:8000
```

El profesional puede filtrar las estadísticas por zona y tipo de plaga, pulsar **Filtrar** y usar **Descargar PDF** o **Descargar Excel**. El campesino ve en **Mis reportes** el diagnóstico, recomendación, profesional y fecha; si aún no existe, aparece un aviso de espera. El resultado sigue visible después del cierre. Los filtros son coincidencias exactas sin distinguir mayúsculas; vacíos incluyen todos los reportes. La exportación incluye los cuatro estados, total, filtros y fecha UTC.

Usuarios de ejemplo: `carlos@finca.co` (campesino) y `laura@agro.co` (profesional), contraseña `clave1234`. Usa base de datos en memoria; al reiniciar vuelve a los datos de ejemplo.

Para ver el flujo completo en la consola (registro → reporte → diagnóstico → notificación → cierre → estadísticas):

```bash
python demo.py
```

El script usa una base de datos en memoria, así que se puede ejecutar cuantas veces se quiera sin dejar archivos.

Para usar la lógica desde otro código:

```python
from app import db, usuarios, reportes

conn = db.conectar("plagas.db")   # o ":memory:" para no guardar nada
db.inicializar(conn)

campesino = usuarios.registrar_usuario(conn, "Carlos", "carlos@finca.co", "clave1234")
reportes.crear_reporte(conn, campesino, "Hojas con manchas", "Vereda La Esperanza", ["hoja.jpg"])
```

## Cómo correr las pruebas

```bash
python -m pytest            # todas las pruebas
python -m pytest -v         # con el nombre de cada prueba
python -m pytest tests/test_us7_estados_notificaciones.py   # solo una historia
```

Resultado esperado: `95 passed`. Las pruebas usan una base de datos en memoria, por lo que no afectan ningún dato real.

> Ejecutar siempre `python -m pytest` desde la carpeta raíz del proyecto. Si se corre desde otra carpeta, Python no encuentra el paquete `app`.

Para verificar las descargas en una demo aislada (se inicia y cierra automáticamente):

```bash
python scripts/verificar_sprint_4.py
```

El manual de uso está en [docs/MANUAL_USUARIO_PLANTAS.pdf](docs/MANUAL_USUARIO_PLANTAS.pdf). Se conserva su diseño original y se agrega la guía del Sprint 4. ReportLab y openpyxl generan los archivos; pypdf se utiliza para verificarlos en las pruebas.

## Arquitectura

El sistema está organizado en capas simples, cada archivo con una sola responsabilidad:

```
Practicas-Proyecto/
├── README.md
├── schema.sql                  # Tablas: usuario, reporte, foto, diagnostico, notificacion
├── app/                        # Lógica de negocio
│   ├── db.py                   # Conexión a SQLite y creación de tablas
│   ├── errores.py              # Excepciones de dominio
│   ├── usuarios.py             # US1  Registro e inicio de sesión
│   ├── reportes.py             # US2, US3, US4, US6  Reportes, ubicación y listados
│   ├── estados.py              # US7  Estados del reporte y notificación automática
│   ├── diagnosticos.py         # US5, US8, US11  Diagnóstico, cierre y consulta propia
│   ├── notificaciones.py       # US7  Consulta y lectura de notificaciones
│   ├── estadisticas.py         # US9  Conteo por estado, zona y tipo de plaga
│   └── exportaciones.py        # US10 Exportación de estadísticas a PDF y Excel
├── tests/                      # Pruebas unitarias con pytest, una por área
├── docs/                       # Documentación del equipo
│   ├── Diagramas/              # Casos de uso, clases, estados, secuencia y paquetes
│   ├── Actas/                  # Dailys, sprints y retrospectivas del equipo
│   ├── DoD_Control_Plagas_Platano.pdf   # Definition of Done
│   ├── ESTANDAR_DOCUMENTACION.md        # Estándar de comentarios y docstrings (v1.1)
│   ├── MANUAL_USUARIO_PLANTAS.pdf       # Manual de usuario, ampliado para US10 y US11
│   ├── Product_Backlog.xlsx             # Product Backlog con el avance por sprint
│   ├── SPRINT_4.pdf                     # Planeación del Sprint 4
│   ├── ACTA_SPRINT_4.pdf                # Acta del Sprint 4
│   ├── ACTA_EPS.md                      # Acta de Entrega Parcial de Software
│   └── REVIEW SPRINT.txt                # Enlace al tablero Miro de la Sprint Review
├── scripts/
│   └── verificar_sprint_4.py   # Verificación HTTP real de US10 y US11
├── demo.py                     # Recorrido de demostración en consola
├── demo_web.py                 # Demo web (http.server) sobre la lógica de app/
├── requirements.txt / pytest.ini
└── .gitignore
```

**Capas.** La presentación (`demo_web.py`, `demo.py`) solo llama a los módulos de `app/`; no contiene reglas de negocio. Dentro de `app/` las dependencias van hacia abajo: `diagnosticos` usa `estados`, `reportes` y `usuarios`; `estados` usa `reportes`; `reportes` usa `usuarios`; `exportaciones` usa `estadisticas`; y casi todos comparten `db` (conexión) y `errores` (excepciones).

**Roles.** Hay dos: *campesino* (reporta, consulta sus reportes, notificaciones y diagnóstico) y *profesional* (ve pendientes, diagnostica, cierra casos, consulta y exporta estadísticas). Las funciones que dependen del rol lo validan antes de actuar (`usuarios.exigir_rol`).

**Ciclo de vida del reporte.** Es la regla central del sistema:

```
Reportado ──► En revisión ──► Diagnosticado ──► Resuelto
    └──────────────────────────►┘
```
Un reporte también puede pasar directo de "Reportado" a "Diagnosticado". No se permiten otros saltos, y cada cambio válido genera una notificación para el campesino dueño del reporte (`estados.py`).


**Base de datos.** SQLite mediante el módulo estándar `sqlite3`, con consultas parametrizadas. Las contraseñas se guardan con PBKDF2 y sal, nunca en texto plano.

## Estándar de código

Las convenciones de comentarios, docstrings y nombres están en [`docs/ESTANDAR_DOCUMENTACION.md`](docs/ESTANDAR_DOCUMENTACION.md). Aplican a todo código nuevo y hacen parte del Definition of Done.

## Trabajo en equipo

- Se trabaja por sprints con Scrum (planeación, daily, review y retrospectiva).
- Una historia se considera terminada cuando cumple el [Definition of Done](docs/DoD_Control_Plagas_Platano.pdf) del equipo.
- Los mensajes de commit indican la historia: `US7: notificar al campesino al cambiar el estado`.
