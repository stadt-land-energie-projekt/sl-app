

function getSelectedRegions() {
    // Read selected regions from banner
    return Array.from(document.getElementById("selected_regions").querySelectorAll("input[name='region']")).map(region => parseInt(region.value));
}

function toggleRegion(region_id, region_name) {
    if (getSelectedRegions().includes(region_id)) {
        deselectRegion(region_id);
    } else {
        selectRegion(region_id, region_name);
    }
}

function selectRegion(region_id, region_name) {
    // Add region to banner
    const col = document.createElement("div");
    col.className = "col";
    const span = document.createElement("span");
    span.className = "badge badge-secondary";
    span.innerHTML = region_name;
    const input = document.createElement("input");
    input.hidden = true;
    input.name = "region";
    input.value = region_id;
    col.appendChild(span);
    col.appendChild(input);
    document.getElementById("selected_regions").getElementsByClassName("row")[0].appendChild(col);
    // TODO: Remove "Keine Region ausgewählt." if first region is added
    // TODO: Add FeatureState "selected" to region
}

function deselectRegion(region_id) {
    // Remove region from banner
    const regionNodes = document.getElementById("selected_regions").querySelectorAll(`input[name='region']`);
    const matchingRegionNodes = Array.from(regionNodes).filter(regionNode => parseInt(regionNode.value) === region_id);
    if (matchingRegionNodes.length > 0) {
        matchingRegionNodes[0].parentNode.remove();
    }
    // TODO: Add "Keine Region ausgewählt." if last region is removed
    // TODO: Remove FeatureState "selected" from region
}
