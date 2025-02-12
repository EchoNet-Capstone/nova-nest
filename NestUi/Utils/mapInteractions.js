console.log("✅ mapInteractions.js loaded!");

// Function to attach click events to markers
function attachMarkerEvents(mapInstance) {
    console.log("✅ Attaching marker click events...");

    if (!mapInstance) {
        console.error("❌ ERROR: Map instance is undefined.");
        return;
    }

    let markerCount = 0;
    mapInstance.eachLayer(function (layer) {
        if (layer instanceof L.Marker) {
            markerCount++;
            console.log("✅ Marker found:", layer);

            layer.on("click", function () {
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
                    let match = contentText.match(/Buoy ID: (BUOY-\d+)/);
                    if (match) {
                        let buoyId = match[1];
                        console.log("✅ Clicked Buoy ID:", buoyId);
                        alert("Buoy Clicked: " + buoyId);
                        if (window.qtChannel) {
                            console.log("✅ Sending Buoy ID to PyQt");
                            window.qtChannel.markerClicked.emit(buoyId);
                        } else {
                            console.log("❌ Qt WebChannel not found!");
                        }
                    }
                }
            });
        }
    });
    console.log("✅ Total Markers Found:", markerCount);
}

// When the document is fully loaded, call attachMarkerEvents with the map instance passed from Python.
document.addEventListener("readystatechange", function () {
    if (document.readyState === "complete") {
        console.log("✅ Document loaded, running attachMarkerEvents()...");
        attachMarkerEvents({{ map_instance }});
    }
});