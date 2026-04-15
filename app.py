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
    # Intenta cargar el archivo desde la raíz o carpeta data
    path = "rnt_med_def.csv" if os.path.exists("rnt_med_def.csv") else "data/rnt_med_def.csv"
    
    df = pd.read_csv(path)
    
    # --- PROCESAMIENTO DE COLUMNAS SEGÚN TU NUEVO DF ---
    # Llenar nulos en total_omisos para que el slider no excluya registros
    df['total_omisos'] = df['total_omisos'].fillna(0)
    
    # Manejo de nulos en la nueva columna categoria_final
    if 'categoria_final' in df.columns:
        df['categoria_final'] = df['categoria_final'].fillna("REVISAR")
    else:
        st.error("La columna 'categoria_final' no se encontró en el archivo.")
        st.stop()
        
    # Limpieza de segmento y estados
    df['rnt_segmento'] = df['rnt_segmento'].astype(str).replace('nan', 'No definido')
    df['cc_act/inact'] = df['cc_act/inact'].fillna("no_inscrito")
    
    # Columnas de cumplimiento (ICA y Omisos)
    cols_cumplimiento = [
        'ica_2021', 'ica_2022', 'ica_2023', 'ica_2024', 
        'omiso_2022', 'omiso_2023', 'omiso_2024'
    ]
    for col in cols_cumplimiento:
        if col in df.columns:
            df[col] = df[col].fillna("SIN REGISTRO")
        
    return df

df = load_data()

# 3. Sidebar: Filtros
st.sidebar.header("🎯 Filtros de Análisis")

# Filtro 1: Cámara de Comercio
f_cc = st.sidebar.multiselect(
    "Estado Cámara de Comercio",
    options=sorted(df['cc_act/inact'].unique()),
    default=df['cc_act/inact'].unique()
)

# Filtro 2: Segmento RNT
f_segmento = st.sidebar.multiselect(
    "Segmento RNT",
    options=sorted(df['rnt_segmento'].unique()),
    default=df['rnt_segmento'].unique()
)

# Filtro 3: Categoría Final (La que acabas de agregar)
f_cat_final = st.sidebar.multiselect(
    "Categoría RNT (Final)",
    options=sorted(df['categoria_final'].unique()),
    default=df['categoria_final'].unique()
)

# Filtro 4: Rango de Omisos
max_omisos = int(df['total_omisos'].max())
f_omisos = st.sidebar.slider("Rango de Omisos Acumulados", 0, max_omisos, (0, max_omisos))

# --- Aplicar Filtros ---
df_filtered = df[
    (df['cc_act/inact'].isin(f_cc)) &
    (df['rnt_segmento'].isin(f_segmento)) &
    (df['categoria_final'].isin(f_cat_final)) &
    (df['total_omisos'].between(f_omisos[0], f_omisos[1]))
]

# 4. Dashboard Principal
st.title("📊 Análisis RNT Medellín - Fiscalización")
st.markdown(f"Mostrando **{df_filtered.shape[0]:,}** registros de un total de **{df.shape[0]:,}**")

# --- FILA 1: Tarjetas Resumen (KPIs) ---
st.subheader("Resumen General")
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric("Contribuyentes Únicos", f"{df_filtered['nroid'].nunique():,}")
    
with kpi2:
    st.metric("Total RNT (Suma)", f"{int(df_filtered['total_rnt_x'].sum()):,}")

with kpi3:
    activos = df_filtered[df_filtered['cc_act/inact'] == 'activo'].shape[0]
    st.metric("Inscritos Activos en CC", f"{activos:,}")

st.divider()

# --- FILA 2: Vigencias y Proporción ---
col_stats, col_pie = st.columns([0.6, 0.4])

with col_stats:
    st.write("**✅ Prestadores Activos por Año (RNT)**")
    v_cols = ['rnt_2021', 'rnt_2022', 'rnt_2023', 'rnt_2024']
    v_metrics = st.columns(4)
    for i, v in enumerate(v_cols):
        cant = int(df_filtered[v].sum())
        v_metrics[i].metric(v.replace('rnt_', ''), f"{cant:,}")

    st.write("**📝 Declarantes ICA**")
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
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# --- FILA 3: Análisis de Omisiones ---
st.subheader("🚨 Cumplimiento de Obligaciones")
omiso_años = ['omiso_2022', 'omiso_2023', 'omiso_2024']

# Preparar datos para gráfica de barras
if not df_filtered.empty:
    resumen_omiso = df_filtered[omiso_años].apply(pd.Series.value_counts).T
    resumen_omiso.index = [idx.replace('omiso_', '') for idx in resumen_omiso.index]
    st.bar_chart(resumen_omiso)
else:
    st.warning("No hay datos para mostrar en la selección actual.")

# --- FILA 4: Tabla Detallada ---
with st.expander("🔍 Explorar Datos Filtrados"):
    # Mostramos las columnas principales que definiste
    cols_mostrar = [
        'nroid', 'rnt_nombre_establecimiento', 'rnt_categoria', 
        'categoria_final', 'cc_act/inact', 'rnt_segmento', 'total_omisos'
    ]
    st.dataframe(df_filtered[cols_mostrar], use_container_width=True)
