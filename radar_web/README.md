# 🌌 SE-MAMO-GEMINI: Sistema de Radar LCC AI

## 📋 Descripción del Proyecto

SE-MAMO-GEMINI es un sistema integral de monitoreo y análisis de tráfico que combina tecnologías de detección de velocidad, visualización de datos en tiempo real y análisis inteligente. El sistema utiliza radares TCP para capturar datos de vehículos, procesarlos y presentarlos en una interfaz web moderna basada en Streamlit con un diseño visual inspirado en el estilo "Gemini Dark".

---

## 🎯 Funcionalidades Principales

### 1. **Monitoreo en Tiempo Real**
- Captura continua de datos de velocidad de vehículos
- Detección automática de infracciones (>60 km/h)
- Estado operativo de sensores/radares
- Feed de capturas fotográficas de eventos

### 2. **Análisis de Datos**
- Estadísticas descriptivas (promedio, máximo, mínimo)
- Mapa de calor de intensidad de tráfico por hora
- Distribución de velocidad por radar
- Tendencias temporales (diarias, semanales, horarias)

### 3. **Sistema de Alertas**
- Alertas automáticas por excesos de velocidad
- Clasificación de infracciones graves
- Notificaciones visuales diferenciadas

### 4. **Gestión Multimedia**
- Búsqueda de videos por fecha y ubicación
- Descarga de evidencia en formato MP4
- Visualización de capturas fotográficas

### 5. **Exportación de Datos**
- Descarga de reportes en CSV
- Datos crudos para auditoría externa

---

## 🖥️ Manual de Comportamiento

### Flujo de Usuario

