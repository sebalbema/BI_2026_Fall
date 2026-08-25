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

st.title("Visualización interactiva de pases")

st.write(
    "Aplicación para visualizar los pases de un partido "
    "del Mundial de Qatar 2022 utilizando datos de StatsBomb."
)


# --------------------------------------------------
# CARGAR DATOS
# --------------------------------------------------

@st.cache_data
def cargar_eventos():

    events = sb.events(match_id=3857255)

    return events


events = cargar_eventos()


# --------------------------------------------------
# SELECCIONAR VARIABLES
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
# CONTROLES DE STREAMLIT
# --------------------------------------------------

minuto = st.slider(
    "Selecciona el minuto",
    min_value=0,
    max_value=90,
    value=0,
    step=1
)


# --------------------------------------------------
# DATOS DEL MINUTO SELECCIONADO
# --------------------------------------------------

datos_minuto = final[
    final['minute'] == minuto
]


st.write(
    f"Pases realizados en el minuto {minuto}: "
    f"{len(datos_minuto)}"
)


# --------------------------------------------------
# CREAR CANCHA
# --------------------------------------------------

pitch = Pitch(
    pitch_color='grass',
    line_color='white',
    stripe=True
)

fig, ax = pitch.draw(
    figsize=(10, 7)
)


# --------------------------------------------------
# GRAFICAR PASES
# --------------------------------------------------

sns.scatterplot(
    data=datos_minuto,
    x='x0',
    y='x1',
    ax=ax,
    hue='team',
    s=80
)


# Dibujar dirección de cada pase
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


ax.set_title(
    f"Pases en el minuto {minuto}"
)

st.pyplot(fig)


# --------------------------------------------------
# MOSTRAR TABLA
# --------------------------------------------------

with st.expander("Ver datos de los pases"):

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
