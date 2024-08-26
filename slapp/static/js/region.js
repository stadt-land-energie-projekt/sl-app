

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
    selectRegionInMap(region_id, true);
}

function deselectRegion(region_id) {
    // Remove region from banner
    const regionNodes = document.getElementById("selected_regions").querySelectorAll(`input[name='region']`);
    const matchingRegionNodes = Array.from(regionNodes).filter(regionNode => parseInt(regionNode.value) === region_id);
    if (matchingRegionNodes.length > 0) {
        matchingRegionNodes[0].parentNode.remove();
        selectRegionInMap(region_id, false);
    }
    // Add "No region selected" info if last region gets deselected
    if (getSelectedRegions().length === 0) {
        const paragraph = document.createElement("p");
        paragraph.innerHTML = "Keine Region ausgewählt.";
        document.getElementById("selected_regions").getElementsByClassName("row")[0].appendChild(paragraph);
    }
}

function selectRegionInMap(region_id, selected) {
    map.setFeatureState(
        {
            source: "municipality",
            sourceLayer: "municipality",
            id: region_id
        },
        {
            selected: selected
        }
    );
}

document.addEventListener('DOMContentLoaded', function () {
    const regionSelect = document.getElementById('region_select');
    if (regionSelect) {
        regionSelect.addEventListener('change', function (event) {
            const selectedMunicipalities = document.getElementById('municipality_select').selectedOptions;
            const municipalitySelected = selectedMunicipalities.length > 0;

            if (municipalitySelected) {
                $('#region_change_confirmation').modal('show');

            }
        });
    }

    document.getElementById('confirm_region_change_btn').addEventListener('click', function () {

        fetch(`/explorer/load-municipalities/?region=?${regionSelect}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        }).then(function () {
            $('#region_change_confirmation').modal('hide');
            deselectRegion(regionSelect);
        }).then(function(){
            htmx.trigger("#municipality_select", "resetRegion")
        });
    });
});
