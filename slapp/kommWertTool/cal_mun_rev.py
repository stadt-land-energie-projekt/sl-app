import pandas as pd
import numpy as np
import csv
import sys
import json
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


timestamp = int(time.time())
CURRENT_DIR = Path(__file__).resolve().parent
SEQUENCES_DIR = CURRENT_DIR / 'data/sequences'
CHARTS_DIR = CURRENT_DIR / 'tmp/charts'
CHARTS_DIR.mkdir(parents=True, exist_ok=True)


av_grey = '#AFAFAF'
av_yellow = '#FDDA0D'
av_light_grey = '#3d3d3d'
av_red = '#FF5C5C'
av_blue = '#409EFF'
av_green = '#67C23A'
av_orange = '#FF9900'
av_blue_lighter = '#bbdeea'
av_green_darker = '#a7649c'

# safe echarts as JSON
def save_echarts_data(data, filename):
    file_path = CHARTS_DIR / filename
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def create_echarts_data_pachteinnahmen(area_costs_yearly, area_est_yearly, area_gewst_yearly):
    echarts_data = {

        "legend": {
            "top": "0",
            "data": ["Direkte Pachteinnahmen", "Komm. ESt-Anteil", "Komm. GewSt-Anteil"]
        },
        "xAxis": {
            "type": "category",
            "data": ["WEA", "FF-PV", "APV"],
        },
        "yAxis": {
            "type": "value",
            "name": "Einnahmen in Euro",
            "axisLabel": {
                "formatter": "{value}".replace(",", ".")
            }
        },
        "series": [
            {
                "name": "Direkte Pachteinnahmen",
                "type": "bar",
                "data": area_costs_yearly,
                "itemStyle": {
                    "color": av_grey  # Beispiel: grün
                }
            },
            {
                "name": "Komm. ESt-Anteil",
                "type": "bar",
                "data": area_est_yearly,
                "itemStyle": {
                    "color": av_light_grey  # Beispiel: blau
                }
            },
            {
                "name": "Komm. GewSt-Anteil",
                "type": "bar",
                "data": area_gewst_yearly,
                "itemStyle": {
                    "color": av_yellow  # Beispiel: orange
                }
            }
        ]
    }
    save_echarts_data(echarts_data, f"pachteinnahmen.json")

def create_echarts_data_eeg(wind_eeg_yearly, pv_eeg_yearly, apv_eeg_yearly):
    echarts_data = {
        "legend": {
            "top": "0",
            "data": ["WEA", "FF-PV", "APV"]
        },
        "xAxis": {
            "type": "category",
            "data": ["EEG Einnahmen"],
        },
        "yAxis": {
            "type": "value",
            "name": "Einnahmen in Euro",
            "axisLabel": {
                "formatter": "{value}".replace(",", ".")
            }
        },
        "series": [
            {"name": "WEA", "type": "bar", "itemStyle": {
                    "color": av_red}, "data": [wind_eeg_yearly]},  # Wert als Liste
            {"name": "FF-PV", "type": "bar", "itemStyle": {
                    "color": av_blue}, "data": [pv_eeg_yearly]},  # Wert als Liste
            {"name": "APV", "type": "bar", "itemStyle": {
                    "color": av_green}, "data": [apv_eeg_yearly]}   # Wert als Liste
        ]
    }
    save_echarts_data(echarts_data, f"eeg_beteiligung.json")


def create_echarts_data_gewerbesteuer(data, years, filename, title, color):
    if not isinstance(data, list):
        raise TypeError(f"Erwarteter Typ für 'data' ist list, erhalten: {type(data)}")
    adjusted_data = [(item[0], max(item[1], 0)) for item in data]

    echarts_data = {
        "legend": {
            "top": "0",
            "data": [title]
        },
        "xAxis": {
            "type": "category",
            "name": "Jahre",
            "data": list(range(1, years + 1))
        },
        "yAxis": {
            "type": "value",
            "name": "Gewerbesteuer in Euro",
            "axisLabel": {
                "formatter": "{value}".replace(",", ".")
            }
        },
        "series": [{
            "name": title,
            "type": "bar",
            "data": [item[1] for item in adjusted_data if item[0] <= years],
            "itemStyle": {
                "color": color
            }
        }]
    }

    save_echarts_data(echarts_data, filename)

def create_echarts_data_srbb(wind_sr_bb_yearly, pv_sr_bb_yearly, apv_sr_bb_yearly):
    echarts_data_sr = {
        "legend": {
            "top": "0",
            "data": ["WEA", "FF-PV", "APV"]
        },
        "xAxis": {
            "type": "category",
            "data": ["Wind-/Solar-Euro"],
        },
        "yAxis": {
            "type": "value",
            "name": "Einnahmen in Euro",
            "axisLabel": {
                "formatter": "{value}".replace(",", ".")
            }
        },
        "series": [
            {"name": "WEA", "type": "bar", "itemStyle": {
                    "color": av_red}, "data": [wind_sr_bb_yearly]},  # Wert als Liste
            {"name": "FF-PV", "type": "bar", "itemStyle": {
                    "color": av_blue}, "data": [pv_sr_bb_yearly]},  # Wert als Liste
            {"name": "APV", "type": "bar", "itemStyle": {
                    "color": av_green}, "data": [apv_sr_bb_yearly]}   # Wert als Liste
        ]
    }
    save_echarts_data(echarts_data_sr, f"wind_solar_euro.json")
