# app.py - Streamlit App untuk Menampilkan Multiple Titik Koordinat di Mapbox
# Dengan ukuran titik diperkecil (radius 15 meter)
# Jalankan dengan: streamlit run app.py
# Upload ke GitHub: Buat repo, tambah app.py + requirements.txt

import streamlit as st
import pandas as pd
# app.py
import pydeck as pdk
import requests

st.title("Peta Titik Koordinat + Batas Wilayah Kota Surabaya")

# ... (bagian input koordinat sama seperti sebelumnya) ...

# Load GeoJSON Surabaya real
@st.cache_data
def load_surabaya_geojson():
    url = "https://raw.githubusercontent.com/okzapradhana/indonesia-city-geojson/master/kota/kota_surabaya.geojson"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except:
        st.warning("Gagal load GeoJSON Surabaya. Gunakan bounding box sederhana.")
        return {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {"name": "Kota Surabaya (fallback)"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [112.5915, -7.3514], [112.8251, -7.3514],
                        [112.8251, -7.1924], [112.5915, -7.1924],
                        [112.5915, -7.3514]
                    ]]
                }
            }]
        }

geojson_surabaya = load_surabaya_geojson()

# Layer poligon Surabaya
surabaya_layer = pdk.Layer(
    'PolygonLayer',
    geojson_surabaya['features'],
    get_polygon='geometry.coordinates',
    get_fill_color=[100, 150, 255, 80],  # biru muda semi-transparan
    get_line_color=[0, 80, 200],
    line_width_min_pixels=2,
    pickable=True
)

# ... (layer titik koordinat sama seperti sebelumnya) ...

# Deck dengan layers
deck = pdk.Deck(
    map_style='mapbox://styles/mapbox/streets-v12',
    initial_view_state=view_state,
    layers=[point_layer, surabaya_layer],  # tambah gresik jika perlu
    tooltip=tooltip
)

st.pydeck_chart(deck, use_container_width=True, height=650)

# ... (sisanya tampilkan dataframe dll) ...


st.title("Peta Titik Koordinat di Mapbox via Streamlit")

st.markdown("""
Masukkan daftar koordinat (longitude, latitude) di bawah ini.  
Format: satu baris per titik, dipisah koma atau spasi.  
Contoh:  
112.7368, -7.2575  
112.7680, -7.2650  
""")

# Input teks multi-line
raw_input = st.text_area(
    "Masukkan koordinat (lng, lat)", 
    height=150, 
    value="""112.7368, -7.2575
112.7680, -7.2650
112.7200, -7.2900
112.7500, -7.2500"""
)

# Parsing input menjadi list of [lon, lat]
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

    st.subheader("Peta Titik Koordinat (Ukuran Titik Diperkecil)")

    # Ukuran titik kecil: 15 meter (bisa dicoba 10 atau 20 jika masih kurang/kelihatan)
    # Warna bisa diganti juga, misal "#FF4500" untuk oranye
    st.map(
        df,
        latitude="lat",
        longitude="lon",
        size=15,                # ← Ukuran radius dalam meter (kecil: 10–20)
        zoom=11,                # Zoom lebih dekat agar titik kecil tetap kelihatan
        color="#FF5733",        # Warna oranye (opsional)
        use_container_width=True,
        height=600
    )

    st.subheader("Data Koordinat")
    st.dataframe(df)

    # Opsional: tampilkan juga dalam format GeoJSON sederhana
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row.lon, row.lat]},
                "properties": {"id": i+1}
            }
            for i, row in df.iterrows()
        ]
    }
    st.json(geojson)
else:
    st.info("Belum ada koordinat yang valid. Masukkan di atas.")
