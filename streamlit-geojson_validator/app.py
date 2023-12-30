import json

import streamlit as st

import geojson_validator

st.set_page_config(
    page_title="geojson-validator",
    layout="centered",
    page_icon="🟥",
    initial_sidebar_state="collapsed",
)

st.image("preview-images/header_img.jpeg")

st.markdown(
    "[![Star](https://img.shields.io/github/stars/chrieke/geojson-validator.svg?logo=github&style=social)]"
    "(https://github.com/chrieke/geojson-validator)"
)

st.write("")
st.markdown(
    "**Validates and automatically fixes invalid GeoJSON - 🌎 Webapp and 🐍 Python package.**",
    unsafe_allow_html=True,
)

text_instruction = "Paste GeoJSON - FeatureCollection, Feature or Geometry"
text_help = "E.g. from https://geojson.io/"
json_string = st.text_area(text_instruction, height=250, help=text_help)

st.write("")
st.write("")

_, cl1, cl2, _ = st.columns(4)
button_validate = cl1.button("Validate")
button_fix = cl2.button("Fix GeoJSON")

if button_validate:
    if not json_string:
        st.error("Input GeoJSON or URL")
        st.stop()
    json_json = dict(json.loads(json_string.replace("'", '"')))
    results = geojson_validator.validate_geometries(json_json)
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

if button_fix:
    st.write("Coming Soon!")
