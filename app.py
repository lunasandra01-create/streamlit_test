import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página (debe ser lo primero)
st.set_page_config(
    page_title="Recetas Express Dashboard", 
    page_icon="🥑", 
    layout="wide" # Para usar todo el ancho de la pantalla
)

# 2. Títulos y subtítulos llamativos
st.title("🥗✨ ¡Súper Dashboard de Recetas Rápidas! 🚀🥑")
st.markdown("### *Descubre las mejores opciones para comer delicioso y sin perder tiempo* ⏱️😋")
st.divider()

# 3. Carga de los datos
# Uso @st.cache_data para que no se recargue el CSV cada vez que interactuamos con la app
@st.cache_data
def cargar_datos():
    # En un entorno real, lee de 'data/datos.csv'
    # Si el archivo no se encuentra, mostramos un error amigable.
    try:
        df = pd.read_csv("data/datos.csv")
        return df
    except FileNotFoundError:
        st.error("🚨 ¡Ups! No pude encontrar el archivo 'data/datos.csv'. Por favor verifica la ruta.")
        return pd.DataFrame() # Devuelve un df vacío para que la app no colapse

df = cargar_datos()

if not df.empty:
    # 4. Filtros en la barra lateral (Sidebar)
    st.sidebar.header("🔍 ¡Filtra a tu gusto!")
    
    # Filtro por Categoría
    categorias_disponibles = df["category"].unique().tolist()
    categorias_seleccionadas = st.sidebar.multiselect(
        "🌮 Elige las Categorías:",
        options=categorias_disponibles,
        default=categorias_disponibles
    )
    
    # Filtro por Dificultad
    dificultades_disponibles = df["difficulty"].unique().tolist()
    dificultades_seleccionadas = st.sidebar.multiselect(
        "🏋️ Nivel de Dificultad:",
        options=dificultades_disponibles,
        default=dificultades_disponibles
    )
    
    # Checkbox para Veganismo
    solo_veganas = st.sidebar.checkbox("🌱 Mostrar solo opciones Veganas")

    # Aplicar los filtros al DataFrame
    df_filtrado = df[
        (df["category"].isin(categorias_seleccionadas)) &
        (df["difficulty"].isin(dificultades_seleccionadas))
    ]
    if solo_veganas:
        df_filtrado = df_filtrado[df_filtrado["is_vegan"] == True]

    # 5. Checkbox para ver la vista previa de datos
    if st.checkbox("👀 Mostrar vista previa de los datos (Top 10 filas)"):
        # Mostramos las primeras 10 filas del DF filtrado de manera interactiva
        st.dataframe(df_filtrado.head(10), use_container_width=True)

    st.write("---")

    # 6. Creación de Gráficos con Plotly Express
    if df_filtrado.empty:
        st.warning("⚠️ ¡Oh no! No hay recetas que coincidan con tus filtros. Prueba cambiando las opciones.")
    else:
        # Layout usando 2 columnas para los primeros dos gráficos
        col1, col2 = st.columns(2)

        with col1:
            # GRÁFICO 1: Gráfico de barras horizontales (Top Recetas por Popularidad)
            df_top = df_filtrado.sort_values(by="user_popularity", ascending=False).head(10)
            fig_barras = px.bar(
                df_top,
                x="user_popularity",
                y="recipe_name",
                orientation='h',
                title="🏆 Top 10 Recetas más Populares",
                color="user_popularity",
                color_continuous_scale="Teal", # Una paleta verde-azulada muy moderna
                labels={"user_popularity": "Popularidad", "recipe_name": "Nombre de la Receta"}
            )
            # Ordenar las barras para que la mayor quede arriba
            fig_barras.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_barras, use_container_width=True)

        with col2:
            # GRÁFICO 2: Gráfico circular tipo Donut (Distribución de Categorías)
            fig_donut = px.pie(
                df_filtrado,
                names="category",
                title="🍩 Distribución por Categorías",
                hole=0.45, # Esto lo convierte en un Donut Chart
                color_discrete_sequence=px.colors.qualitative.Set3 # Colores suaves pastel
            )
            # Mejoramos los detalles del texto del gráfico
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_donut, use_container_width=True)

        # GRÁFICO 3: Histograma (Distribución de Calorías) a todo lo ancho de la página
        fig_hist = px.histogram(
            df_filtrado,
            x="calories",
            title="🔥 ¿Cuántas calorías tienen nuestras recetas?",
            color="difficulty", # Apilar barras por dificultad
            nbins=12,
            barmode="stack",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={"calories": "Calorías (kcal)", "difficulty": "Dificultad"}
        )
        fig_hist.update_layout(bargap=0.1) # Damos un pequeño espacio entre las barras para que se vea más limpio
        st.plotly_chart(fig_hist, use_container_width=True)