import streamlit as st
import pandas as pd
import os

# Configuración de página
st.set_page_config(layout="wide", page_title="Dashboard RNT Medellín")

# Función para cargar y limpiar datos
@st.cache_data
def load_data():
    path = "rnt_med_def.csv" # Ajusta si está en /data/
    df = pd.read_csv(path)
    
    # --- LIMPIEZA CRÍTICA PARA CONTEOS REALES ---
    # 1. Llenar nulos en total_omisos con 0 para que no desaparezcan del filtro
    df['total_omisos'] = df['total_omisos'].fillna(0)
    
    # 2. Llenar nulos en categorías para que aparezcan como opción "Sin Información"
    df['categoria_actividad_RNT'] = df['categoria_actividad_RNT'].fillna("Sin Categoría")
    df['categoria_actividad_RNT_inscritos'] = df['categoria_actividad_RNT_inscritos'].fillna("No Inscrito")
    
    # 3. Asegurar que las columnas de ICA y Omisos tengan un valor legible si son nulas
    cols_check = ['ica_2021', 'ica_2022', 'ica_2023', 'ica_2024', 'omiso_2022', 'omiso_2023', 'omiso_2024']
    for col in cols_check:
        df[col] = df[col].fillna("SIN REGISTRO")
        
    return df

df = load_data()

# --- SIDEBAR: FILTROS ---
st.sidebar.header("Filtros de Control")

# 1. Filtro Cámara de Comercio (Por defecto todos)
f_cc = st.sidebar.multiselect(
    "Estado Cámara Comercio", 
    options=df['cc_act/inact'].unique(), 
    default=df['cc_act/inact'].unique()
)

# 2. Filtro Segmento
f_segmento = st.sidebar.multiselect(
    "Segmento RNT", 
    options=df['rnt_segmento'].unique(), 
    default=df['rnt_segmento'].unique()
)

# 3. Filtro Actividad RNT
f_cat_rnt = st.sidebar.multiselect(
    "Categoría Actividad RNT", 
    options=df['categoria_actividad_RNT'].unique(),
    default=df['categoria_actividad_RNT'].unique()
)

# 4. Filtro Omisos (Ahora incluye los que eran NaN como 0)
max_o = int(df['total_omisos'].max())
f_omisos = st.sidebar.slider("Rango de Omisos", 0, max_o, (0, max_o))

# --- APLICACIÓN DE FILTROS ---
df_filtered = df[
    (df['cc_act/inact'].isin(f_cc)) &
    (df['rnt_segmento'].isin(f_segmento)) &
    (df['categoria_actividad_RNT'].isin(f_cat_rnt)) &
    (df['total_omisos'].between(f_omisos[0], f_omisos[1]))
]

# --- CUERPO PRINCIPAL ---
st.title("📊 Análisis RNT Medellín")
st.markdown(f"Mostrando **{df_filtered.shape[0]}** registros de un total de **{df.shape[0]}**")

# FILA 1: TARJETAS RESUMEN
c1, c2, c3, c4 = st.columns(4)

with c1:
    total_unicos = df_filtered['nroid'].nunique()
    st.metric("Contribuyentes Únicos", f"{total_unicos:,}")

with c2:
    total_rnt = int(df_filtered['total_rnt_x'].sum())
    st.metric("Total RNT (Suma)", f"{total_rnt:,}")

with c3:
    # Mostramos los activos (cc_act/inact == 'activo')
    activos_cc = df_filtered[df_filtered['cc_act/inact'] == 'activo'].shape[0]
    st.metric("Inscritos Activos CC", f"{activos_cc:,}")

with c4:
    # Promedio de omisos en la selección
    prom_om = df_filtered['total_omisos'].mean()
    st.metric("Promedio Omisiones", f"{prom_om:.2f}")

st.divider()

# FILA 2: VIGENCIAS RNT (Columnas rnt_202X)
st.subheader("📅 Prestadores Activos por Año (RNT)")
v_cols = ['rnt_2021', 'rnt_2022', 'rnt_2023', 'rnt_2024']
cv = st.columns(4)
for i, v in enumerate(v_cols):
    cant = int(df_filtered[v].sum())
    cv[i].metric(f"Vigencia {v[-4:]}", f"{cant:,}")

st.divider()

# FILA 3: ICA Y CUMPLIMIENTO
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 Declarantes ICA")
    ica_años = ['ica_2021', 'ica_2022', 'ica_2023', 'ica_2024']
    # Creamos un pequeño resumen para graficar
    resumen_ica = []
    for a in ica_años:
        d = df_filtered[df_filtered[a] == 'DECLARO_ICA'].shape[0]
        resumen_ica.append({'Año': a[-4:], 'Declarantes': d})
    df_res_ica = pd.DataFrame(resumen_ica)
    st.bar_chart(df_res_ica.set_index('Año'))

with col_right:
    st.subheader("⚠️ Estado de Omisos (2024)")
    # Ver cómo están los omisos en el último año
    om_dist = df_filtered['omiso_2024'].value_counts()
    st.dataframe(om_dist)

# TABLA DETALLE
with st.expander("🔍 Explorar Datos Filtrados"):
    st.dataframe(df_filtered)
