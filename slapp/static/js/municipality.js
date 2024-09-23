

function getSelectedMunicipalities() {
    // Read selected municipalities from banner
    return Array.from(document.getElementById("selected_municipalities").querySelectorAll("input[name='selected_mun']")).map(municipality => parseInt(municipality.value));
}

function toggleMunicipality(municipality_id, municipality_name) {
    if (getSelectedMunicipalities().includes(municipality_id)) {
        deselectMunicipality(municipality_id);
    } else {
        selectMunicipality(municipality_id, municipality_name);
    }
}

function selectMunicipality(municipality_id, municipality_name) {
    // Remove "No municipality selected" info if first municipality gets selected
    if (getSelectedMunicipalities().length === 0) {
        document.getElementById("selected_municipalities").getElementsByTagName("p")[1].remove();
    }
    // Add municipality to banner
    const col = document.createElement("div");
    col.className = "col";
    const span = document.createElement("span");
    span.className = "badge badge-secondary";
    span.innerHTML = municipality_name;
    const input = document.createElement("input");
    input.hidden = true;
    input.name = "selected_mun";
    input.value = municipality_id;
    col.appendChild(span);
    col.appendChild(input);
    document.getElementById("selected_municipalities").getElementsByClassName("row")[0].appendChild(col);
    selectMunicipalityInMap(municipality_id, true);
}

function deselectMunicipality(municipality_id) {
    // Remove municipality from banner
    const municipalityNodes = document.getElementById("selected_municipalities").querySelectorAll(`input[name='selected_mun']`);
    const matchingMunicipalityNodes = Array.from(municipalityNodes).filter(municipalityNode => parseInt(municipalityNode.value) === municipality_id);
    if (matchingMunicipalityNodes.length > 0) {
        matchingMunicipalityNodes[0].parentNode.remove();
        selectMunicipalityInMap(municipality_id, false);
    }
    // Add "No municipality selected" info if last municipality gets deselected
    if (getSelectedMunicipalities().length === 0) {
        const paragraph = document.createElement("p");
        paragraph.innerHTML = "Keine Region ausgewählt.";
        document.getElementById("selected_municipalities").getElementsByClassName("row")[0].appendChild(paragraph);
    }
}

function selectMunicipalityInMap(municipality_id, selected) {
    map.setFeatureState(
        {
            source: "municipality",
            sourceLayer: "municipality",
            id: municipality_id
        },
        {
            selected: selected
        }
    );
}

document.addEventListener('DOMContentLoaded', function () {
    const regionSelect = document.getElementById('region_select');

    if (regionSelect) {
        regionSelect.addEventListener('change', function () {
            const selectedMunicipalities = document.getElementById('municipality_select').selectedOptions;
            const municipalitySelected = selectedMunicipalities.length > 0;

            if (municipalitySelected) {
                $('#region_change_confirmation').modal('show');

            } else {
                this.setAttribute('data-previous-region-id', regionSelect.value);
            }
        });
    }

    document.getElementById('confirm_region_change_btn').addEventListener('click', function () {
        const regionID = regionSelect.value;
        fetch(`/explorer/load-municipalities/?region_select=${regionID}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        }).then(function () {
            $('#region_change_confirmation').modal('hide');
            deselectMunicipality(regionSelect);
        });
            this.setAttribute('data-previous-region-id', regionID);
            htmx.trigger("#municipality_select", "resetRegion");
    });

    document.getElementById('abort_region_change_btn').addEventListener('click', function () {
        const prevRegionSelect = regionSelect.getAttribute('data-previous-region-id');
        $('#region_change_confirmation').modal('hide');
        regionSelect.value = prevRegionSelect;
        htmx.trigger("#region_select", "resetRegion");
    });
});
