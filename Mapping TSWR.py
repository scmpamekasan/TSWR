# app.py - Streamlit + PyDeck: Titik Koordinat + Batas Kecamatan Surabaya & Gresik
# requirements.txt: streamlit pandas pydeck requests

import streamlit as st
import pandas as pd
import pydeck as pdk
import requests
import json

st.title("Peta Titik Koordinat + Batas Kecamatan Surabaya & Gresik")

st.markdown("""
- Masukkan koordinat (lng, lat) di bawah (satu per baris).
- Layer batas kecamatan Surabaya & Gresik ditampilkan sebagai poligon transparan.
- Titik koordinat kecil (radius ~10-15 meter).
""")

# Input koordinat
raw_input = st.text_area(
    "Koordinat (lng, lat) – satu per baris",
    height=150,
    value="""112.7368, -7.2575
112.7680, -7.2650
112.7200, -7.2900
112.7500, -7.2500"""
)

# Parsing koordinat
points = []
for line in raw_input.strip().split("\n"):
    line = line.strip()
    if not line:
        continue
    try:
        parts = [float(x.strip()) for x in line.replace(";", ",").split(",") if x.strip()]
        if len(parts) >= 2:
            lng, lat = parts[0], parts[1]
            points.append({"lng": lng, "lat": lat})
    except:
        st.warning(f"Baris dilewati: {line}")

df_points = pd.DataFrame(points) if points else pd.DataFrame()

# --- Layer Batas Kecamatan (GeoJSON) ---
# Contoh URL GeoJSON publik (ganti jika perlu dengan yang lebih akurat)
# Surabaya kecamatan: https://raw.githubusercontent.com/Alf-Anas/batas-administrasi-indonesia/main/kecamatan/surabaya-kec.geojson (jika ada, atau filter)
# Alternatif: Gunakan BIG atau HDX-derived repo

SURABAYA_KEC_GEOJSON_URL = "https://raw.githubusercontent.com/eppofahmi/geojson-indonesia/master/kota/surabaya.geojson"  # contoh, adjust jika perlu filter kecamatan
GRESIK_KEC_GEOJSON_URL   = "https://raw.githubusercontent.com/Alf-Anas/batas-administrasi-indonesia/main/kecamatan/gresik-kec.geojson"  # adjust sesuai repo

@st.cache_data
def load_geojson(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Gagal load GeoJSON dari {url}: {e}")
        return None

surabaya_geo = load_geojson(SURABAYA_KEC_GEOJSON_URL)
gresik_geo   = load_geojson(GRESIK_KEC_GEOJSON_URL)

# Layer Poligon batas kecamatan (chloropleth sederhana, warna random berdasarkan nama)
def create_boundary_layer(geo_data, color_range=[200, 100, 50, 100], name="Batas"):
    if not geo_data:
        return None
    return pdk.Layer(
        "GeoJsonLayer",
        geo_data,
        opacity=0.4,
        stroked=True,
        filled=True,
        extruded=False,
        wireframe=True,
        get_fill_color=[100, 150, 200, 120],  # biru muda transparan, bisa custom
        get_line_color=[0, 0, 0],
        line_width_min_pixels=1,
        pickable=True,
        auto_highlight=True,
        tooltip={"text": "{NAMOBJ}"}  # asumsi property NAMOBJ = nama kecamatan
    )

layer_surabaya = create_boundary_layer(surabaya_geo, name="Kecamatan Surabaya") if surabaya_geo else None
layer_gresik   = create_boundary_layer(gresik_geo,   name="Kecamatan Gresik", color_range=[150, 200, 100, 100]) if gresik_geo else None

# Layer Titik Koordinat (kecil)
if not df_points.empty:
    layer_points = pdk.Layer(
        "ScatterplotLayer",
        df_points,
        get_position=["lng", "lat"],
        get_radius=12,                 # kecil sekali
        radius_min_pixels=4,
        radius_max_pixels=10,
        get_fill_color=[255, 140, 0, 220],  # oranye
        pickable=True
    )
else:
    layer_points = None

# Hitung view center (prioritas titik input, fallback Surabaya)
if not df_points.empty:
    center_lon = df_points["lng"].mean()
    center_lat = df_points["lat"].mean()
    zoom_level = 11
else:
    center_lon, center_lat = 112.75, -7.25  # pusat Surabaya-Gresik
    zoom_level = 10

view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=zoom_level,
    pitch=0
)

# Deck layers
layers = [l for l in [layer_surabaya, layer_gresik, layer_points] if l is not None]

if layers:
    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v10",  # atau streets-v12 jika punya token
        initial_view_state=view_state,
        layers=layers,
        tooltip={
            "html": "<b>{NAMOBJ}</b><br>Kecamatan" if "NAMOBJ" in str else "<b>Titik:</b> {lng:.6f}, {lat:.6f}",
            "style": {"backgroundColor": "white", "color": "black"}
        }
    )

    st.pydeck_chart(deck, use_container_width=True, height=700)
else:
    st.info("Tidak ada layer yang bisa ditampilkan. Cek koneksi GeoJSON.")

# Tampilkan data titik
if not df_points.empty:
    st.subheader("Daftar Titik Koordinat")
    st.dataframe(df_points.style.format({"lng": "{:.6f}", "lat": "{:.6f}"}))

st.markdown("""
**Catatan Penting:**
- GeoJSON di atas adalah contoh. Untuk akurasi tinggi, download dari:
  - https://github.com/Alf-Anas/batas-administrasi-indonesia (filter kecamatan Jatim)
  - https://tanahair.indonesia.go.id (BIG resmi, download SHP → convert ke GeoJSON via QGIS/online tool)
  - https://data.humdata.org/dataset/cod-ab-idn (HDX Indonesia boundaries)
- Jika ingin filter hanya kecamatan Surabaya/Gresik: Load full Jatim, lalu filter properties['KABKOT'] == 'KOTA SURABAYA' atau 'KABUPATEN GRESIK'.
- Tambah Mapbox token di `map_style` jika ingin style premium.
""")
