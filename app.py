import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuración de la página
st.set_page_config(
    layout="wide", 
    page_title="Dashboard RNT Medellín - TalentoTech",
    page_icon="📊"
)

# 2. Función de carga y limpieza de datos
@st.cache_data
def load_data():
    # Intenta cargar desde la carpeta data o raíz
    if os.path.exists("data/rnt_med_def.csv"):
        path = "data/rnt_med_def.csv"
    else:
        path = "rnt_med_def.csv"
        
    df = pd.read_csv(path)
    
    # --- LIMPIEZA PARA ASEGURAR INTEGRIDAD DE CONTEOS ---
    # Convertir nulos en total_omisos a 0 para que no se filtren con el slider
    df['total_omisos'] = df['total_omisos'].fillna(0)
    
    # Manejo de nulos en categorías
    df['categoria_actividad_RNT'] = df['categoria_actividad_RNT'].fillna("SIN CATEGORÍA")
    df['categoria_actividad_RNT_inscritos'] = df['categoria_actividad_RNT_inscritos'].fillna("NO INSCRITO")
    df['rnt_segmento'] = df['rnt_segmento'].astype(str).fillna("No definido")
    
    # Columnas de cumplimiento (ICA y Omisos)
    cols_cumplimiento = [
        'ica_2021', 'ica_2022', 'ica_2023', 'ica_2024', 
        'omiso_2022', 'omiso_2023', 'omiso_2024'
    ]
    for col in cols_cumplimiento:
        df[col] = df[col].fillna("SIN REGISTRO")
        
    return df

df = load_data()

# 3. Sidebar: Filtros
st.sidebar.header("🎯 Filtros de Análisis")

# Estado Cámara de Comercio
f_cc = st.sidebar.multiselect(
    "Estado Cámara de Comercio",
    options=sorted(df['cc_act/inact'].unique()),
    default=df['cc_act/inact'].unique()
)

# Segmento RNT
f_segmento = st.sidebar.multiselect(
    "Segmento RNT",
    options=sorted(df['rnt_segmento'].unique()),
    default=df['rnt_segmento'].unique()
)

# Categoría Actividad RNT (General)
f_cat_rnt = st.sidebar.multiselect(
    "Categoría Actividad RNT",
    options=sorted(df['categoria_actividad_RNT'].unique()),
    default=df['categoria_actividad_RNT'].unique()
)

# Categoría Actividad RNT (Inscritos)
f_cat_inscritos = st.sidebar.multiselect(
    "Categoría Actividad (Inscritos)",
    options=sorted(df['categoria_actividad_RNT_inscritos'].unique()),
    default=df['categoria_actividad_RNT_inscritos'].unique()
)

# Rango de Omisos
max_omisos = int(df['total_omisos'].max())
f_omisos = st.sidebar.slider("Rango de Omisos Acumulados", 0, max_omisos, (0, max_omisos))

# --- Aplicar Filtros ---
df_filtered = df[
    (df['cc_act/inact'].isin(f_cc)) &
    (df['rnt_segmento'].isin(f_segmento)) &
    (df['categoria_actividad_RNT'].isin(f_cat_rnt)) &
    (df['categoria_actividad_RNT_inscritos'].isin(f_cat_inscritos)) &
    (df['total_omisos'].between(f_omisos[0], f_omisos[1]))
]

# 4. Dashboard Principal
st.title("📊 Análisis de Formalización y Cumplimiento RNT")
st.markdown(f"Visualizando **{df_filtered.shape[0]:,}** registros de un total de **{df.shape[0]:,}**")

# --- FILA 1: Tarjetas Resumen (KPIs) ---
st.subheader("Resumen General")
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric("Contribuyentes Únicos", f"{df_filtered['nroid'].nunique():,}")
    
with kpi2:
    st.metric("Total RNT (Suma)", f"{int(df_filtered['total_rnt_x'].sum()):,}")

with kpi3:
    # Proporción de activos
    activos = df_filtered[df_filtered['cc_act/inact'] == 'activo'].shape[0]
    st.metric("Inscritos Activos en CC", f"{activos:,}")

st.divider()

# --- FILA 2: Activos por Vigencia y Gráfica de Proporción ---
col_stats, col_pie = st.columns([0.6, 0.4])

with col_stats:
    st.write("**✅ Cantidad de Activos por Vigencia (RNT)**")
    v_cols = ['rnt_2021', 'rnt_2022', 'rnt_2023', 'rnt_2024']
    v_metrics = st.columns(4)
    for i, v in enumerate(v_cols):
        cant = int(df_filtered[v].sum())
        v_metrics[i].metric(v.replace('rnt_', ''), f"{cant:,}")

    st.write("**📝 Cantidad de Declarantes ICA**")
    ica_años = ['ica_2021', 'ica_2022', 'ica_2023', 'ica_2024']
    ica_metrics = st.columns(4)
    for i, a in enumerate(ica_años):
        cant = df_filtered[df_filtered[a] == 'DECLARO_ICA'].shape[0]
        ica_metrics[i].metric(f"ICA {a[-4:]}", f"{cant:,}")

with col_pie:
    st.write("**⚖️ Proporción Cámara de Comercio**")
    cc_counts = df_filtered['cc_act/inact'].value_counts().reset_index()
    cc_counts.columns = ['Estado', 'Cantidad']
    
    fig_pie = px.pie(
        cc_counts, 
        values='Cantidad', 
        names='Estado',
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Safe,
        category_orders={"Estado": ["activo", "inactivo", "no_inscrito"]}
    )
    fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# --- FILA 3: Cumplimiento de Obligaciones (Omisos) ---
st.subheader("🚨 Análisis de Omisiones")
omiso_años = ['omiso_2022', 'omiso_2023', 'omiso_2024']

# Transformar datos para gráfica de barras comparativa
resumen_omiso = df_filtered[omiso_años].apply(pd.Series.value_counts).T
resumen_omiso.index = [idx.replace('omiso_', '') for idx in resumen_omiso.index]

st.bar_chart(resumen_omiso)

# --- FILA 4: Tabla de Datos ---
with st.expander("🔍 Ver detalle de datos filtrados"):
    st.dataframe(
        df_filtered[['nroid', 'rnt_nombre_establecimiento', 'cc_act/inact', 'rnt_segmento', 'total_omisos']], 
        use_container_width=True
    )
