
import pandas as pd
import  streamlit as st
import numpy as np
import seaborn as sb
import plotly as pl
import matplotlib as mp
import plotly.express as px

Ruta =  "RNT_Final.csv"
RNT= pd.read_csv(Ruta,sep=";",encoding='utf-8')#, on_bad_lines='skip')
RNT=RNT.dropna()

st.set_page_config(layout="centered",
                   page_title="OFERTA*DE*SERVICIOS*TURÍSTICOS*EN*COLOMBIA",
                   page_icon=":bar_chart:")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right,#a2e0b2, #EAF0F6);
    }
    </style>
    """,
    unsafe_allow_html=True
)

t1, t2 =st.columns([0.001,0.999])
t2.title("Oferta de Servicios Turísticos en Colombia 2019-2026")
t2.markdown( 'El Registro Nacional de Turismo (RNT) es un mecanismo obligatorio y gratuito de inscripción para todos los prestadores de servicios turísticos (hoteles, agencias, guías, etc.) que operan en el país. Sirve para formalizar la actividad, garantizar calidad, y es gestionado por las Cámaras de Comercio bajo el Ministerio de Comercio, Industria y Turismo. A través del uso de la información recopilada en el RNT es posible mostrar las empresas que prestan servicios turísticos en el sector, pudiendo el usuario hacer diferentes filtros de acuerdo a la información puntual que desea observar.' )
t2.image("imagen2.jpeg", width=350)

#Sidebar para filtros
st.sidebar.header("Filtros")

# 1. Widget de multiselect con nombres únicos
options = RNT["CATEGORIA"].unique().tolist()
options0 = RNT["SUB_CATEGORIA"].unique().tolist()
options1 = RNT["AÑO"].unique().tolist()
options2 = RNT["DEPARTAMENTO"].unique().tolist()
options3 = RNT["MUNICIPIO"].unique().tolist()

selected_names = st.sidebar.multiselect(
    "Selecciona CATEGORIA a graficar en el mapa:",
    options=options,
    default=[],# vacío por defecto
    max_selections=30,
    accept_new_options=True,
)
selected_names0 = st.sidebar.multiselect(
    "Selecciona SUB_CATEGORIA a graficar en el mapa:",
    options=options0,
    default=[]# vacío por defecto
)
selected_years = st.sidebar.multiselect(
    "Selecciona AÑO(S) a graficar en el mapa:",
    options=options1,
    default=[]  # vacío por defecto
)
selected_departamentos = st.sidebar.multiselect(
    "Selecciona DEPARTAMENTO(S) a graficar en el mapa:",
    options=options2,
    default=[]  # vacío por defecto
)
selected_municipios = st.sidebar.multiselect(
    "Selecciona MUNICIPIO(S) a graficar en el mapa:",
    options=options3,
    default=[]  # vacío por defecto
)

# 2. Filtrar el DataFrame según la selección
if not selected_names:
    df_filtered = RNT # mapa vacío si nada seleccionado
else:
    df_filtered = RNT[RNT["CATEGORIA"].isin(selected_names)].copy()

if not selected_names0:
    df_filtered0 = df_filtered
else:
    df_filtered0 = df_filtered[df_filtered["SUB_CATEGORIA"].isin(selected_names0)].copy()

if not selected_years:
    df_filtered1 = df_filtered0
else:
    df_filtered1 = df_filtered0[df_filtered0["AÑO"].isin(selected_years)].copy()

if not selected_departamentos:
    df_filtered2 = df_filtered1
else:
    df_filtered2 = df_filtered1[df_filtered1["DEPARTAMENTO"].isin(selected_departamentos)].copy()

if not selected_municipios:
    df_filtered3 = df_filtered2
else:
    df_filtered3 = df_filtered2[df_filtered2["MUNICIPIO"].isin(selected_municipios)].copy()
     
# 3. Mostrar el mapa en Streamlit
#st.write("Puntos seleccionados:")

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Total Registros Seleccionados")
st.metric(label="", value=df_filtered["CODIGO_RNT"].count())
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("# RNT Únicos")
st.metric(label="",value=df_filtered["CODIGO_RNT"].nunique())
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("# de Empresas")
st.metric(label="",value=df_filtered["NIT"].nunique())
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("# de Empleos Generados")
st.metric(label="",value=df_filtered["NUMERO_DE_EMPLEADOS"].sum())
st.markdown('</div>', unsafe_allow_html=True)

st.map(
    df_filtered3,latitude="Latitud",longitude="Longitud"
)

st.dataframe(df_filtered3[["RAZON_SOCIAL_ESTABLECIMIENTO","MUNICIPIO","AÑO","NUMERO_DE_EMPLEADOS"]])

df_yearly = df_filtered3.groupby(["AÑO"]).size().reset_index()

#st.table(df_yearly.columns)
df_yearly.rename(columns={0:'# de RNT'},inplace = True) 
fig = px.line(
    df_yearly,     
    x='AÑO', 
    y='# de RNT',
    title='Número de Registros de Turismo',
    labels={'': '', '': ''}
)

st.plotly_chart(fig)

df_yearlyNIT = df_filtered3.groupby("AÑO")["NIT"].nunique().reset_index()
df_yearly.columns = ["AÑO", "NITS_Únicos"]

#st.table(df_yearlyNIT.columns)
df_yearlyNIT.rename(columns={0:'# de NIT'},inplace = True) 
fig1 = px.line(
    df_yearlyNIT,     
    x='AÑO', 
    y='NIT',
    title='Número de Empresas Registradas',
    labels={'': '', '': ''}
)

st.plotly_chart(fig1)

df_cat = df_filtered3.groupby("CATEGORIA")["CODIGO_RNT"].count().reset_index()
df_cat.columns = ["CATEGORIA", "CODIGO_RNT"]

fig2 = px.pie(
    df_cat,
    names="CATEGORIA",
    values="CODIGO_RNT",
    title="Distribución por Categoría", 
)

#fig2.update_layout(margin=dict(t=0,b=0,l=0,r=0)
    #width=1000,
    #height=1000
#)

st.plotly_chart(fig2, use_container_width=True)

    
