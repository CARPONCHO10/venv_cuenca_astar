import streamlit as st
import folium
from astar_algorithm import AStarPathFinder
import time
import tempfile
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Ruta Óptima en Cuenca", layout="wide")

# --- DATOS COMPLETOS CON 10 PUNTOS ADICIONALES ---
CUENCA_NODOS = {
    # Puntos originales
    "Catedral Nueva": {"lat": -2.8975, "lon": -79.005, "descripcion": "Centro histórico de Cuenca"},
    "Parque Calderón": {"lat": -2.89741, "lon": -79.00438, "descripcion": "Corazón de Cuenca"},
    "Puente Roto": {"lat": -2.90423, "lon": -79.00142, "descripcion": "Monumento histórico"},
    "Museo Pumapungo": {"lat": -2.90607, "lon": -78.99681, "descripcion": "Museo de antropología"},
    "Terminal Terrestre": {"lat": -2.89222, "lon": -78.99277, "descripcion": "Terminal de autobuses"},
    "Mirador de Turi": {"lat": -2.92583, "lon": -79.0040, "descripcion": "Mirador con vista panorámica"},
    
    # 10 puntos adicionales
    "Mall del Río": {"lat": -2.88917, "lon": -79.01611, "descripcion": "Centro comercial principal"},
    "Universidad de Cuenca": {"lat": -2.90194, "lon": -79.01111, "descripcion": "Campus universitario central"},
    "Hospital Regional": {"lat": -2.91306, "lon": -78.99583, "descripcion": "Hospital principal de Cuenca"},
    "Parque de la Madre": {"lat": -2.89278, "lon": -79.00833, "descripcion": "Parque recreativo familiar"},
    "Mercado 10 de Agosto": {"lat": -2.89472, "lon": -79.00278, "descripcion": "Mercado tradicional"},
    "Iglesia de San Sebastián": {"lat": -2.89583, "lon": -79.00694, "descripcion": "Iglesia histórica"},
    "Plaza San Francisco": {"lat": -2.89639, "lon": -79.00361, "descripcion": "Plaza comercial"},
    "Museo de las Conceptas": {"lat": -2.89806, "lon": -79.00222, "descripcion": "Museo de arte religioso"},
    "Parque El Paraíso": {"lat": -2.89000, "lon": -78.99833, "descripcion": "Parque ecológico"},
    "Centro Histórico": {"lat": -2.89722, "lon": -79.00472, "descripcion": "Zona patrimonial"}
}

GRAPH_EDGES = {
    "Catedral Nueva": ["Parque Calderón", "Puente Roto", "Museo Pumapungo", "Plaza San Francisco"],
    "Parque Calderón": ["Catedral Nueva", "Terminal Terrestre", "Puente Roto", "Centro Histórico"],
    "Puente Roto": ["Catedral Nueva", "Parque Calderón", "Museo Pumapungo", "Mirador de Turi"],
    "Museo Pumapungo": ["Catedral Nueva", "Puente Roto", "Terminal Terrestre", "Hospital Regional"],
    "Terminal Terrestre": ["Parque Calderón", "Museo Pumapungo", "Mirador de Turi", "Parque El Paraíso"],
    "Mirador de Turi": ["Puente Roto", "Terminal Terrestre", "Hospital Regional"],
    "Mall del Río": ["Universidad de Cuenca", "Parque de la Madre"],
    "Universidad de Cuenca": ["Mall del Río", "Parque de la Madre", "Iglesia de San Sebastián"],
    "Hospital Regional": ["Museo Pumapungo", "Mirador de Turi", "Parque El Paraíso"],
    "Parque de la Madre": ["Mall del Río", "Universidad de Cuenca", "Mercado 10 de Agosto"],
    "Mercado 10 de Agosto": ["Parque de la Madre", "Iglesia de San Sebastián", "Plaza San Francisco"],
    "Iglesia de San Sebastián": ["Universidad de Cuenca", "Mercado 10 de Agosto", "Centro Histórico"],
    "Plaza San Francisco": ["Catedral Nueva", "Mercado 10 de Agosto", "Museo de las Conceptas"],
    "Museo de las Conceptas": ["Plaza San Francisco", "Centro Histórico"],
    "Parque El Paraíso": ["Terminal Terrestre", "Hospital Regional"],
    "Centro Histórico": ["Parque Calderón", "Iglesia de San Sebastián", "Museo de las Conceptas"]
}

# --- INICIALIZACIÓN DEL BUSCADOR DE RUTAS ---
pathfinder = AStarPathFinder(CUENCA_NODOS, GRAPH_EDGES)

# --- FUNCIÓN PARA CREAR MAPA ---
def crear_mapa(ruta=None, origen="", destino=""):
    """Crea un mapa de Folium con la ruta y puntos de interés"""
    mapa = folium.Map(location=[-2.900, -79.005], zoom_start=13)
    
    # Marcar todos los puntos
    for nombre, info in CUENCA_NODOS.items():
        if nombre == origen:
            color = "red"
            icono = "play"
        elif nombre == destino:
            color = "blue" 
            icono = "flag"
        elif ruta and nombre in ruta:
            color = "purple"
            icono = "circle"
        else:
            color = "green"
            icono = "info-sign"
        
        folium.Marker(
            [info["lat"], info["lon"]],
            popup=f"<b>{nombre}</b><br>{info['descripcion']}",
            tooltip=nombre,
            icon=folium.Icon(color=color, icon=icono)
        ).add_to(mapa)

    # Dibujar la ruta óptima solo si existe una ruta
    if ruta and len(ruta) > 1:
        coordenadas_ruta = []
        for lugar in ruta:
            coord = [CUENCA_NODOS[lugar]["lat"], CUENCA_NODOS[lugar]["lon"]]
            coordenadas_ruta.append(coord)

        folium.PolyLine(
            coordenadas_ruta,
            color="purple",
            weight=6,
            opacity=0.8,
            tooltip="Ruta Óptima A*",
            dash_array='5, 10'
        ).add_to(mapa)

        # Ajustar el mapa para que muestre toda la ruta
        mapa.fit_bounds(coordenadas_ruta)
    
    return mapa

