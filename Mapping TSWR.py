# app.py (versi advanced)
import streamlit as st
import pandas as pd
import pydeck as pdk

st.title("Peta Multiple Titik Koordinat – Mapbox + PyDeck")

# Masukkan Mapbox token (penting untuk style bagus)
MAPBOX_TOKEN = st.text_input(
    "Mapbox Access Token (opsional, tapi direkomendasikan)",
    value="pk.eyJ1Ijoi...ganti_dengan_token_kamu...",
    type="password"
)

# Input koordinat sama seperti versi 1
raw_input = st.text_area(
    "Koordinat (lng, lat) – satu per baris",
    height=180,
    value="""112.7368, -7.2575, Titik A
112.7680, -7.2650, Titik B
112.7200, -7.2900, Titik C
112.7500, -7.2500, Titik D"""
)

points = []
for i, line in enumerate(raw_input.strip().split("\n")):
    line = line.strip()
    if not line: continue
    try:
        parts = [x.strip() for x in line.replace(";", ",").split(",")]
        lng = float(parts[0])
        lat = float(parts[1])
        name = parts[2] if len(parts) > 2 else f"Titik {i+1}"
        points.append({"lng": lng, "lat": lat, "name": name})
    except:
        pass

if points:
    df = pd.DataFrame(points)

    # Layer titik (Scatterplot)
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lng", "lat"],
        get_color=[255, 140, 0, 180],  # oranye semi-transparan
        get_radius=120,               # ukuran titik (meter)
        pickable=True,
    )

    # Tooltip
    tooltip = {
        "html": "<b>{name}</b><br>Lng: {lng}<br>Lat: {lat}",
        "style": {"background": "grey", "color": "white", "font-family": "Arial"}
    }

    # View awal (bisa dihitung otomatis dari data)
    if not df.empty:
        center_lon = df["lng"].mean()
        center_lat = df["lat"].mean()
    else:
        center_lon, center_lat = 112.75, -7.25

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=10,
        pitch=0
    )

    # Deck dengan Mapbox
    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/streets-v12" if MAPBOX_TOKEN else None,
        api_keys={"mapbox": MAPBOX_TOKEN} if MAPBOX_TOKEN else None,
        initial_view_state=view_state,
        layers=[layer],
        tooltip=tooltip
    )

    st.pydeck_chart(deck, use_container_width=True, height=650)

    st.dataframe(df[["name", "lng", "lat"]])
else:
    st.info("Masukkan koordinat di atas (contoh: 112.75, -7.25, Nama Titik)")
