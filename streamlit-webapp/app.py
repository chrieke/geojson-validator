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

_, cl1, cl2, cl3, _ = st.columns(5)
button_schema = cl1.button("Validate Schema")
button_geometries = cl2.button("Validate Geometries")
button_fix = cl3.button("Fix Geometries")

if button_schema:
    if not json_string:
        st.error("Please input GeoJSON or URL")
        st.stop()
    json_json = dict(json.loads(json_string.replace("'", '"')))
    errors = geojson_validator.validate_schema(json_json)
    if not errors:
        st.success("Input is valid according to GeoJSON specification.")
    if errors:
        st.error(
            f"Input is invalid according to GeoJSON specification. Reasons: {errors}"
        )

if button_geometries:
    if not json_string:
        st.error("Please input GeoJSON or URL")
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
    if not json_string:
        st.error("Please input GeoJSON or URL")
        st.stop()
    json_json = dict(json.loads(json_string.replace("'", '"')))
    fixed_fc = geojson_validator.fix_geometries(json_json)
    st.success("Fixed geoemtries")
    st.write(fixed_fc)
