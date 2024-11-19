import os
import csv
import subprocess
import json
import logging
from pathlib import Path
from time import sleep, time
from shutil import rmtree
from django.urls import reverse

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from slapp.explorer.models import Municipality

MAX_MUNICIPALITY_COUNT = 3

# Basis- und Verzeichnis-Einstellungen
BASE_DIR = Path(__file__).resolve().parent.parent
CHARTS_DIR = BASE_DIR / 'kommWertTool' / 'tmp' / 'charts'
def load_chart_data(filename):
    charts_dir = os.path.join(BASE_DIR, 'kommWertTool', 'tmp', 'charts')
    file_path = os.path.join(charts_dir, filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return None

def check_charts_data(request, chart_type):
    filenames = {
        'eeg_beteiligung': 'eeg_beteiligung.json',
        'wind_solar_euro': 'wind_solar_euro.json',
        'pachteinnahmen': 'pachteinnahmen.json',
        'gesamteinnahmen': 'gesamteinnahmen.json',
        'gewerbesteuer_wind': 'gewerbesteuer_wind.json',
        'gewerbesteuer_ff_pv': 'gewerbesteuer_ff_pv.json',
        'gewerbesteuer_agri_pv': 'gewerbesteuer_agri_pv.json'
        # incluce more charts
    }

    data = load_chart_data(filenames.get(chart_type))
    if data:
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Data not found:'}, status=404)

# Verzeichnis erstellen, falls nicht vorhanden
def create_plots_directory():
    if not CHARTS_DIR.exists():
        CHARTS_DIR.mkdir(parents=True)
        logging.debug(f"Verzeichnis erstellt: {CHARTS_DIR}")
    else:
        logging.debug(f"Verzeichnis existiert bereits: {CHARTS_DIR}")

create_plots_directory()

# Verzeichnis löschen
def clear_plots_directory():
    for filename in CHARTS_DIR.iterdir():
        if filename.is_file() or filename.is_symlink():
            filename.unlink()
        elif filename.is_dir():
            rmtree(filename)

# Haupt-Ansicht
def index(request):
    try:
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

    # Erstellen eines Zeitstempels, um ihn in der HTML-Ansicht anzuzeigen
    timestamp = int(time())

    results = run_external_script('slapp/kommWertTool/cal_mun_rev.py')
    results_dict = results
    try:
        next_url = None
        prev_url = reverse("kommWertTool:added_value")
        active_tab = "step_7_added_value"
        sidepanel = True

        ids = request.session.get("municipality_ids", [])
        muns = Municipality.objects.filter(id__in=ids) if ids else None

        return render(request, 'added_value_results.html', {
            'results': results_dict,
            'timestamp': timestamp,  # Zeitstempel an HTML-Template übergeben
            "next_url": next_url,
            "prev_url": prev_url,
            "active_tab": active_tab,
            "has_sidepanel": sidepanel,
            "municipalities": muns
        })
    except Exception as e:
        return HttpResponse(f'Fehler beim Lesen der added_value_calc.html: {str(e)}', status=500)

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
