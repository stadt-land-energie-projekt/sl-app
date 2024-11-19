import os
import csv
import subprocess
import json
import logging
from pathlib import Path
from time import sleep, time
from shutil import rmtree
from django.urls import reverse, reverse_lazy

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from slapp.explorer.models import Municipality, Region

MAX_MUNICIPALITY_COUNT = 3


# Basis- und Verzeichnis-Einstellungen
BASE_DIR = Path(__file__).resolve().parent.parent
PLOTS_DIR = BASE_DIR / 'kommWertTool' / 'tmp' / 'plots'

# Verzeichnis erstellen, falls nicht vorhanden
def create_plots_directory():
    if not PLOTS_DIR.exists():
        PLOTS_DIR.mkdir(parents=True)
        logging.debug(f"Verzeichnis erstellt: {PLOTS_DIR}")
    else:
        logging.debug(f"Verzeichnis existiert bereits: {PLOTS_DIR}")

create_plots_directory()

# Verzeichnis löschen
def clear_plots_directory():
    for filename in PLOTS_DIR.iterdir():
        if filename.is_file() or filename.is_symlink():
            filename.unlink()
        elif filename.is_dir():
            rmtree(filename)

# Haupt-Ansicht
def index(request):
    try:
        """Render page for information about 'Wertschöpfung'."""
        next_url = None
        prev_url = reverse("explorer:results_variation")
        active_tab = "step_7_added_value"
        sidepanel = True

        if request.session.get("prev_before_added_value") == "robustness":
            prev_url = reverse("explorer:results_robustness")

        ids = request.session.get("municipality_ids", [])
        muns = Municipality.objects.filter(id__in=ids) if ids else None

        context = {
            "next_url": next_url,
            "prev_url": prev_url,
            "active_tab": active_tab,
            "has_sidepanel": sidepanel,
            "municipalities": muns
        }
        return render(request, "added_value_calc.html", context)
    except Exception as e:
        return HttpResponse(f'Fehler beim Lesen der added_value_calc.html: {str(e)}', status=500)


# Einsende-Ansicht
@require_http_methods(["POST"])
def submit(request):
    form_data = request.POST.dict()
    form_data = {k: '0' if v in ['', 'Bitte wählen:'] else v for k, v in form_data.items()}
    fieldnames = list(form_data.keys())

    csv_path = BASE_DIR / 'kommWertTool' / 'tmp' / 'input_variables.csv'
    if csv_path.exists():
        csv_path.unlink()

    try:
        with open(csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(fieldnames)
            writer.writerow([form_data[field] for field in fieldnames])
            file.flush()
            os.fsync(file.fileno())
        logging.debug("CSV-Datei erfolgreich geschrieben. Inhalt:")
        with open(csv_path, mode='r', encoding="utf-8") as check_file:
            logging.debug(check_file.read())
    except Exception as e:
        return HttpResponse(f"Fehler beim Speichern der Daten: {str(e)}", status=500)

    clear_plots_directory()

    # Ausführung des externen Skripts
    results = run_external_script('slapp/kommWertTool/cal_mun_rev.py')

    required_keys = [
        'plot_file_komm_wert_jaehrliche_pachteinnahmen',
        'plot_file_einnahmen_wind_solar_euro',
        'plot_file_komm_wert_eeg_einnahmen',
        'plot_file_gewerbesteuer_agri_pv',
        'plot_file_gewerbesteuer_ff_pv',
        'plot_file_gewerbesteuer_wind',
        'plot_file_gesamteinnahmen'
    ]

    def plots_exist():
        missing_plots = []
        for key in required_keys:
            plot_file = results.get(key)
            filepath = PLOTS_DIR / plot_file if plot_file else None
            if not (plot_file and filepath.exists()):
                missing_plots.append(key)
                logging.error(f"Fehlt: {key} -> {filepath}")
        if missing_plots:
            logging.error(f"Fehlende Plots: {missing_plots}")
            return False
        return True

    start_time = time()
    timeout_seconds =1200
    sleep_interval = 5

    logging.debug("Prüfe, ob die Plots existieren...")

    while not plots_exist():
        if time() - start_time > timeout_seconds:
            logging.error("Timeout waiting for plots to be created")
            return HttpResponse("Timeout waiting for plots to be created", status=500)
        sleep(sleep_interval)

    try:
        """Render page for information about 'Wertschöpfung'."""
        next_url = None
        prev_url = reverse("kommWertTool:added_value")
        active_tab = "step_7_added_value"
        sidepanel = True

        ids = request.session.get("municipality_ids", [])
        muns = Municipality.objects.filter(id__in=ids) if ids else None



        return render(request, 'added_value_results.html', {
            'results': results,
            'plot_komm_wert_jaehrliche_pachteinnahmen': results.get('plot_file_komm_wert_jaehrliche_pachteinnahmen'),
            'plot_einnahmen_wind_solar_euro': results.get('plot_file_einnahmen_wind_solar_euro'),
            'plot_komm_wert_eeg_einnahmen': results.get('plot_file_komm_wert_eeg_einnahmen'),
            'plot_gewerbesteuer_wind': results.get('plot_file_gewerbesteuer_wind'),
            'plot_gewerbesteuer_ff_pv': results.get('plot_file_gewerbesteuer_ff_pv'),
            'plot_gewerbesteuer_agri_pv': results.get('plot_file_gewerbesteuer_agri_pv'),
            'plot_file_gesamteinnahmen': results.get('plot_file_gesamteinnahmen'),
            'time_instance': int(time()),
            "next_url": next_url,
            "prev_url": prev_url,
            "active_tab": active_tab,
            "has_sidepanel": sidepanel,
            "municipalities": muns
        })
    except Exception as e:
        return HttpResponse(f'Fehler beim Lesen der added_value_calc.html: {str(e)}', status=500)
# Skript ausführen
def run_external_script(script_path, timeout=600):
    try:
        logging.debug(f"Starte Skript: {script_path}")
        result = subprocess.run(['python', script_path], capture_output=True, text=True, check=True, timeout=timeout)
        logging.debug(f"Skript {script_path} beendet")
        output = result.stdout.strip()
        logging.debug(f"Output from {script_path}: {output}")
        if not output:
            logging.error(f"No output from script: {script_path}")
            return {"error": f"Kein Output vom Skript: {script_path}"}
        return json.loads(output)
    except subprocess.CalledProcessError as e:
        logging.error(f"Fehler beim Ausführen des Skripts: {e.stderr}")
        return {"error": f"Fehler beim Ausführen des Skripts: {e.stderr}"}
    except subprocess.TimeoutExpired:
        logging.error(f"Das Skript {script_path} hat zu lange gebraucht.")
        return {"error": f"Das Skript {script_path} hat zu lange gebraucht."}
    except json.JSONDecodeError as e:
        logging.error(f"Fehler beim Dekodieren von JSON: {str(e)}")
        return {"error": f"Fehler beim Dekodieren von JSON: {str(e)}"}

# Plot senden
def send_plot(request, filename):
    path = PLOTS_DIR / filename
    logging.debug(f"Sending plot from {PLOTS_DIR} : {filename}")

    if not path.exists():
        logging.error(f"File does not exist: {path}")
        return HttpResponse("File not found", status=404)

    with open(path, 'rb') as f:
        response = HttpResponse(f.read(), content_type="image/jpeg")
        response['Cache-Control'] = 'no-store'
        return response