def create_echarts_data_gesamteinnahmen(gewerbesteuer_anlagen, eeg_einnahmen, sr_bb_einnahmen,
                                        area_costs_total, area_gewst_total, area_est_total, sum_wea_plot, sum_agri_pv_plot, sum_ff_pv_plot):
    legend_data = []
    series_data = []

    # Hilfsfunktion zum Hinzufügen von Daten
    def add_series(name, data, yAxisIndex=0):
        if any(value > 0 for value in data):
            legend_data.append(name)
            series_data.append({"name": name, "type": "bar", "data": data, "yAxisIndex": yAxisIndex})

    # Fügen Sie die Serien hinzu
    add_series("GewSt.-Einnahmen Anlagengewinne", gewerbesteuer_anlagen)
    add_series("EEG-Beteiligung", eeg_einnahmen)
    add_series("Wind-/Solar-Euro", sr_bb_einnahmen)
    add_series("Direkte Pachteinnahmen", area_costs_total)
    add_series("GewSt.-Einnahmen Pacht", area_gewst_total)
    add_series("ESt.-Einnahmen Pacht", area_est_total)
    add_series("Gesamteinnahmen WEA", sum_wea_plot, 1)
    add_series("Gesamteinnahmen FF-PV", sum_ff_pv_plot, 1)
    add_series("Gesamteinnahmen APV", sum_agri_pv_plot, 1)

    echarts_data = {

        "legend": {
            "top": "0",
            "bottom": "50%",
            "padding": [5, 10, 15, 10],  # [top, right, bottom, left]
            "data": legend_data
        },
        "xAxis": {
            "type": "category",
            "data": ["WEA", "FF-PV", "APV", "Gesamt WEA", "Gesamt FF-PV", "Gesamt APV"],
        },
        "yAxis": [
            {
                "type": "value",
                "name": "Einnahmen in Euro",
                "axisLabel": {
                    "formatter": "{value}".replace(",", ".")
                }
            },
            {
                "type": "value",
                "name": "Gesamteinnahmen in Euro",
                "axisLabel": {
                    "formatter": "{value}".replace(",", ".")
                },
                "position": "right"
            }
        ],
        "series": [
            {"name": "GewSt.-Einnahmen Anlagengewinne", "type": "bar", "itemStyle": {"color": av_blue_lighter}, "data": gewerbesteuer_anlagen},
            {"name": "EEG-Beteiligung", "type": "bar", "itemStyle": {"color": av_green_darker}, "data": eeg_einnahmen},
            {"name": "Wind-/Solar-Euro", "itemStyle": {"color": av_orange}, "type": "bar", "data": sr_bb_einnahmen},
            {"name": "Direkte Pachteinnahmen", "type": "bar", "itemStyle": {"color": av_grey}, "data": area_costs_total},
            {"name": "GewSt.-Einnahmen Pacht", "type": "bar", "itemStyle": {"color": av_yellow}, "data": area_gewst_total},
            {"name": "ESt.-Einnahmen Pacht", "type": "bar", "itemStyle": {"color": av_light_grey}, "data": area_est_total},
            {"name": "Gesamteinnahmen WEA", "type": "bar", "itemStyle": {"color": av_red}, "data": sum_wea_plot, "yAxisIndex": 1},
            {"name": "Gesamteinnahmen FF-PV", "type": "bar", "itemStyle": {"color": av_blue}, "data": sum_ff_pv_plot, "yAxisIndex": 1},
            {"name": "Gesamteinnahmen APV", "type": "bar", "itemStyle": {"color": av_green}, "data": sum_agri_pv_plot, "yAxisIndex": 1},
        ],
    }
    save_echarts_data(echarts_data, f"gesamteinnahmen.json")
