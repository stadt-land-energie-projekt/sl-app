

function getSelectedRegions() {
    // Read selected regions from banner
    return Array.from(document.getElementById("selected_regions").querySelectorAll("input[name='region']")).map(region => parseInt(region.value));
}

function toggleRegion(region) {
    if (getSelectedRegions().includes(region.id)) {
        deselectRegion(region);

    } else {
        selectRegion(region);
    }
}


function selectRegion(region) {
    // Add region to banner
    const col = document.createElement("div");
    col.className = "col";
    const span = document.createElement("span");
    span.className = "badge badge-secondary";
    span.innerHTML = region.properties.name;
    const input = document.createElement("input");
    input.hidden = true;
    input.name = "region";
    input.value = region.id;
    col.appendChild(span);
    col.appendChild(input);
    document.getElementById("selected_regions").getElementsByClassName("row")[0].appendChild(col);
}

function deselectRegion(region) {
    // Remove region from banner
    const regionNodes = document.getElementById("selected_regions").querySelectorAll(`input[name='region']`);
    const matchingRegionNodes = Array.from(regionNodes).filter(regionNode => parseInt(regionNode.value) === region.id);
    if (matchingRegionNodes.length > 0) {
        matchingRegionNodes[0].parentNode.remove();
    }
}
