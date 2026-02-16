# app.py
import streamlit as st
import pandas as pd
import pydeck as pdk

st.title("Peta Titik Koordinat di Mapbox via Streamlit")

st.markdown("""
Masukkan daftar koordinat (longitude, latitude) di bawah ini.  
Format: satu baris per titik, dipisah koma atau spasi.  
Contoh:  
112.7368, -7.2575  
112.7680, -7.2650  
""")

# Input teks multi-line
raw_input = st.text_area("Masukkan koordinat (lng, lat)", height=150, value="""112.7368, -7.2575
112.7680, -7.2650
112.7200, -7.2900
112.7500, -7.2500""")

# Parsing input menjadi list of [lng, lat]
points = []
for line in raw_input.strip().split("\n"):
    line = line.strip()
    if not line:
        continue
    try:
        parts = [float(x.strip()) for x in line.replace(";", ",").split(",") if x.strip()]
        if len(parts) >= 2:
            lng, lat = parts[0], parts[1]
            points.append({"lon": lng, "lat": lat})
    except:
        st.warning(f"Baris salah format → dilewati: {line}")

if points:
    df = pd.DataFrame(points)

    layer = pdk.Layer(
        'ScatterplotLayer',
        df,
        get_position=['lon', 'lat'],
        get_radius=10,             # radius dalam meter (sangat kecil)
        radius_min_pixels=3,       # minimal 3 pixel (agar tetap kelihatan zoom out)
        radius_max_pixels=8,       # maksimal 8 pixel (agar tidak besar saat zoom in)
        get_fill_color=[255, 140, 0, 200],  # oranye semi-transparan
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=df['lat'].mean(),
        longitude=df['lon'].mean(),
        zoom=11,
        pitch=0
    )

    deck = pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v12',
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "Lon: {lon}, Lat: {lat}"}
    )

    st.pydeck_chart(deck, use_container_width=True, height=600)    
    
    
