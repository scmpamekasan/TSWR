# app.py - Streamlit App untuk Menampilkan Multiple Titik Koordinat di Mapbox
# Jalankan dengan: streamlit run app.py
# Upload ke GitHub: Buat repo, tambah app.py + requirements.txt, lalu deploy ke Streamlit Cloud jika mau

import streamlit as st
import streamlit.components.v1 as components

# Judul app
st.title("Mapbox dengan Multiple Titik Koordinat (Draggable)")

# Instruksi
st.markdown("""
App ini menampilkan peta Mapbox dengan multiple markers yang bisa ditambah/geser.
- Klik peta untuk tambah marker baru.
- Geser marker untuk ubah posisi.
- Koordinat ditampilkan di panel kiri.
- Hapus marker via tombol di list.

**Catatan:** Kamu perlu token Mapbox sendiri. Ganti di kode HTML di bawah.
""")

# Input token Mapbox (opsional, bisa hardcode)
mapbox_token = st.text_input("Masukkan Mapbox Access Token (dapatkan di account.mapbox.com)", value="pk.eyJ1Ijoi... ISI TOKEN KAMU ...")

# Kode HTML/JS Mapbox (mirip versi sebelumnya, tapi diembed)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <link href="https://api.mapbox.com/mapbox-gl-js/v3.9.0/mapbox-gl.css" rel="stylesheet"/>
  <style>
    body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
    #map {{ height: 600px; width: 100%; }}
    #info {{
      background: white;
      padding: 12px 16px;
      border-radius: 6px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.3);
      max-width: 320px;
      font-size: 13px;
      max-height: 400px;
      overflow-y: auto;
    }}
    #info h4 {{ margin: 0 0 8px; font-size: 15px; }}
    .marker-item {{ margin: 6px 0; padding: 6px; background: #f8f9fa; border-radius: 4px; }}
    .marker-item button {{ margin-left: 8px; font-size: 11px; padding: 2px 6px; }}
    .coords {{ font-family: monospace; color: #d63384; }}
  </style>
</head>
<body>
  <div id="map"></div>
  <div id="info" style="position: absolute; top: 10px; left: 10px; z-index: 10;">
    <h4>Multiple Titik Koordinat</h4>
    Klik peta untuk tambah titik baru<br>
    Geser marker untuk ubah posisi<br>
    <div id="markers-list"></div>
  </div>

  <script src="https://api.mapbox.com/mapbox-gl-js/v3.9.0/mapbox-gl.js"></script>
  <script>
    mapboxgl.accessToken = '{mapbox_token}';

    const map = new mapboxgl.Map({{
      container: 'map',
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [112.750, -7.250], // Surabaya
      zoom: 11
    }});

    const markersData = [];

    function updateMarkersList() {{
      const listEl = document.getElementById('markers-list');
      listEl.innerHTML = '';

      if (markersData.length === 0) {{
        listEl.innerHTML = '<small>Belum ada titik</small>';
        return;
      }}

      markersData.forEach((item, index) => {{
        const div = document.createElement('div');
        div.className = 'marker-item';
        div.innerHTML = `
          Titik ${{index + 1}}: 
          <span class="coords">${{item.lngLat.lng.toFixed(6)}}, ${{item.lngLat.lat.toFixed(6)}}</span>
          <button onclick="removeMarker(${{index}})">Hapus</button>
        `;
        listEl.appendChild(div);
      }});
    }}

    window.removeMarker = function(index) {{
      const item = markersData[index];
      if (item) {{
        item.marker.remove();
        item.popup.remove();
        markersData.splice(index, 1);
        updateMarkersList();
      }}
    }};

    function addOrUpdateMarker(lngLat, isNew = true) {{
      const marker = new mapboxgl.Marker({{
        color: isNew ? '#FF5733' : '#3388FF',
        draggable: true
      }})
        .setLngLat(lngLat)
        .addTo(map);

      const popup = new mapboxgl.Popup({{
        offset: 28,
        closeButton: true,
        closeOnClick: false
      }})
        .setLngLat(lngLat)
        .setHTML(`
          <strong>Titik:</strong><br>
          <span class="coords">${{lngLat.lng.toFixed(6)}}, ${{lngLat.lat.toFixed(6)}}</span>
          <br><small>Klik & drag untuk geser</small>
        `)
        .addTo(map);

      const item = {{ marker, popup, lngLat }};
      markersData.push(item);

      marker.on('dragend', () => {{
        const newLngLat = marker.getLngLat();
        item.lngLat = newLngLat;
        popup.setLngLat(newLngLat)
             .setHTML(`
               <strong>Titik:</strong><br>
               <span class="coords">${{newLngLat.lng.toFixed(6)}}, ${{newLngLat.lat.toFixed(6)}}</span>
               <br><small>Klik & drag untuk geser</small>
             `);
        updateMarkersList();
      }});

      updateMarkersList();
    }}

    map.on('click', (e) => {{
      addOrUpdateMarker(e.lngLat, true);
    }});

    map.on('load', () => {{
      const initialPoints = [
        {{ lng: 112.7368, lat: -7.2575 }},
        {{ lng: 112.7680, lat: -7.2650 }},
        {{ lng: 112.7200, lat: -7.2900 }}
      ];
      initialPoints.forEach(pt => {{
        addOrUpdateMarker(pt, false);
      }});
    }});
  </script>
</body>
</html>
"""

# Embed HTML ke Streamlit (tinggi bisa disesuaikan)
components.html(html_code, height=700)

# Tambahan: Tombol untuk reset atau export (opsional, tapi JS di atas sudah cukup interaktif)
st.markdown("**Export Koordinat:** Copy dari panel di peta. Untuk fitur lebih (simpan ke file), bisa ditambahkan nanti.")