# read data from csv
def read_form_data():
    data = {}
    try:
        with open(CURRENT_DIR / 'tmp/input_variables.csv', mode='r', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                for key, value in row.items():
                    if key in []:  # divide percentage by 100
                        value = float(value) / 100
                    else:
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                    data[key] = value
                # read area ownership depending on number of inputs
                flaechen_eigentuemer = {
                    'wea': [],
                    'apvv': [],
                    'apvh': [],
                    'pv': []
                }
                counter = 1
                while True:
                    wea_ownertype_key = f'wea_area_ownertype{counter}'
                    wea_area_share_key = f'wea_anteil_flaeche{counter}'
                    apvv_ownertype_key = f'apvv_area_ownertype{counter}'
                    apvv_area_share_key = f'apvv_anteil_flaeche{counter}'
                    apvh_ownertype_key = f'apvh_area_ownertype{counter}'
                    apvh_area_share_key = f'apvh_anteil_flaeche{counter}'
                    pv_ownertype_key = f'ffpv_area_ownertype{counter}'
                    pv_area_share_key = f'ffpv_anteil_flaeche{counter}'

                    found_any = False

                    if wea_ownertype_key in row and row[wea_ownertype_key]:
                        eigentuemer = {
                            'ownertype': row.get(wea_ownertype_key, 'default_ownertype'),
                            'area_share': float(row.get(wea_area_share_key, 0))  # Convert to float
                        }
                        flaechen_eigentuemer['wea'].append(eigentuemer)
                        found_any = True

                    if apvv_ownertype_key in row and row[apvv_ownertype_key]:
                        eigentuemer = {
                            'ownertype': row.get(apvv_ownertype_key, 'default_ownertype'),
                            'area_share': float(row.get(apvv_area_share_key, 0))  # Convert to float
                        }
                        flaechen_eigentuemer['apvv'].append(eigentuemer)
                        found_any = True

                    if apvh_ownertype_key in row and row[apvh_ownertype_key]:
                        eigentuemer = {
                            'ownertype': row.get(apvh_ownertype_key, 'default_ownertype'),
                            'area_share': float(row.get(apvh_area_share_key, 0))  # Convert to float
                        }
                        flaechen_eigentuemer['apvh'].append(eigentuemer)
                        found_any = True

                    if pv_ownertype_key in row and row[pv_ownertype_key]:
                        eigentuemer = {
                            'ownertype': row.get(pv_ownertype_key, 'default_ownertype'),
                            'area_share': float(row.get(pv_area_share_key, 0))  # Convert to float
                        }
                        flaechen_eigentuemer['pv'].append(eigentuemer)
                        found_any = True

                    if not found_any:
                        break

                    counter += 1

            default_eigentuemer = {
                'ownertype': 'Landes-/Bundeseigentum',
                'area_share': 0
            }

            if not flaechen_eigentuemer['wea']:
                flaechen_eigentuemer['wea'].append(default_eigentuemer)
            if not flaechen_eigentuemer['apvv']:
                flaechen_eigentuemer['apvv'].append(default_eigentuemer)
            if not flaechen_eigentuemer['apvh']:
                flaechen_eigentuemer['apvh'].append(default_eigentuemer)
            if not flaechen_eigentuemer['pv']:
                flaechen_eigentuemer['pv'].append(default_eigentuemer)

            # Ensure lists are of equal length for consistency
            max_length = max(len(flaechen_eigentuemer['wea']), len(flaechen_eigentuemer['apvv']),
                             len(flaechen_eigentuemer['apvh']), len(flaechen_eigentuemer['pv']))

            def extend_list(lst):
                while len(lst) < max_length:
                    lst.append({'ownertype': 'N/A', 'area_share': 0})
                return lst

            flaechen_eigentuemer['wea'] = extend_list(flaechen_eigentuemer['wea'])
            flaechen_eigentuemer['apvv'] = extend_list(flaechen_eigentuemer['apvv'])
            flaechen_eigentuemer['apvh'] = extend_list(flaechen_eigentuemer['apvh'])
            flaechen_eigentuemer['pv'] = extend_list(flaechen_eigentuemer['pv'])

            data['flaechen_eigentuemer'] = flaechen_eigentuemer

    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Fehler beim Lesen der Formulardaten: {str(e)}"}))
        sys.exit(1)

    return data

# eeg and wind- and solar euro parameters
eeg_beteiligung = 2 # €/MWh
bb_euro_mw_wind = 5000 # €/MW
bb_euro_mw_pv = 2000 # €/MW
# taxes
ekst = 0.24 # 24% income tax
ekst_bb = 0.15 # 15% municipal share
year_income = 59094 # average annual income in BB in €
freibetrag = 24500 # tax-free amount for partner companies
steuermessbetrag = 0.035 # fix for DE
income_betriebe_bb = 220000 # annual income of businesses
# area costs per ha
pv_area_costs = 3000 # €/ha
apv_area_costs = 830 # €/ha
wea_area_costs = 16000 # € / MW
# colors
htw_green = '#76B900'
htw_green_darker = '#8FC264'
htw_blue = '#0082D1'
htw_blue_lighter = '#6BB8E6'
htw_orange = '#FF5F00'
htw_orange_lighter = '#FF9900'
htw_grey = '#AFAFAF'
htw_yellow = '#FDDA0D'
htw_light_grey = '#3d3d3d'

def main():
    results = {}  # Define results dictionary before the try block to ensure accessibility in case of an error
    try:

        form_data = read_form_data()
        ffpv_area_max = form_data.get('ffpv_area_max', 0)
        apvv_area_max = form_data.get('apvv_area_max', 0)
        apvh_area_max = form_data.get('apvh_area_max', 0)
        wea_area_max = form_data.get('wea_area_max', 0)
        wea_eeg_share = form_data.get('wea_eeg_share', 100)
        wind_euro_share = form_data.get('wind_euro_share', 100)
        rotor_diameter = form_data.get('rotor_diameter', 130)
        system_output = form_data.get('system_output', 4)
        wea_p_max = form_data.get('wea_p_max', 0)
        pv_p_max = form_data.get('pv_p_max', 0)
        apv_ver_p_max = form_data.get('apv_ver_p_max', 0)
        apv_hor_p_max = form_data.get('apv_hor_p_max', 0)
        flaechen_eigentuemer = form_data.get('flaechen_eigentuemer', {})
        levy_rate = form_data.get('levy_rate', 435)
        mun_key_value = form_data.get('mun_key_value', 0.003)
        apvv_mw_ha = 0.35
        apvh_mw_ha = 0.65
        choosen_mun = form_data.get('choosen_mun', 0)
        # standard levy rate if None is given
        if mun_key_value == 0:
            sz_ghm = 0.3
        else:
            sz_ghm = mun_key_value * 100

        # standard mun value key if None is given
        if levy_rate == 0:
            hebesatz = 4.35
        else:
            hebesatz = levy_rate / 100

        # if no area for eeg or wind-euro is given, set to 100%
        if wea_eeg_share == 0:
            wea_eeg_share = 1
        else:
            wea_eeg_share = wea_eeg_share / 100
        if wind_euro_share == 0:
            wind_euro_share = 1
        else:
            wind_euro_share = wind_euro_share / 100

        # Calculate max. power if only area is given
        if wea_p_max == 0 and wea_area_max != 0:
            A_wea = (np.pi * rotor_diameter * 5 * rotor_diameter * 3)/5
            N_wea = round((wea_area_max * 10000) / A_wea)
            wea_p_max = system_output * N_wea
        else:
            wea_p_max = wea_p_max
        if pv_p_max == 0 and ffpv_area_max != 0:
            pv_p_max = ffpv_area_max
        else:
            pv_p_max = pv_p_max
        if apv_ver_p_max == 0 and apvv_area_max != 0:
            apv_ver_p_max = apvv_area_max * apvv_mw_ha
        else:
            apv_ver_p_max = apv_ver_p_max
        if apv_hor_p_max == 0 and apvh_area_max != 0:
            apv_hor_p_max = apvh_area_max * apvh_mw_ha
        else:
            apv_hor_p_max = apv_hor_p_max

        # Calculate area if only power is given
        if wea_area_max == 0 and wea_p_max != 0:
            A_wea = (np.pi * rotor_diameter * 5 * rotor_diameter * 3)/5
            N_wea = round(wea_p_max / system_output)
            wea_area_max = (A_wea * N_wea) / 10000
        else:
            wea_area_max = wea_area_max
        if ffpv_area_max == 0 and pv_p_max != 0:
            ffpv_area_max = pv_p_max
        else:
            ffpv_area_max = ffpv_area_max
        if apvv_area_max == 0 and apv_ver_p_max != 0:
            apvv_area_max = apv_ver_p_max / apvv_mw_ha
        else:
            apvv_area_max = apvv_area_max
        if apvh_area_max == 0 and apv_hor_p_max != 0:
            apvh_area_max = apv_hor_p_max / apvh_mw_ha
        else:
            apvh_area_max = apvh_area_max
        # invest costs for tec depending on power of tec
        if system_output < 4:
            wea_invest_cost = 1846000
        elif system_output < 5:
            wea_invest_cost = 1676000
        elif system_output < 6:
            wea_invest_cost = 1556000
        else:
            wea_invest_cost = 1561000

        if pv_p_max == 1:
            ffpv_invest_costs = 840000
        elif pv_p_max < 2:
            ffpv_invest_costs = 800000
        elif pv_p_max < 5:
            ffpv_invest_costs = 770000
        else:
            ffpv_invest_costs = 750000

        if apv_ver_p_max == 1:
            apvv_invest_costs = 840000*1.108
        elif apv_ver_p_max < 2:
            apvv_invest_costs = 800000*1.108
        elif apv_ver_p_max < 5:
            apvv_invest_costs = 770000*1.108
        else:
            apvv_invest_costs = 750000*1.108

        if apv_hor_p_max == 1:
            apvh_invest_costs = 840000*1.26
        elif apv_hor_p_max < 2:
            apvh_invest_costs = 800000*1.26
        elif apv_hor_p_max < 5:
            apvh_invest_costs = 770000*1.26
        else:
            apvh_invest_costs = 750000*1.26

        # read feed-in profiles
        wind_profile = pd.read_csv(SEQUENCES_DIR / 'wind-onshore_profile.csv', delimiter=';')
        agri_pv_hor_profile = pd.read_csv(SEQUENCES_DIR / 'agri-pv_hor_ground_profile.csv', header=0, delimiter=';')
        agri_pv_ver_profile = pd.read_csv(SEQUENCES_DIR / 'agri-pv_ver_ground_profile.csv', header=0, delimiter=';')
        ff_pv_profile = pd.read_csv(SEQUENCES_DIR / 'solar-pv_ground_profile.csv', delimiter=';')


        '''
        MUN INCOME FROM LEASES
        '''
        def calc_tax_income(taxable_income):
            income = int(taxable_income)

            if income <= 11604:
                taxes = 0
            elif income <= 17005:
                y = (income - 11604) / 10000
                taxes = round((922.98 * y + 1400) * y)
            elif income <= 66760:
                z = (income - 17005) / 10000
                taxes = round((181.19 * z + 2397) * z + 1025.38)
            elif income <= 277825:
                taxes = round(0.42 * income - 10602.13)
            else:
                taxes = round(0.45 * income - 18936.88)

            return taxes

        gewerbesteuer_income = (income_betriebe_bb - freibetrag) * steuermessbetrag * hebesatz
        gewerbesteuer_income_wea = (income_betriebe_bb) * steuermessbetrag * hebesatz

        est_income = calc_tax_income(year_income)

        def process_area(freibetrag, max_area, ownertype, area_share, area_costs, income_betriebe_bb, steuermessbetrag,
                         hebesatz, gewerbesteuer_income, year_income, est_income, ekst_bb, sz_ghm):
            area_share = area_share / 100  # Convert to decimal if percentage is given
            if ownertype == 'Gewerbliches Eigentum':
                area_gewst = int(((((max_area * area_costs * area_share) + income_betriebe_bb - freibetrag)
                                   * steuermessbetrag * hebesatz) - gewerbesteuer_income))
                area_gewst_total = area_gewst - int(
                    (((max_area * area_share * area_costs) * steuermessbetrag / hebesatz) * 0.35))
                area_income = 0
                ghm_est_income = 0
            elif ownertype == 'Privateigentum':
                area_income_max = area_costs * (max_area * area_share) + year_income
                taxes_list = []
                for income in [area_income_max]:  # List for comprehension
                    taxes = calc_tax_income(income)
                    taxes_list.append(taxes - est_income)
                ghm_est_income = taxes_list[0] * ekst_bb * sz_ghm
                area_gewst_total = 0
                area_income = 0
            elif ownertype == 'Gemeindeeigentum':
                area_income = area_costs * max_area * area_share
                area_gewst_total = 0
                ghm_est_income = 0
            else:
                area_income = 0
                area_gewst_total = 0
                ghm_est_income = 0
            return area_income, area_gewst_total, ghm_est_income

        # Variables to accumulate the results
        apvh_area_income = apvh_area_gewst_total = ghm_est_income_apvh = 0
        apvv_area_income = apvv_area_gewst_total = ghm_est_income_apvv = 0
        pv_area_income = pv_area_gewst_total = ghm_est_income_pv = 0
        wea_area_income = wea_area_gewst_total = ghm_est_income_wea = 0

        # Processing each ownertype for each category
        for apvh_eigentuemer in flaechen_eigentuemer['apvh']:
            eigentuemer_input_apvh = (
                freibetrag, apvh_area_max, apvh_eigentuemer['ownertype'], apvh_eigentuemer['area_share'], apv_area_costs,
                income_betriebe_bb, steuermessbetrag, hebesatz, gewerbesteuer_income, year_income, est_income,
                ekst_bb,
                sz_ghm
            )
            area_income, area_gewst_total, ghm_est_income = process_area(*eigentuemer_input_apvh)
            apvh_area_income += area_income
            apvh_area_gewst_total += area_gewst_total
            ghm_est_income_apvh += ghm_est_income

        for apvv_eigentuemer in flaechen_eigentuemer['apvv']:
            eigentuemer_input_apvv = (
                freibetrag, apvv_area_max, apvv_eigentuemer['ownertype'], apvv_eigentuemer['area_share'], apv_area_costs,
                income_betriebe_bb, steuermessbetrag, hebesatz, gewerbesteuer_income, year_income, est_income,
                ekst_bb,
                sz_ghm
            )
            area_income, area_gewst_total, ghm_est_income = process_area(*eigentuemer_input_apvv)
            apvv_area_income += area_income
            apvv_area_gewst_total += area_gewst_total
            ghm_est_income_apvv += ghm_est_income

        for pv_eigentuemer in flaechen_eigentuemer['pv']:
            eigentuemer_input_pv = (
                freibetrag, ffpv_area_max, pv_eigentuemer['ownertype'], pv_eigentuemer['area_share'], pv_area_costs,
                income_betriebe_bb, steuermessbetrag, hebesatz, gewerbesteuer_income, year_income, est_income,
                ekst_bb,
                sz_ghm
            )
            area_income, area_gewst_total, ghm_est_income = process_area(*eigentuemer_input_pv)
            pv_area_income += area_income
            pv_area_gewst_total += area_gewst_total
            ghm_est_income_pv += ghm_est_income

        for wea_eigentuemer in flaechen_eigentuemer['wea']:
            eigentuemer_input_wea = (
                0, wea_p_max, wea_eigentuemer['ownertype'], wea_eigentuemer['area_share'], wea_area_costs,
                income_betriebe_bb, steuermessbetrag, hebesatz, gewerbesteuer_income_wea, year_income, est_income,
                ekst_bb,
                sz_ghm
            )
            area_income, area_gewst_total, ghm_est_income = process_area(*eigentuemer_input_wea)
            wea_area_income += area_income
            wea_area_gewst_total += area_gewst_total
            ghm_est_income_wea += ghm_est_income

        area_costs_yearly = [wea_area_income, pv_area_income, apvh_area_income + apvv_area_income]
        area_gewst_yearly = [wea_area_gewst_total, pv_area_gewst_total, apvh_area_gewst_total + apvv_area_gewst_total]
        area_est_yearly = [ghm_est_income_wea, ghm_est_income_pv, ghm_est_income_apvh + ghm_est_income_apvv]

        '''
        EEG participation
        '''
        wind_eeg_yearly = ((np.array(wind_profile['GHM-wind-onshore-profile']) * wea_p_max) * eeg_beteiligung).sum() * wea_eeg_share
        pv_eeg_yearly = ((ff_pv_profile['GHM-solar-pv_ground-profile'] * pv_p_max) * eeg_beteiligung).sum()
        apv_eeg_yearly = (((agri_pv_ver_profile['GHM-agri-pv_ver_ground-profile'] * apv_ver_p_max) + (
                    agri_pv_hor_profile['GHM-agri-pv_hor_ground-profile'] * apv_hor_p_max)) * eeg_beteiligung).sum()


        # performance degradation
        degradation_pv = 0.005
        degradation_wind = 0.006

        def calculate_degraded_sum(initial_value, degradation_rate, years=25):
            total = 0
            yearly_eeg = []

            for year in range(1, years + 1):
                degraded_value = initial_value * (1 - degradation_rate) ** year
                total += degraded_value
                yearly_eeg.append(degraded_value)

            return total, yearly_eeg

        iterations = 25


        '''
        Special Regulation BB - Wind-/Solar-Euro
        '''

        wind_sr_bb_yearly = (wea_p_max * bb_euro_mw_wind) * wind_euro_share
        pv_sr_bb_yearly = pv_p_max * bb_euro_mw_pv
        apv_sr_bb_yearly = (apv_ver_p_max + apv_hor_p_max) * bb_euro_mw_pv


        '''
         INVESTMENT COSTS
         '''

        def calculate_profit_year(title, eeg_anteil_gemeinde, investitionskosten, fremdkapitalanteil, zinshoehe,
                                  tilgungsdauer, jaehrliche_betriebskosten_ersten_10_jahre,
                                  jaehrliche_betriebskosten_ab_11_jahr, erzeugte_energiemenge, preis_pro_mengeneinheit,
                                  steuermessbetrag, hebesatz, freibetrag, tilgungsfreie_jahre, jaehrliche_abschreibung,
                                  abschreibungs_dauer, degradation, initial_loss_carryforward=0):
            # Initiale Calculation
            fremdkapital = investitionskosten * fremdkapitalanteil

            if tilgungsfreie_jahre == 1:
                zinsen_jahr_1 = fremdkapital * zinshoehe
                restschuld = fremdkapital
                jaehrliche_tilgung = restschuld / (tilgungsdauer - 2)

            else:
                restschuld = fremdkapital
                jaehrliche_tilgung = restschuld / tilgungsdauer

            kumulierte_kosten = 0
            kumulierte_einnahmen = 0
            kumulierte_jahresgewinne = 0
            jahr = 0
            jahresgewinne = []
            gewerbesteuer_tot = []
            gewerbesteuer = []
            gewinn_start_jahr = None
            total_loss_carryforward = initial_loss_carryforward

            for jahr in range(1, 26):  # Year 1 to 25
                if jahr <= 10:
                    jaehrliche_betriebskosten = jaehrliche_betriebskosten_ersten_10_jahre
                else:
                    jaehrliche_betriebskosten = jaehrliche_betriebskosten_ab_11_jahr

                if jahr > abschreibungs_dauer:
                    jaehrliche_abschreibung = 0

                if jahr == 1:
                    jahresenergieertrag = erzeugte_energiemenge
                    eeg_jahrebetrag = eeg_anteil_gemeinde
                else:
                    jahresenergieertrag = erzeugte_energiemenge * ((1 - degradation) ** jahr)
                    eeg_jahrebetrag = eeg_anteil_gemeinde * ((1 - degradation) ** jahr)

                if jahr == 1 and tilgungsfreie_jahre == 1:
                    jaehrliche_zinsen = zinsen_jahr_1
                    tilgung = 0
                    jahreskosten = jaehrliche_betriebskosten + jaehrliche_zinsen + eeg_jahrebetrag
                elif jahr == 2 and tilgungsfreie_jahre == 1:
                    jaehrliche_zinsen = zinsen_jahr_1
                    tilgung = 0
                    jahreskosten = jaehrliche_betriebskosten + jaehrliche_zinsen + eeg_jahrebetrag
                else:
                    jaehrliche_zinsen = restschuld * zinshoehe
                    tilgung = min(jaehrliche_tilgung, restschuld)
                    restschuld = max(0, restschuld - tilgung)
                    jahreskosten = jaehrliche_betriebskosten + eeg_jahrebetrag + jaehrliche_zinsen

                kumulierte_kosten += jahreskosten
                jaehrliche_einnahmen = jahresenergieertrag * preis_pro_mengeneinheit

                if jaehrliche_einnahmen > 0:
                    kumulierte_einnahmen += jaehrliche_einnahmen

                if jahr <= 2:
                    jaehrlicher_gewinn = jaehrliche_einnahmen - jahreskosten - jaehrliche_abschreibung
                else:
                    jaehrlicher_gewinn = jaehrliche_einnahmen - jahreskosten - jaehrliche_abschreibung

                kumulierte_jahresgewinne += jaehrlicher_gewinn

                if jaehrlicher_gewinn < 0:
                    total_loss_carryforward += -jaehrlicher_gewinn
                    adjusted_profit = 0
                else:
                    adjusted_profit = jaehrlicher_gewinn

                    if total_loss_carryforward > 0 and adjusted_profit > 0:
                        # Deduct up to 1 million loss
                        subtracted_loss = min(1_000_000, adjusted_profit, total_loss_carryforward)
                        adjusted_profit -= subtracted_loss
                        total_loss_carryforward -= subtracted_loss

                        # Deduct 60% of the remaining profit
                        if total_loss_carryforward > 0 and total_loss_carryforward > (adjusted_profit * 0.6):
                            extra_loss = adjusted_profit * 0.6
                            total_loss_carryforward -= extra_loss
                            adjusted_profit *= 0.4
                        elif total_loss_carryforward > 0 and total_loss_carryforward < (adjusted_profit * 0.6):
                            extra_loss = total_loss_carryforward
                            total_loss_carryforward -= extra_loss
                            adjusted_profit -= extra_loss

                jahresgewinne.append((jahr, adjusted_profit))

                if adjusted_profit > 0:
                    gewerbesteuer_tot_value = ((adjusted_profit * 0.9) - freibetrag) * steuermessbetrag * hebesatz
                    gewerbesteuer_value = gewerbesteuer_tot_value - (
                            (((adjusted_profit * 0.9) - freibetrag) * steuermessbetrag) * 0.35)
                else:
                    gewerbesteuer_tot_value = 0
                    gewerbesteuer_value = 0

                gewerbesteuer_tot.append((jahr, gewerbesteuer_tot_value))
                gewerbesteuer.append((jahr, gewerbesteuer_value))

                if jaehrlicher_gewinn > 0 and jahr >= 3:
                    if gewinn_start_jahr is None:
                        gewinn_start_jahr = jahr

            return (
                gewinn_start_jahr if gewinn_start_jahr is not None else "kein Gewinn"), jahresgewinne, gewerbesteuer, kumulierte_jahresgewinne

        def run_scenario(params, results):

            berechnete_mw = params.get("berechnete_mw", 0)
            genehmigte_anlagen = params.get("genehmigte_anlagen", 0)
            eeg_beteiligung = params.get("eeg_beteiligung", 0)
            profil = params.get("profil", pd.Series([0]))
            investitionskosten = params.get("investitionskosten", 0)
            betriebskosten10 = params.get("betriebskosten10", 0)
            betriebskosten20 = params.get("betriebskosten20", 0)
            sr_bb_euro = params.get("sr_bb_euro", 0)
            erzeugte_energiemenge = params.get("erzeugte_energiemenge", 0)
            preis_pro_mengeneinheit = params.get("preis_pro_mengeneinheit", 0)
            tilgungsfreie_jahre = params.get("tilgungsfreie_jahre", 0)
            degradation = params.get("degradation", 0)
            title = params.get("title", "Unknown Scenario")

            wind_euro_2026 = berechnete_mw - genehmigte_anlagen if genehmigte_anlagen < berechnete_mw else 0
            investitionskosten = investitionskosten * berechnete_mw
            fremdkapitalanteil = params.get("fremdkapitalanteil", 0.8)  # Standard 80%
            zinshoehe = params.get("zinshoehe", 0.05)  # Standard 5%
            tilgungsdauer = params.get("tilgungsdauer", 15)
            freibetrag = params.get("freibetrag", 0)
            abschreibungs_dauer = params.get("abschreibungs_dauer", 0)
            if choosen_mun != 0:
                sr_bb_euro = wind_euro_2026 * sr_bb_euro + ((genehmigte_anlagen / 6) * 10000)
            else:
                sr_bb_euro = 0
            eeg_anteil_gemeinde = ((profil * berechnete_mw) * eeg_beteiligung).sum()
            jaehrliche_betriebskosten_ersten_10_jahre = betriebskosten10 * berechnete_mw + sr_bb_euro
            jaehrliche_betriebskosten_ab_11_jahr = betriebskosten20 * berechnete_mw + sr_bb_euro
            erzeugte_energiemenge = erzeugte_energiemenge * berechnete_mw
            preis_pro_mengeneinheit = preis_pro_mengeneinheit  # Preis pro kWh in €
            tilgungsfreie_jahre = tilgungsfreie_jahre
            if abschreibungs_dauer != 0:
                jaehrliche_abschreibung = investitionskosten / abschreibungs_dauer
            else:
                jaehrliche_abschreibung = 0
            profit_year, jahresgewinne, gewerbesteuer, kumulierte_jahresgewinne = calculate_profit_year(title,
                                                                                                        eeg_anteil_gemeinde,
                                                                                                        investitionskosten,
                                                                                                        fremdkapitalanteil,
                                                                                                        zinshoehe,
                                                                                                        tilgungsdauer,
                                                                                                        jaehrliche_betriebskosten_ersten_10_jahre,
                                                                                                        jaehrliche_betriebskosten_ab_11_jahr,
                                                                                                        erzeugte_energiemenge,
                                                                                                        preis_pro_mengeneinheit,
                                                                                                        steuermessbetrag,
                                                                                                        hebesatz,
                                                                                                        freibetrag,
                                                                                                        tilgungsfreie_jahre,
                                                                                                        jaehrliche_abschreibung,
                                                                                                        abschreibungs_dauer,
                                                                                                        degradation)

            # Saving the trade tax in the result dictionary
            results[params["name"]] = gewerbesteuer

        # Save trade tax results for different scenarios
        gewerbesteuer_results = {}

        # Defining scenarios
        szenarien = [  # Wind 100%
            {"berechnete_mw": wea_p_max, "erzeugte_energiemenge": 2550000,
             "preis_pro_mengeneinheit": 0.0828, "eeg_beteiligung": 2,
             "profil": wind_profile['GHM-wind-onshore-profile'], "sr_bb_euro": 5000,
             "investitionskosten": wea_invest_cost,
             "betriebskosten10": 44000, "betriebskosten20": 53000, "fremdkapitalanteil": 0.8, "zinshoehe": 0.05,
             "tilgungsdauer": 15, "title": "Gewerbesteuer der WEA",
             "filename": "komm-wert-gwst-anlagenbetreibende-wind100.png", "bar_color": htw_orange, "freibetrag": 0, "tilgungsfreie_jahre": 1,
             "name": 'Wind100', "abschreibungs_dauer": 16, "degradation": 0.006},  # FF-PV 100%
            {"berechnete_mw": pv_p_max, "genehmigte_anlagen": 0, "erzeugte_energiemenge": 1000000,
             "preis_pro_mengeneinheit": 0.073, "eeg_beteiligung": 2,
             "profil": ff_pv_profile['GHM-solar-pv_ground-profile'], "sr_bb_euro": 2000, "investitionskosten": ffpv_invest_costs,
             "betriebskosten10": 14300, "betriebskosten20": 14300, "fremdkapitalanteil": 0.8, "zinshoehe": 0.03,
             "tilgungsdauer": 15, "title": "Gewerbesteuer der FF-PV",
             "filename": "komm-wert-gwst-anlagenbetreibende-ff-pv-100.png", "bar_color": htw_green, "freibetrag": 24500,
             "tilgungsfreie_jahre": 1, "name": 'FFPV100', "abschreibungs_dauer": 20, "degradation": 0.005},
            # Agri-PV hor. 100%
            {"berechnete_mw": apv_hor_p_max, "genehmigte_anlagen": 0, "erzeugte_energiemenge": apvh_invest_costs,
             "preis_pro_mengeneinheit": 0.088, "eeg_beteiligung": 2,
             "profil": agri_pv_hor_profile['GHM-agri-pv_hor_ground-profile'], "sr_bb_euro": 2000,
             "investitionskosten": 945000, "betriebskosten10": 12870, "betriebskosten20": 12870,
             "fremdkapitalanteil": 0.8, "zinshoehe": 0.03, "tilgungsdauer": 15,
             "title": "Max. Gewerbesteuer der Agri-PV-Anlagen (hor.)",
             "filename": "komm-wert-gwst-anlagenbetreibende-agri-pv-hor-1.png", "bar_color": htw_blue, "freibetrag": 24500,
             "tilgungsfreie_jahre": 1, "name": 'APVH100', "abschreibungs_dauer": 20, "degradation": 0.005},
            # Agri-PV ver. 100%
            {"berechnete_mw": apv_ver_p_max, "genehmigte_anlagen": 0, "erzeugte_energiemenge": apvv_invest_costs,
             "preis_pro_mengeneinheit": 0.088, "eeg_beteiligung": 2,
             "profil": agri_pv_ver_profile['GHM-agri-pv_ver_ground-profile'], "sr_bb_euro": 2000,
             "investitionskosten": 831000, "betriebskosten10": 11440, "betriebskosten20": 11440,
             "fremdkapitalanteil": 0.8, "zinshoehe": 0.03, "tilgungsdauer": 15,
             "title": "Max. Gewerbesteuer der Agri-PV-Anlagen (ver.)",
             "filename": "komm-wert-gwst-anlagenbetreibende-agri-pv-ver-1.png", "bar_color": htw_blue, "freibetrag": 24500,
             "tilgungsfreie_jahre": 1, "name": 'APVV100', "abschreibungs_dauer": 20, "degradation": 0.005},
        ]
        for szenario in szenarien:
            run_scenario(szenario, gewerbesteuer_results)

        szenariennamen_fuer_summe_1 = ["FFPV100"]
        szenariennamen_fuer_summe_2 = ["APVV100", "APVH100"]
        szenariennamen_fuer_summe_3 = ["Wind100"]

        # finding maximum annual trade tax
        def max_annual_sum(gewerbesteuer_results, szenariennamen_fuer_summe):
            summierte_steuern = [0] * 25

            # Sum up the trade tax per year across the specific scenarios
            for jahr in range(1, 26):
                for szenarioname in szenariennamen_fuer_summe:
                    for j, steuer in gewerbesteuer_results[szenarioname]:
                        if j == jahr:
                            summierte_steuern[jahr - 1] += steuer

            # Find the maximum value of the total trade tax per year
            max_steuer = max(summierte_steuern)
            return max_steuer

        max_steuer_1 = max_annual_sum(gewerbesteuer_results, szenariennamen_fuer_summe_1)
        max_steuer_2 = max_annual_sum(gewerbesteuer_results, szenariennamen_fuer_summe_2)
        max_steuer_3 = max_annual_sum(gewerbesteuer_results, szenariennamen_fuer_summe_3)

        # total trade tax over 25 years
        gesamt_gewerbesteuer_1 = sum(
            sum(jahressteuer for jahr, jahressteuer in gewerbesteuer_results[szenarioname] if jahressteuer > 0) for
            szenarioname in szenariennamen_fuer_summe_1)

        gesamt_gewerbesteuer_2 = sum(
            sum(jahressteuer for jahr, jahressteuer in gewerbesteuer_results[szenarioname] if jahressteuer > 0) for
            szenarioname in szenariennamen_fuer_summe_2)
        gesamt_gewerbesteuer_3 = sum(
            sum(jahressteuer for jahr, jahressteuer in gewerbesteuer_results[szenarioname] if jahressteuer > 0) for
            szenarioname in szenariennamen_fuer_summe_3)

        try:

            # FF-PV
            create_echarts_data_gewerbesteuer(gewerbesteuer_results['FFPV100'], 25,
                                              "gewerbesteuer_ff_pv.json",
                                              "FF-PV", av_blue)

            # WEA
            create_echarts_data_gewerbesteuer(gewerbesteuer_results['Wind100'], 25,
                                              "gewerbesteuer_wind.json",
                                              "WEA", av_red)
            # APV
            apv_combined = []
            for year in range(1, 26):
                apv_value = sum(gewerbesteuer_results[name][year - 1][1] for name in szenariennamen_fuer_summe_2)
                apv_combined.append((year, apv_value))

            create_echarts_data_gewerbesteuer(apv_combined, 25,
                                              "gewerbesteuer_agri_pv.json",
                                              "APV", av_green)

        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Gewerbesteuer-Charts: {str(e)}")

        '''
        ALL MUN INCOME FOR 25 YEARS
        '''

        wind_eeg_degradation_result, wind_eeg_degradation_yearly = calculate_degraded_sum(wind_eeg_yearly,
                                                                                          degradation_wind, iterations)
        pv_eeg_degradation_result, pv_eeg_degradation_yearly = calculate_degraded_sum(pv_eeg_yearly, degradation_pv,
                                                                                      iterations)
        apv_eeg_degradation_result, apv_eeg_degradation_yearly = calculate_degraded_sum(apv_eeg_yearly, degradation_pv,
                                                                                        iterations)

        years = 25
        gewerbesteuer_anlagen = [gesamt_gewerbesteuer_3, gesamt_gewerbesteuer_1,
                                 gesamt_gewerbesteuer_2]
        eeg_einnahmen = [wind_eeg_degradation_result, pv_eeg_degradation_result, apv_eeg_degradation_result]
        sr_bb_einnahmen = [wind_sr_bb_yearly * years, pv_sr_bb_yearly * years, apv_sr_bb_yearly * years]

        area_costs_total = np.array(area_costs_yearly) * years
        area_gewst_total = np.array(area_gewst_yearly) * years
        area_est_total = np.array(area_est_yearly) * years

        sum_wea = gesamt_gewerbesteuer_3 + wind_eeg_degradation_result + wind_sr_bb_yearly * years + area_costs_total[0] + area_gewst_total[0] + area_est_total[0]
        sum_ff_pv = gesamt_gewerbesteuer_1 + pv_eeg_degradation_result + pv_sr_bb_yearly * years  + area_costs_total[1] + area_gewst_total[1] + area_est_total[1]
        sum_agri_pv = gesamt_gewerbesteuer_2 + apv_eeg_degradation_result + apv_sr_bb_yearly * years + area_costs_total[2] + area_gewst_total[2] + area_est_total[2]
        sum_wea_plot = [0, 0, 0, sum_wea, 0, 0]
        sum_agri_pv_plot = [0, 0, 0, 0, 0, sum_agri_pv]
        sum_ff_pv_plot = [0, 0, 0, 0, sum_ff_pv, 0]
        create_echarts_data_pachteinnahmen(area_costs_yearly, area_est_yearly, area_gewst_yearly)
        create_echarts_data_eeg(wind_eeg_yearly, pv_eeg_yearly, apv_eeg_yearly)
        create_echarts_data_srbb(wind_sr_bb_yearly, pv_sr_bb_yearly, apv_sr_bb_yearly)
        create_echarts_data_pachteinnahmen(area_costs_yearly, area_est_yearly, area_gewst_yearly)

        create_echarts_data_gesamteinnahmen(gewerbesteuer_anlagen, eeg_einnahmen, sr_bb_einnahmen,
                                            area_costs_total.tolist(), area_gewst_total.tolist(),
                                            area_est_total.tolist(), sum_wea_plot, sum_agri_pv_plot, sum_ff_pv_plot)

        # correct format for values diplayed on added_value_results.html
        def format_numbers(value):
            return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

        apv_area_income = apvh_area_income + apvv_area_income
        apv_pacht_est = ghm_est_income_apvh + ghm_est_income_apvv
        apv_pacht_gewst = apvh_area_gewst_total + apvv_area_gewst_total

        wind_eeg_yearly = format_numbers(wind_eeg_yearly)
        pv_eeg_yearly = format_numbers(pv_eeg_yearly)
        apv_eeg_yearly = format_numbers(apv_eeg_yearly)
        wind_sr_bb_yearly = format_numbers(wind_sr_bb_yearly)
        pv_sr_bb_yearly = format_numbers(pv_sr_bb_yearly)
        apv_sr_bb_yearly = format_numbers(apv_sr_bb_yearly)
        wea_area_income = format_numbers(wea_area_income)
        pv_area_income = format_numbers(pv_area_income)
        apv_area_income = format_numbers(apv_area_income)
        ghm_est_income_wea = format_numbers(ghm_est_income_wea)
        ghm_est_income_pv = format_numbers(ghm_est_income_pv)
        apv_pacht_est = format_numbers(apv_pacht_est)
        wea_area_gewst_total = format_numbers(wea_area_gewst_total)
        pv_area_gewst_total = format_numbers(pv_area_gewst_total)
        apv_pacht_gewst = format_numbers(apv_pacht_gewst)
        gesamt_gewerbesteuer_1 = format_numbers(gesamt_gewerbesteuer_1)
        gesamt_gewerbesteuer_2 = format_numbers(gesamt_gewerbesteuer_2)
        gesamt_gewerbesteuer_3 = format_numbers(gesamt_gewerbesteuer_3)
        max_steuer_1 = format_numbers(max_steuer_1)
        max_steuer_2 = format_numbers(max_steuer_2)
        max_steuer_3 = format_numbers(max_steuer_3)
        sum_wea = format_numbers(sum_wea)
        sum_ff_pv = format_numbers(sum_ff_pv)
        sum_agri_pv = format_numbers(sum_agri_pv)
        choosen_mun = format_numbers(choosen_mun)


        results.update({"wind_eeg_yearly": wind_eeg_yearly,
                   "pv_eeg_yearly": pv_eeg_yearly,
                   "apv_eeg_yearly":apv_eeg_yearly,
                      "wind_sr_bb_yearly":  wind_sr_bb_yearly,
                        "pv_sr_bb_yearly": pv_sr_bb_yearly,
                        "apv_sr_bb_yearly": apv_sr_bb_yearly,
                        "gesamt_gewerbesteuer_1": gesamt_gewerbesteuer_1,
                        "gesamt_gewerbesteuer_2": gesamt_gewerbesteuer_2,
                        "gesamt_gewerbesteuer_3": gesamt_gewerbesteuer_3,
                        'wea_pachteinnahmen': wea_area_income,
                        'pv_pachteinnahmen': pv_area_income,
                        'apv_pachteinnahmen': apv_area_income,
                        'wea_pacht_est':ghm_est_income_wea,
                        'pv_pacht_est':ghm_est_income_pv,
                        'apv_pacht_est': apv_pacht_est,
                        'wea_pacht_gewst': wea_area_gewst_total,
                        'pv_pacht_gewst': pv_area_gewst_total,
                        'apv_pacht_gewst': apv_pacht_gewst,
                        'max_steuer_1': max_steuer_1,
                        'max_steuer_2': max_steuer_2,
                        'max_steuer_3': max_steuer_3,
                        'sum_wea': sum_wea,
                        'sum_ff_pv': sum_ff_pv,
                        'sum_agri_pv': sum_agri_pv,
                        'choosen_mun': choosen_mun,
                        })

        try:
            json_output = json.dumps(results)
            print(json_output)
        except (TypeError, ValueError) as e:
            print(json.dumps({"status": "error", "message": "Invalid JSON output"}))
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
