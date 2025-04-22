from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)

@app.route("/")
def map_view():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <title>Crab Map</title>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
  <script src="https://unpkg.com/leaflet.vectorgrid@1.3.0/dist/Leaflet.VectorGrid.bundled.js"></script>

  <style>
    html, body, #map { height: 100%; margin: 0; }
  </style>
</head>
<body>
<div id="map"></div>
<script>
  var map = L.map('map').setView([44.5, -68.5], 7);  // center on Maine coast

  L.vectorGrid.protobuf("http://localhost:9000/data/maine/{z}/{x}/{y}.pbf", {
    vectorTileLayerStyles: {
      admin: { color: "#000", weight: 1 },
      maritime: { color: "#0000ff", dashArray: "4,4", weight: 2 },
      coastline: { color: "#222", weight: 1.5 },
      water: { fill: true, fillColor: "#aad3df", fillOpacity: 1, stroke: false },
      landuse: { fill: true, fillColor: "#e0e0e0", fillOpacity: 0.4 },
      seamark: { radius: 4, fillColor: "#f90", color: "#f60", weight: 1 },
      harbor: { color: "#666699", weight: 2, fillOpacity: 0.6 },
      fishing: { color: "#c33", fillColor: "#fbb", fillOpacity: 0.6 },
      islands: { fill: true, fillColor: "#c2b280", fillOpacity: 0.8, color: "#333", weight: 0.5 }
    },
    interactive: true,
    maxZoom: 18
  }).addTo(map);
</script>
</body>
</html>
    """)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
