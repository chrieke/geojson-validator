import json

import streamlit as st

import geojson_validator

st.set_page_config(
    page_title="geojson-validator",
    layout="wide",
    page_icon="🟥",
    initial_sidebar_state="collapsed",
)

col1, _, col2 = st.columns([1, 0.1, 1])
col1.image("repo-images/header_img.jpeg")

with col1.expander(
    "**Validate GeoJSON and automatically fix invalid geometries**. Like *geojsonhint*, "
    "but with geometry checks & fixes!",
    expanded=True,
):
    st.markdown("- Checks 🧬 **structure** according to GeoJSON specification")
    st.markdown(
        "- 🔴 **Detects invalid geometries** & 🟢 **fixes them** : *Duplicate nodes, winding order etc.*"
    )
    st.markdown(
        "- 🟨 **Problematic** geometries (for tools & APIs): *Self-intersection, anti-meridian etc.*"
    )
    st.markdown(
        "⭐ [**Github/chrieke/geojson-validator**](https://github.com/chrieke/geojson-validator)"
    )

col1.write("")

text_instruction = "Paste GeoJSON - FeatureCollection, Feature or Geometry"
placeholder_text = col1.empty()
json_string = placeholder_text.text_area(text_instruction, height=250)

col1.write("")

cl_ex, cl1, cl2, cl3, _ = col1.columns(5)
button_structure = cl1.button("Validate Structure")
button_geometries = cl2.button("Validate Geometries")
button_fix = cl3.button("Fix Geometries")

button_example = cl_ex.button("Example")
if button_example:
    example = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [13.376753, 52.515641],
                            [13.37696, 52.515011],
                            [13.378033, 52.514998],
                            [13.378049, 52.516176],
                        ]
                    ],
                },
            }
        ],
    }
    json_string = placeholder_text.text_area(
        text_instruction, value=example, height=250
    )
    button_geometries = True

if button_structure:
    if not json_string:
        col2.error("Please input GeoJSON or URL")
        st.stop()
    json_json = dict(json.loads(json_string.replace("'", '"')))
    errors = geojson_validator.validate_structure(json_json)
    if not errors:
        col2.success("Valid GeoJSON (structure)")
    if errors:
        col2.error("Invalid GeoJSON (structure)")
        col2.write(errors)

if button_geometries:
    if not json_string:
        col2.error("Please input GeoJSON or URL")
        st.stop()
    json_json = dict(json.loads(json_string.replace("'", '"')))
    results = geojson_validator.validate_geometries(json_json)
    if results["invalid"]:
        col2.error("Invalid GeoJSON (geometries)")
    elif results["problematic"]:
        col2.warning("Problematic GeoJSON (geometries)")
    else:
        col2.success("Valid GeoJSON (geometries)")
    col2.write(results)

if button_fix:
    if not json_string:
        col2.error("Please input GeoJSON or URL")
        st.stop()
    json_json = dict(json.loads(json_string.replace("'", '"')))
    fixed_fc = geojson_validator.fix_geometries(json_json)
    col2.success("Fixed geoemtries")
    col2.write(fixed_fc)
