

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
    // Remove "No region selected" info if first region gets selected
    if (getSelectedRegions().length === 0) {
        document.getElementById("selected_regions").getElementsByTagName("p")[1].remove();
    }
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
    // TODO: Add FeatureState "selected" to region
}

function deselectRegion(region_id) {
    // Remove region from banner
    const regionNodes = document.getElementById("selected_regions").querySelectorAll(`input[name='region']`);
    const matchingRegionNodes = Array.from(regionNodes).filter(regionNode => parseInt(regionNode.value) === region_id);
    if (matchingRegionNodes.length > 0) {
        matchingRegionNodes[0].parentNode.remove();
    }
    // Add "No region selected" info if last region gets deselected
    if (getSelectedRegions().length === 0) {
        const paragraph = document.createElement("p");
        paragraph.innerHTML = "Keine Region ausgewählt.";
        document.getElementById("selected_regions").getElementsByClassName("row")[0].appendChild(paragraph);
    }
    // TODO: Remove FeatureState "selected" from region
}
