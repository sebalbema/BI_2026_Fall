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

st.write(
    "Selecciona un Mundial, un partido y un minuto "
    "para visualizar los pases de ambos equipos."
)


# --------------------------------------------------
# CARGAR COMPETICIONES
# --------------------------------------------------

@st.cache_data
def cargar_competiciones():
    return sb.competitions()


competitions = cargar_competiciones()


# --------------------------------------------------
# FILTRAR FIFA WORLD CUP
# --------------------------------------------------

world_cups = competitions[
    competitions["competition_name"] == "FIFA World Cup"
].copy()


# --------------------------------------------------
# CREAR NOMBRE DEL MUNDIAL
# --------------------------------------------------

world_cups["mundial"] = (
    world_cups["season_name"].astype(str)
)


# --------------------------------------------------
# SELECCIONAR MUNDIAL
# --------------------------------------------------

mundial_seleccionado = st.selectbox(
    "Selecciona un Mundial:",
    world_cups["mundial"].unique()
)


# Obtener datos del Mundial elegido
mundial = world_cups[
    world_cups["mundial"] == mundial_seleccionado
].iloc[0]


competition_id = mundial["competition_id"]
season_id = mundial["season_id"]


# --------------------------------------------------
# CARGAR PARTIDOS DEL MUNDIAL
# --------------------------------------------------

@st.cache_data
def cargar_partidos(competition_id, season_id):

    return sb.matches(
        competition_id=competition_id,
        season_id=season_id
    )


partidos = cargar_partidos(
    competition_id,
    season_id
)


# --------------------------------------------------
# CREAR NOMBRE DEL PARTIDO
# --------------------------------------------------

partidos["partido"] = (
    partidos["home_team"]
    + " vs "
    + partidos["away_team"]
)


# --------------------------------------------------
# SELECCIONAR PARTIDO
# --------------------------------------------------

partido_seleccionado = st.selectbox(
    "Selecciona un partido:",
    partidos["partido"].tolist()
)


# Obtener información del partido
partido = partidos[
    partidos["partido"] == partido_seleccionado
].iloc[0]


match_id = partido["match_id"]


st.write(
    f"**Partido seleccionado:** "
    f"{partido['home_team']} vs {partido['away_team']}"
)


# --------------------------------------------------
# CARGAR EVENTOS
# --------------------------------------------------

@st.cache_data
def cargar_eventos(match_id):

    return sb.events(
        match_id=match_id
    )


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
# SLIDER DE MINUTO
# --------------------------------------------------

minuto_maximo = int(
    final["minute"].max()
)


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

datos_minuto = final[
    final["minute"] == minuto
]


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
# GRAFICAR PUNTOS DE ORIGEN
# --------------------------------------------------

sns.scatterplot(
    data=datos_minuto,
    x='x0',
    y='x1',
    hue='team',
    ax=ax,
    s=80
)


# --------------------------------------------------
# GRAFICAR FLECHAS DE LOS PASES
# --------------------------------------------------

for _, pase in datos_minuto.iterrows():

    pitch.arrows(
        pase['x0'],
        pase['x1'],
        pase['y0'],
        pase['y1'],
        ax=ax,
        width=1.5,
        headwidth=4,
        headlength=4,
        alpha=0.7
    )


# --------------------------------------------------
# LEYENDA
# --------------------------------------------------

plt.legend(
    loc='upper center',
    ncols=2
)


# --------------------------------------------------
# TÍTULO
# --------------------------------------------------

ax.set_title(
    f"{partido['home_team']} vs {partido['away_team']} "
    f"- Minuto {minuto}",
    fontsize=16
)


# --------------------------------------------------
# MOSTRAR GRÁFICA
# --------------------------------------------------

st.pyplot(fig)


# --------------------------------------------------
# MOSTRAR TABLA
# --------------------------------------------------

with st.expander(
    "Ver información de los pases"
):

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
