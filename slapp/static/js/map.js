
PubSub.subscribe(mapEvent.MAP_LOADED, activateRegionSelection);


function activateRegionSelection(msg) {
    map.on("click", function (element) {
        const features = map.queryRenderedFeatures(element.point, {layers: ['municipality']});
        if (features.length === 0) {
            return;
        }
        toggleRegion(features[0]);
    });
    return logMessage(msg);
}
