// Function to attach click events to markers
function attachMarkerEvents(mapInstance) {
    console.log("✅ Attaching marker click events...");
    if (!mapInstance) {
        console.error("❌ ERROR: Map instance is undefined.");
        return;
    }

    let markerCount = 0;
    mapInstance.eachLayer(function(layer) {
        if (layer instanceof L.Marker) {
            markerCount++;
            console.log("✅ Marker found:", layer);
            layer.on("click", function() {
                if (layer.getPopup()) {
                    let popupContent = layer.getPopup().getContent();
                    let contentText = "";
                    if (typeof popupContent === "string") {
                        contentText = popupContent;
                    } else if (popupContent instanceof HTMLElement) {
                        contentText = popupContent.innerText;
                    } else {
                        contentText = String(popupContent);
                    }
                    console.log("Popup Content:", contentText);
                    let match = contentText.match(/Buoy ID:\s*(\d+)/);
                    if (match) {
                        let buoyId = match[1];
                        console.log("markerClicked:" + buoyId);
                        alert("Buoy Clicked: " + buoyId);
                    }
                }
            });
        }
    });
    console.log("✅ Total Markers Found:", markerCount);
}

// Optionally, if you need to run attachMarkerEvents without waiting for QWebChannel (for debugging)
document.addEventListener("readystatechange", function () {
    if (document.readyState === "complete") {
        attachMarkerEvents({{map_instance}});
    }
});