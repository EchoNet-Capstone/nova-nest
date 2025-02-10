console.log("✅ mapInteractions.js loaded!");

// Function to attach click events to markers
function attachMarkerEvents() {
    console.log("✅ Attaching marker click events...");

    if (typeof map_87504f654c85298218282642e0c45ffb === "undefined") {
        console.error("❌ ERROR: Map instance is undefined.");
        return;
    }

    let markerCount = 0;
    map_87504f654c85298218282642e0c45ffb.eachLayer(function (layer) {
        if (layer instanceof L.Marker) {
            markerCount++;
            console.log("✅ Marker found:", layer);

            layer.on("click", function () {
                if (layer.getPopup()) {
                    let popupContent = layer.getPopup().getContent();
                    console.log("Popup Content:", popupContent);

                    let match = popupContent.match(/Buoy ID: (BUOY-\\d+)/);
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

    console.log(`✅ Total Markers Found: ${markerCount}`);
}

// Run after the document is fully loaded
document.addEventListener("readystatechange", function () {
    if (document.readyState === "complete") {
        console.log("✅ Document loaded, running attachMarkerEvents()...");
        attachMarkerEvents();
    }
});