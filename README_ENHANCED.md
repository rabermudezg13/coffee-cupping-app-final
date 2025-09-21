# ☕ Coffee Cupping App - Professional Edition

Una aplicación moderna y profesional para la evaluación de café con funcionalidades avanzadas de análisis, compartición y colaboración.

## 🚀 Características Principales

### 1. 🔗 Función de Compartir
- **URLs únicos** para cada sesión de catación
- **Páginas públicas** con visualización atractiva de resultados
- **Botones de compartir** para redes sociales (Twitter, Facebook, LinkedIn, WhatsApp, Telegram)
- **Tarjetas de compartir** personalizadas para redes sociales
- **Códigos QR** para acceso rápido desde dispositivos móviles
- **Analytics de compartición** para medir engagement

### 2. 🕶️ Modo Anónimo
- **Activación por sesión** - el usuario puede elegir si mostrar su identidad
- **Persistencia en base de datos** - la configuración se mantiene entre sesiones
- **Visualización como "Anonymous Taster"** en resultados compartidos
- **Configuración por defecto** en ajustes de usuario

### 3. 📊 Análisis Avanzado con Python
- **Promedios automáticos** de atributos sensoriales
- **Rankings de categorías** más destacadas
- **Visualizaciones interactivas** con Plotly:
  - Gráficos radar para perfiles sensoriales
  - Histogramas de distribución de puntajes
  - Mapas de calor para tendencias temporales
  - Gráficos de barras para análisis de orígenes
- **Tendencias de la comunidad**:
  - Sabores más mencionados
  - Cafés con mejores promedios
  - Evolución temporal de calidad
  - Análisis geográfico por origen

### 4. 🎨 UX/UI Moderna y Adaptativa
- **Diseño responsive** - perfecto en móvil, tablet y escritorio
- **Temas claro/oscuro** intercambiables
- **Animaciones suaves** con CSS modernas
- **Tipografía moderna** con gradientes y efectos
- **Componentes interactivos** (toggles, tabs, expanders)
- **Métricas visuales** con tarjetas animadas
- **Scrollbar personalizada** y elementos de interfaz refinados

## 🏗️ Arquitectura Modular

```
coffee_cupping_final/
├── config.py                    # Configuración central
├── streamlit_app_new.py         # Aplicación principal mejorada
├── requirements.txt             # Dependencias actualizadas
├── components/
│   └── cupping_interface.py     # Interfaz de catación mejorada
├── database/
│   └── db_manager.py            # Gestión de base de datos con SQLite/JSON
├── pages/
│   ├── public_cupping.py        # Páginas públicas de resultados
│   └── analytics_dashboard.py   # Dashboard de análisis
├── styles/
│   └── themes.py                # Temas y estilos modernos
└── utils/
    ├── analytics.py             # Motor de análisis con Python
    └── sharing.py               # Sistema de compartición
```

## 📦 Instalación y Configuración

### Dependencias Requeridas
```bash
pip install streamlit plotly pandas qrcode[pil] pillow reportlab matplotlib numpy
```

### Variables de Entorno
```bash
# Opcional: URL base para compartir (por defecto usa Streamlit Cloud)
SHARE_URL_BASE=https://tu-dominio.com

# Opcional: Base de datos (por defecto usa JSON)
DATABASE_URL=sqlite:///cupping.db
```

### Ejecutar la Aplicación
```bash
# Versión mejorada
streamlit run streamlit_app_new.py

# Versión original (para comparación)
streamlit run streamlit_app.py
```

## 🎯 Funcionalidades Detalladas

### Sistema de Compartición
```python
# Generar URL de compartir
share_url = sharing_manager.generate_share_url(share_id)

# Crear tarjeta visual para redes sociales
card_image = sharing_manager.create_share_card_image(session_data)

# Enlaces directos a redes sociales
social_links = sharing_manager.generate_social_share_links(session_data, share_url)
```

### Análisis de Datos
```python
# Obtener tendencias de la comunidad
trends = analytics.get_community_trends()

# Crear visualización radar
radar_chart = analytics.create_radar_chart(session_data, title)

# Generar insights automáticos
insights = analytics.generate_session_insights(session_data)
```

### Base de Datos
```python
# Guardar sesión con modo anónimo
share_id = db.save_cupping_session(session_data, anonymous_mode=True)

# Obtener sesión por ID de compartir
session = db.get_session_by_share_id(share_id)

# Registrar evento de analytics
db.log_analytics_event('social_share', session_id=share_id, data={'platform': 'twitter'})
```

## 📊 Métricas de Éxito

### KPIs Implementados
- **Engagement de Compartición**:
  - Número de URLs copiadas
  - Comparticiones en redes sociales
  - Visualizaciones de páginas públicas
  - Descargas de tarjetas de compartir

- **Uso de Modo Anónimo**:
  - Porcentaje de sesiones anónimas
  - Conversión de usuarios anónimos

- **Tiempo en la Aplicación**:
  - Sesiones completadas vs iniciadas
  - Tiempo promedio por sesión de catación

- **Calidad de Datos**:
  - Completitud de perfiles de sabor
  - Consistencia en puntajes

### Dashboard de Analytics
El dashboard incluye:
- 📈 **Análisis de Puntajes**: Distribución y tendencias
- 🌍 **Tendencias Geográficas**: Análisis por origen
- 🍃 **Insights de Sabores**: Perfiles más populares
- ⏰ **Patrones Temporales**: Actividad en el tiempo
- 🎖️ **Métricas de Calidad**: Distribución de grados SCA

## 🎨 Temas y Personalización

### Modo Oscuro/Claro
```python
# Alternar tema
toggle_theme()

# Obtener colores actuales
colors = get_theme_colors()

# Aplicar estilos personalizados
apply_custom_css()
```

### Componentes Reutilizables
```python
# Crear tarjeta de métrica
metric_card = create_metric_card("Total Sessions", "42", "+12%")

# Renderizar toggle de tema
render_theme_toggle()
```

## 🚀 Deployment

### Streamlit Cloud
1. Conectar repositorio GitHub
2. Usar `streamlit_app_new.py` como punto de entrada
3. Las dependencias se instalan automáticamente desde `requirements.txt`

### Variables de Configuración
- `SHARE_URL_BASE`: URL base para links de compartir
- `DATABASE_URL`: URL de base de datos (opcional)

## 🔄 Migración desde Versión Anterior

La nueva versión mantiene compatibilidad con datos existentes:

```python
# Los datos JSON existentes se migran automáticamente
# El formato de sesiones es compatible
# Los usuarios existentes pueden seguir usando la app
```

## 🤝 Contribución

### Estructura de Commits
```bash
git commit -m "feat: agregar modo anónimo con persistencia"
git commit -m "fix: corregir error en visualización de radar"
git commit -m "style: mejorar responsive design en móviles"
```

### Testing
```bash
# Ejecutar tests locales
python -m pytest tests/

# Verificar compatibilidad móvil
streamlit run streamlit_app_new.py --server.headless true
```

## 📄 Licencia

© 2025 Rodrigo Bermudez - Cafe Cultura LLC

---

## 🔗 Links Útiles

- **Demo Live**: [https://coffee-cupping-app-final.streamlit.app](https://coffee-cupping-app-final.streamlit.app)
- **Documentación SCA**: [Specialty Coffee Association](https://sca.coffee/)
- **Streamlit Docs**: [https://docs.streamlit.io](https://docs.streamlit.io)

---

*Aplicación desarrollada con ❤️ para la comunidad cafetera profesional*