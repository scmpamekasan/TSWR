import streamlit as st
import pandas as pd
import json
import pydeck as pdk
import os

st.title("Peta Titik Koordinat + Batas Wilayah Bangkalan Kota")

st.markdown("""
Masukkan daftar koordinat (longitude, latitude) satu per baris.  
Format: lng, lat (dipisah koma atau spasi)  
Contoh:  
112.7368, -7.2575
""")

raw_input = st.text_area(
    "Koordinat (lng, lat)",
    height=150,
    value="""112.7368, -7.2575
112.7680, -7.2650
112.7200, -7.2900
112.7500, -7.2500"""
)

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
    except Exception:
        st.warning(f"Baris salah format (dilewati): {line}")

if points:
    df = pd.DataFrame(points)

    # ────────────────────────────────────────────────
    # Load batas wilayah Bangkalan Kota dari GeoJSON
    # ────────────────────────────────────────────────
    geojson_path = os.path.join("Map", "Bangkalan_BangkalanKota.geojson")

    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            batas_geojson = json.load(f)

        st.success("Batas wilayah Bangkalan berhasil dimuat!")

        # Layer 1: Batas wilayah (polygon / MultiPolygon)
        boundary_layer = pdk.Layer(
            "GeoJsonLayer",
            data=batas_geojson,
            opacity=0.35,                     # transparan agar titik kelihatan
            stroked=True,
            filled=True,
            get_fill_color=[220, 53, 69, 120],  # merah muda semi-transparan
            get_line_color=[180, 0, 0],
            line_width_min_pixels=2,
            pickable=True
        )

        # Layer 2: Titik koordinat (radius 15 meter)
        points_layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=["lon", "lat"],
            get_radius=15,                    # dalam meter
            get_fill_color=[255, 87, 51, 220],  # oranye semi-transparan
            get_line_color=[0, 0, 0, 150],
            line_width_min_pixels=1,
            pickable=True
        )

        # View state (pusat Bangkalan)
        view_state = pdk.ViewState(
            latitude=-7.03,
            longitude=112.75,
            zoom=11,
            pitch=0
        )

        # Gabungkan layers
        deck = pdk.Deck(
            layers=[boundary_layer, points_layer],  # batas di bawah, titik di atas
            initial_view_state=view_state,
            tooltip={"text": "Titik ID: {id}"},     # opsional, bisa ditambah properties lain
            map_style=None                          # default Carto (tidak butuh token)
            # Jika ingin Mapbox style: map_style="mapbox://styles/mapbox/light-v10"
            # lalu tambah api_keys={"mapbox": st.secrets["MAPBOX_TOKEN"]}
        )

        st.subheader("Peta Titik + Batas Wilayah")
        st.pydeck_chart(deck, use_container_width=True, height=650)

        st.subheader("Data Koordinat")
        st.dataframe(df)

        # Opsional: tampilkan GeoJSON titik
        point_geojson = {
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
        with st.expander("GeoJSON Titik (untuk debug)"):
            st.json(point_geojson)

    except FileNotFoundError:
        st.error(
            f"File GeoJSON tidak ditemukan di: `{geojson_path}`\n\n"
            "Pastikan:\n"
            "• Folder 'Map' ada di root repo\n"
            "• File bernama persis 'Bangkalan_BangkalanKota.geojson'\n"
            "• Sudah commit + push ke GitHub\n"
            "• Deploy ulang app di Streamlit Cloud"
        )
    except json.JSONDecodeError:
        st.error("File GeoJSON rusak atau format tidak valid. Cek di geojson.io")
    except Exception as e:
        st.error(f"Error saat memproses peta: {str(e)}")

else:
    st.info("Masukkan setidaknya satu koordinat yang valid di atas.")