```
┌─────────────────────────────────────────────────────────────┐
│                    PÁGINA PRINCIPAL                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Inicio     │  │  Alertas    │  │  Estadísticas       │  │
│  │  (Dashboard)│  │  (>55km/h)  │  │  (Análisis profundo)│  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Búsqueda Videos | Infracciones Graves (>60km/h)   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Uso de Cada Módulo

#### **Página Principal (`app.py`)**
1. Seleccionar ubicación del radar en el filtro
2. Filtrar por tipo de vehículo
3. Ajustar rango de fechas
4. Visualizar KPIs: Tráfico Total, Vel. Promedio, Infracciones, Récord
5. Explorar gráficos de dispersión y distribución
6. Revisar capturas recientes
7. Consultar estado de sensores

#### **Alertas (`2_alertas.py`)**
1. Visualizar alertas activas (>55 km/h)
2. Filtrar por radar y período
3. Ver galería de imágenes con evidencia
4. Revisar evolución mensual de alertas

#### **Infracciones Graves (`1_🚨_Infracciones_Graves.py`)**
1. Definir rango de fechas (desde/hasta)
2. Filtrar por radar y tipo de vehículo
3. Visualizar estadísticas: Total graves, Velocidad máxima, Punto crítico
4. Explorar galería de evidencias fotográficas

#### **Búsqueda de Videos (`3_Busqueda_Videos.py`)**
1. Seleccionar fecha del evento
2. Elegir ubicación del radar
3. Ajustar filtro de velocidad mínima
4. Visualizar timeline de eventos
5. Reproducir y descargar videos disponibles

#### **Estadísticas (`4_📊_Estadisticas.py`)**
1. Ver tabla de vehículos detectados
2. Analizar tendencias temporales
3. Comparar radares
4. Identificar patrones por día y hora
5. Explorar detalle por radar individual

---

## 📁 Estructura del Código

### Archivo: `radar_web/app.py`
**Propósito**: Página principal del dashboard

| Sección | Descripción | Líneas |
|---------|-------------|--------|
| Configuración | Page config de Streamlit | 12-17 |
| Rutas | Definición de paths para DB y archivos | 21-25 |
| CSS Maestro | Estilos Gemini Dark UI + Sidebar Pro | 30-145 |
| Motor de Datos | Función `get_data()` con cache | 150-170 |
| Header & Filtros | Título y controles de filtro | 175-199 |
| KPIs | Tarjetas con métricas principales | 221-225 |
| Panel Pro | Gráfico de dispersión Plotly | 227-247 |
| Resumen | Resumen inteligente lateral | 249-263 |
| Feed | Capturas recientes con imágenes | 271-286 |
| Sensores | Estado de sensores online/offline | 300-324 |
| Analytics | Mapa de calor y box plots | 331-361 |
| Auditoría | Tabla de estadísticas por radar | 363-381 |
| Neural Summary | Terminal con insights IA | 389-408 |
| Export | Descarga de datos CSV | 411-424 |

---

### Archivo: `radar_web/pages/1_🚨_Infracciones_Graves.py`
**Propósito**: Monitoreo de infracciones (>60 km/h)

| Sección | Descripción | Líneas |
|---------|-------------|--------|
| Configuración | Page config especializado | 11 |
| CSS | Estilos con gradientes de alerta | 21-104 |
| Lógica | Función `cargar_graves()` | 110-122 |
| UI | Header con gradiente de alerta | 127-131 |
| Filtros | Contenedor con selects y date inputs | 133-144 |
| KPIs | Métricas de infracciones graves | 152-172 |
| Galería | Grid de evidencias fotográficas | 174-203 |

---

### Archivo: `radar_web/pages/2_alertas.py`
**Propósito**: Monitor de alertas (>55 km/h)

| Sección | Descripción | Líneas |
|---------|-------------|--------|
| Configuración | Page config expandido | 12-17 |
| CSS | Estilos Gemini Dark | 29-68 |
| Motor | `get_alert_data()` filtrado | 73-87 |
| Header | Título con gradiente | 94 |
| Filtros | Selectores de radar y fecha | 101-107 |
| KPIs | Métricas de alertas | 110-115 |
| Galería | Grid de imágenes con evidencia | 122-152 |
| Evolución | Gráfico mensual | 156-166 |

---

### Archivo: `radar_web/pages/3_Busqueda_Videos.py`
**Propósito**: Sistema de video forense

| Sección | Descripción | Líneas |
|---------|-------------|--------|
| Configuración | Page config wide | 11 |
| CSS | Estilos con reproductor | 21-103 |
| Lógica DB | `cargar_infracciones()` | 108-121 |
| Lógica Videos | `obtener_videos_disponibles()` | 123-130 |
| UI Header | Título con gradiente | 135-139 |
| Parámetros | Filtros de búsqueda | 141-156 |
| Timeline | Dataframe de eventos | 169-173 |
| Visor | Reproductor y descarga | 182-191 |

---

### Archivo: `radar_web/pages/4_📊_Estadisticas.py`
**Propósito**: Panel de análisis estadístico

| Sección | Descripción | Líneas |
|---------|-------------|--------|
| Configuración | Page config wide | 14-19 |
| CSS | Estilos con tabla personalizada | 33-119 |
| DB | `conectar_db()` | 121-127 |
| Datos | `obtener_datos_historial()` | 129-152 |
| Tabla | `render_custom_table()` | 154-216 |
| Header | Título con gradiente | 221-225 |
| Filtros | Sidebar con radares | 239-242 |
| KPIs | Métricas con comparación | 257-265 |
| Tendencias | Evolución diaria y heatmap | 268-299 |
| Análisis Radar | Comparativa y box plots | 304-328 |
| Patrones | Día y hora | 331-360 |
| Detalle | Expander por radar | 365-377 |

---

### Archivo: `radar_web/campo_estrellas.html`
**Propósito**: Visualización de campo de estrellas interactivo

| Componente | Descripción |
|------------|-------------|
| Canvas | Elemento principal de renderizado |
| Clase `Estrella` | Estrellas individuales con parallax y parpadeo |
| Clase `EstrellaFugaz` | Estrellas fugaces con cola de gradiente |
| `drawNebula()` | Nebulosa de fondo con gradiente radial |
| `animate()` | Loop principal de animación |

---

## 🎨 Estilo Visual Gemini Dark

### Colores Principales

| Color | Valor | Uso |
|-------|-------|-----|
| Fondo Principal | `#0b0f19` | Base de la aplicación |
| Fondo Tarjeta | `#131722` | Cards y contenedores |
| Acento Azul | `#4285F4` | Primario Gemini |
| Acento Rosa | `#E91E63` | Alertas y énfasis |
| Acento Violeta | `#9C27B0` | Gradientes |
| Texto Blanco | `#ffffff` | Títulos principales |
| Texto Gris | `#9aa0a6` | Subtítulos |

### Elementos CSS Destacados

```css
/* Gradiente de texto */
.gradient-text {
    background: linear-gradient(90deg, #4285F4, #9C27B0, #E91E63);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Tarjeta Gemini */
.gemini-card {
    background-color: #131722;
    border-radius: 24px;
    border: 1px solid rgba(100, 149, 237, 0.08);
    padding: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0b0f19;
    border-right: 1px solid rgba(100, 149, 237, 0.05);
}
```

---

## 🗄️ Base de Datos

### Estructura de la Tabla `historial`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | Identificador único |
| fecha | DATE | Fecha del registro |
| hora | TIME | Hora del registro |
| radar | TEXT | Identificador del radar |
| velocidad | REAL | Velocidad detectada (km/h) |
| tipo | TEXT | Tipo de vehículo |
| placa | TEXT | Placa del vehículo |
| foto | TEXT | Ruta de imagen |

---

## 🚀 Tecnologías Utilizadas

- **Frontend**: Streamlit, Plotly, HTML/CSS/JS
- **Backend**: Python, SQLite
- **Visualización**: Plotly Express, Plotly Graph Objects
- **Estilos**: CSS Personalizado (Gemini Dark)
- **Animaciones**: Canvas API (campo_estrellas.html)

---

## 📦 Dependencias

```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
sqlite3 (estándar)
```

---

## 📄 Licencia

© 2024 LCC Analytics - Sistema v2.5
