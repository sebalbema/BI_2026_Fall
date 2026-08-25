import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from statsbombpy import sb
from mplsoccer import Pitch


# --------------------------------------------------
# CONFIGURACIÓN DE LA APP
# --------------------------------------------------

st.set_page_config(
    page_title="Visualización de pases",
    layout="wide"
)

st.title("⚽ Visualización interactiva de pases")
st.write("Mundial de Qatar 2022 - StatsBomb Open Data")


# --------------------------------------------------
# CARGAR TODOS LOS PARTIDOS DEL MUNDIAL
# --------------------------------------------------

@st.cache_data
def cargar_partidos():
    partidos = sb.matches(
        competition_id=43,
        season_id=106
    )

    return partidos


wc_2022 = cargar_partidos()


# --------------------------------------------------
# CREAR NOMBRE PARA CADA PARTIDO
# --------------------------------------------------

wc_2022["partido"] = (
    wc_2022["home_team"]
    + " vs "
    + wc_2022["away_team"]
)


# --------------------------------------------------
# SELECCIONAR PARTIDO
# --------------------------------------------------

partido_seleccionado = st.selectbox(
    "Selecciona un partido:",
    wc_2022["partido"].tolist()
)


# Buscar la fila del partido seleccionado
partido = wc_2022[
    wc_2022["partido"] == partido_seleccionado
].iloc[0]


# Obtener automáticamente el match_id
match_id = partido["match_id"]


st.write(
    f"**Partido seleccionado:** "
    f"{partido['home_team']} vs {partido['away_team']}"
)

st.write(
    f"**Match ID:** {match_id}"
)


# --------------------------------------------------
# CARGAR EVENTOS DEL PARTIDO SELECCIONADO
# --------------------------------------------------

@st.cache_data
def cargar_eventos(match_id):
    events = sb.events(
        match_id=match_id
    )

    return events


events = cargar_eventos(match_id)


# --------------------------------------------------
# VARIABLES QUE NOS INTERESAN
# --------------------------------------------------

variables = [
    'location',
    'minute',
    'period',
    'player',
    'second',
    'team',
    'type',
    'pass_end_location',
    'pass_recipient'
]


passes = events[variables].copy()


# --------------------------------------------------
# FILTRAR SOLAMENTE PASES
# --------------------------------------------------

final = passes[
    passes['type'] == 'Pass'
].copy()


final.reset_index(
    drop=True,
    inplace=True
)


# --------------------------------------------------
# ELIMINAR PASES SIN COORDENADAS
# --------------------------------------------------

final = final.dropna(
    subset=[
        'location',
        'pass_end_location'
    ]
)


# --------------------------------------------------
# EXTRAER COORDENADAS
# --------------------------------------------------

final['x0'] = final['location'].apply(
    lambda x: x[0]
)

final['x1'] = final['location'].apply(
    lambda x: x[1]
)

final['y0'] = final['pass_end_location'].apply(
    lambda x: x[0]
)

final['y1'] = final['pass_end_location'].apply(
    lambda x: x[1]
)


# --------------------------------------------------
# ELEGIR EQUIPO
# --------------------------------------------------

equipos = [
    partido["home_team"],
    partido["away_team"]
]


equipo_seleccionado = st.selectbox(
    "Selecciona un equipo:",
    equipos
)


# --------------------------------------------------
# FILTRAR POR EQUIPO
# --------------------------------------------------

final_equipo = final[
    final["team"] == equipo_seleccionado
]


# --------------------------------------------------
# SLIDER DE MINUTO
# --------------------------------------------------

minuto_maximo = int(final["minute"].max())


minuto = st.slider(
    "Selecciona el minuto:",
    min_value=0,
    max_value=minuto_maximo,
    value=0,
    step=1
)


# --------------------------------------------------
# FILTRAR POR MINUTO
# --------------------------------------------------

datos_minuto = final_equipo[
    final_equipo["minute"] == minuto
]


st.write(
    f"### {equipo_seleccionado}"
)

st.write(
    f"Pases realizados en el minuto {minuto}: "
    f"{len(datos_minuto)}"
)


# --------------------------------------------------
# CREAR CANCHA
# --------------------------------------------------

pitch = Pitch(
    pitch_type='statsbomb',
    pitch_color='grass',
    line_color='white',
    stripe=True
)


fig, ax = pitch.draw(
    figsize=(12, 8)
)


# --------------------------------------------------
# GRAFICAR PASES
# --------------------------------------------------

for _, pase in datos_minuto.iterrows():

    pitch.arrows(
        pase['x0'],
        pase['x1'],
        pase['y0'],
        pase['y1'],
        ax=ax,
        width=2,
        headwidth=5,
        headlength=5
    )


# Punto inicial del pase
pitch.scatter(
    datos_minuto['x0'],
    datos_minuto['x1'],
    ax=ax,
    s=60
)


# --------------------------------------------------
# TÍTULO
# --------------------------------------------------

ax.set_title(
    f"{equipo_seleccionado} - Minuto {minuto}",
    fontsize=16
)


# --------------------------------------------------
# MOSTRAR CANCHA EN STREAMLIT
# --------------------------------------------------

st.pyplot(fig)


# --------------------------------------------------
# TABLA DE PASES
# --------------------------------------------------

with st.expander("Ver información de los pases"):

    st.dataframe(
        datos_minuto[
            [
                'minute',
                'second',
                'player',
                'team',
                'pass_recipient'
            ]
        ]
    )
