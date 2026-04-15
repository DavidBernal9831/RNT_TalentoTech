import streamlit as st
import pandas as pd
import os

# Configuración de página
st.set_page_config(layout="wide", page_title="Dashboard RNT")

# Función para cargar datos
@st.cache_data
def load_data():
    # Buscamos el archivo en la carpeta data
    path = os.path.join("./rnt_med_def.csv")
    df = pd.read_csv(path)
    return df

df = load_data()

# --- FILTROS EN SIDEBAR ---
st.sidebar.header("Filtros")
f_cc = st.sidebar.multiselect("Estado Cámara Comercio", options=df['cc_act/inact'].unique(), default=df['cc_act/inact'].unique())
f_segmento = st.sidebar.multiselect("Segmento RNT", options=df['rnt_segmento'].unique(), default=df['rnt_segmento'].unique())
f_cat_rnt = st.sidebar.multiselect("Categoría Actividad RNT", options=df['categoria_actividad_RNT'].dropna().unique())
f_cat_insc = st.sidebar.multiselect("Categoría Inscritos", options=df['categoria_actividad_RNT_inscritos'].dropna().unique())
f_omisos = st.sidebar.slider("Rango de Omisos", 0, int(df['total_omisos'].max()), (0, int(df['total_omisos'].max())))

# Aplicación de filtros
df_filtered = df[
    (df['cc_act/inact'].isin(f_cc)) &
    (df['rnt_segmento'].isin(f_segmento)) &
    (df['total_omisos'].between(f_omisos[0], f_omisos[1]))
]

if f_cat_rnt:
    df_filtered = df_filtered[df_filtered['categoria_actividad_RNT'].isin(f_cat_rnt)]
if f_cat_insc:
    df_filtered = df_filtered[df_filtered['categoria_actividad_RNT_inscritos'].isin(f_cat_insc)]

# --- DASHBOARD ---
st.title("📊 RNT - Medellín")

# Tarjetas Principales
c1, c2, c3 = st.columns(3)
c1.metric("Contribuyentes Únicos", f"{df_filtered['nroid'].nunique():,}")
c2.metric("Suma Total RNT", f"{int(df_filtered['total_rnt_x'].sum()):,}")
with c3:
    st.write("**Inscritos (CC)**")
    st.write(df_filtered['cc_act/inact'].value_counts(dropna=False))

st.divider()

# Activos por Vigencia
st.subheader("✅ Activos por Vigencia")
vigencias = ['rnt_2021', 'rnt_2022', 'rnt_2023', 'rnt_2024']
cols_v = st.columns(4)
for i, v in enumerate(vigencias):
    cols_v[i].metric(v.replace('rnt_', ''), f"{int(df_filtered[v].sum())}")

st.divider()

# Declarantes ICA y Omisos
col_ica, col_om = st.columns(2)

with col_ica:
    st.subheader("📑 Declarantes ICA")
    ica_años = ['ica_2021', 'ica_2022', 'ica_2023', 'ica_2024']
    for a in ica_años:
        cant = df_filtered[df_filtered[a] == 'DECLARO_ICA'].shape[0]
        st.write(f"**{a[-4:]}:** {cant} declarantes")

with col_om:
    st.subheader("🚨 Resumen Omisos")
    om_años = ['omiso_2022', 'omiso_2023', 'omiso_2024']
    resumen_omiso = df_filtered[om_años].apply(pd.Series.value_counts).T
    st.bar_chart(resumen_omiso)