# --- INTERFAZ DE STREAMLIT ---
st.title("🗺️ Sistema de Navegación A* - Ciudad de Cuenca")
st.markdown("### Implementación del Algoritmo A* para Optimización de Rutas")

col1, col2 = st.columns([1, 2])

# Variable para controlar si se ha calculado una ruta
ruta_calculada = None
distancia_calculada = 0
nodos_explorados_calculados = 0
tiempo_ejecucion = 0

with col1:
    st.subheader("Configuración de Ruta")
    origen = st.selectbox("📍 Punto de Origen:", list(CUENCA_NODOS.keys()))
    destino = st.selectbox("🎯 Punto de Destino:", list(CUENCA_NODOS.keys()))
    
    if st.button("🚀 Calcular Ruta Óptima", type="primary"):
        if origen == destino:
            st.error("¡Selecciona puntos de origen y destino diferentes!")
        else:
            with st.spinner("Buscando la mejor ruta con A*..."):
                start_time = time.time()
                ruta, distancia, nodos_explorados = pathfinder.find_path(origen, destino)
                end_time = time.time()
                tiempo_ejecucion = end_time - start_time

            if ruta:
                st.success("¡Ruta óptima encontrada!")
                ruta_calculada = ruta
                distancia_calculada = distancia
                nodos_explorados_calculados = nodos_explorados
                
                # Mostrar resultados
                st.metric("Distancia total", f"{distancia:.2f} km")
                st.metric("Tiempo de ejecución", f"{tiempo_ejecucion:.4f} segundos")
                st.metric("Nodos explorados", nodos_explorados)
                
                st.write(f"**Ruta más corta:**")
                for i, punto in enumerate(ruta):
                    st.write(f"{i+1}. {punto}")
            else:
                st.error("No se pudo encontrar una ruta entre los puntos seleccionados.")

# Mostrar el mapa en la columna 2
with col2:
    if ruta_calculada:
        st.subheader("Visualización de la Ruta")
        mapa = crear_mapa(ruta_calculada, origen, destino)
    else:
        st.subheader("Mapa de Puntos de Interés en Cuenca")
        # Mostrar mapa básico con todos los puntos (sin ruta)
        mapa = crear_mapa()
    
    # Guardar mapa temporalmente y mostrarlo
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
        mapa.save(tmp_file.name)
        html_content = open(tmp_file.name, 'r', encoding='utf-8').read()
    
    st.components.v1.html(html_content, height=600)
    
    # Limpiar archivo temporal
    os.unlink(tmp_file.name)

# --- INFORMACIÓN ADICIONAL ---
with st.expander("📊 Análisis y Fundamentación Técnica"):
    st.markdown("""
    ### Fundamentación del Algoritmo A*
    
    **Función de Evaluación:** `f(n) = g(n) + h(n)`
    - **g(n):** Costo real desde el nodo inicial hasta el nodo actual (Distancia de Haversine)
    - **h(n):** Heurística (distancia euclidiana al objetivo)
    
    **Características:**
    - **Completo:** Siempre encuentra una solución si existe
    - **Óptimo:** Encuentra la ruta más corta
    - **Eficiente:** Usa heurística para guiar la búsqueda
    
    **Ventajas sobre otros algoritmos:**
    - **BFS:** Explora todos los caminos por niveles (menos eficiente)
    - **DFS:** Puede quedar atrapado en caminos largos
    - **A*:** Combina lo mejor de ambos usando información heurística
    """)

with st.expander("🔍 Modelado del Grafo"):
    st.write("**Nodos (16 Puntos de Interés):**")
    for nombre, info in CUENCA_NODOS.items():
        st.write(f"- **{nombre}**: {info['descripcion']} (Lat: {info['lat']}, Lon: {info['lon']})")
    
    st.write("**Aristas (Conexiones):**")
    st.json(GRAPH_EDGES)

with st.expander("📈 Resultados y Análisis"):
    if ruta_calculada:
        st.write("**Análisis de Eficiencia:**")
        st.write(f"- **Total de nodos en el grafo:** {len(CUENCA_NODOS)}")
        st.write(f"- **Nodos explorados por A*:** {nodos_explorados_calculados}")
        st.write(f"- **Eficiencia de búsqueda:** {(nodos_explorados_calculados/len(CUENCA_NODOS))*100:.1f}% del grafo explorado")
        st.write(f"- **Longitud de la ruta:** {len(ruta_calculada)} segmentos")
        st.write(f"- **Distancia total:** {distancia_calculada:.2f} km")
        st.write(f"- **Tiempo de ejecución:** {tiempo_ejecucion:.4f} segundos")
    else:
        st.write("Calcula una ruta para ver el análisis de eficiencia.")

# --- PIE DE PÁGINA ---
st.markdown("---")
st.markdown("**Guía Práctica 2 - Inteligencia Artificial** | *Tecnología Superior en Desarrollo de Software| Realizado por Steven Carpio*")