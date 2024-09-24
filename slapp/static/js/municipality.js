

function getSelectedMunicipalities() {
    // Read selected municipalities from banner
    return Array.from(document.getElementById("selected_municipalities").querySelectorAll("input[name='selected_mun']")).map(municipality => parseInt(municipality.value));
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

function toggleMunicipalities() {
    /**
     * Removes selection for all municipalities and re-selects municipalities from selection
     */
    map.removeFeatureState({source: "municipality", sourceLayer: "municipality"});
    const munsInSelection = Array.from(document.getElementById('municipality_select').selectedOptions).map(item => parseInt(item.value));
    for (const munId of munsInSelection) {
        selectMunicipalityInMap(munId, true);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('municipality_select').addEventListener('change', toggleMunicipalities);
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
        });
        this.setAttribute('data-previous-region-id', regionID);
        htmx.trigger("#region_select", "resetRegion");
        htmx.trigger("#municipality_select", "resetRegion");
    });

    document.getElementById('abort_region_change_btn').addEventListener('click', function () {
        const prevRegionSelect = regionSelect.getAttribute('data-previous-region-id');
        $('#region_change_confirmation').modal('hide');
        regionSelect.value = prevRegionSelect;
        htmx.trigger("#region_select", "resetRegion");
    });
});
