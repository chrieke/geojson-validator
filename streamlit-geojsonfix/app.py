import json
import requests

import streamlit as st
from streamlit_lottie import st_lottie

import geojsonfix

st.set_page_config(
    page_title="geojsonfix",
    layout="centered",
    page_icon="🔻",
    initial_sidebar_state="collapsed",
)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


col1_header, col2_header = st.columns([1, 6])
lottie_url = "https://assets10.lottiefiles.com/temp/lf20_YQB3X3.json"
lottie_json = load_lottieurl(lottie_url)
with col1_header:
    st_lottie(lottie_json, height=100, speed=1)

col2_header.write("")
col2_header.title(f"GeoJSONfix")
st.write("")
st.markdown(
    "**Validates and automatically fixes your geospatial vector data.**",
    unsafe_allow_html=True,
)

text_instruction = "Paste GeoJSON - FeatureCollection, Feature or Geometry"
text_help = f"E.g. from https://geojson.io/"
json_string = st.text_area(text_instruction, height=250, help=text_help)

st.write("")
st.write("")

button_run = st.button("Validate")

if button_run:
    if not json_string:
        st.error("Input GeoJSON")
        st.stop()
    json_json = json.loads(json_string.replace("'", '"'))
    results = geojsonfix.validate(dict(json_json))
    if results["invalid"]:
        st.error("Invalid GeoJSON")
    elif results["problematic"]:
        st.warning("Problematic GeoJSON")
    else:
        st.success("Valid GeoJSON")
    st.write(
        "Results (shows the positional index of the invalid/problematic geometries)"
    )
    st.write(results)
