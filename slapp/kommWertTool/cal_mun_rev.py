import pandas as pd
import numpy as np
import csv
import sys
import json
import time
from pathlib import Path
import logging
from datetime import datetime


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CURRENT_DIR = Path(__file__).resolve().parent

# ----------- GLOBAL PARAMETERS ----------- #
with open(CURRENT_DIR / 'underlying-data-added-value-calc.json', 'r') as file:
    underlying_data = json.load(file)

# access to underlying data
wind = underlying_data['wind']
apvh = underlying_data['apvh']
apvv = underlying_data['apvv']
apv_general = underlying_data['apv_general']
ffpv = underlying_data['ff-pv']
colors = underlying_data['colors']
ekst = underlying_data['ekst']
gewst = underlying_data['gewst']
eeg_participation = underlying_data['eeg_participation']
bb_euro_mw = underlying_data['bb_euro_mw']
electricity_price = underlying_data['average_electricity_price']
property_tax_a = underlying_data['property_tax_a']

# taxes
mun_ekst_share = ekst['mun_ekst_share']
annual_income = ekst['annual_income'] # average annual income in DE in €
tax_assesment_amount = gewst['tax_assesment_amount'] # fix for DE (Steuermessbetrag)
average_business_income = gewst['average_business_income'] # annual income of businesses
# area costs per ha
pv_area_costs = ffpv['area_costs'] # €/ha
apv_area_costs = apv_general['area_costs'] # €/ha
wea_area_costs = wind['area_costs'] # € / MW
# invest costs per mw
wea_invest_cost = wind['invest_cost'] # €/ha
ffpv_invest_costs = ffpv['invest_cost'] # €/ha
apvh_invest_costs = apvh['invest_cost'] # €/ha
apvv_invest_costs = apvv['invest_cost'] # €/ha
apvv_mw_ha = apvv['mw_ha']
apvh_mw_ha = apvh['mw_ha']
current_year = datetime.now().year

# ----------- CREATE CHARTS ----------- #
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
                    "color": colors['grey']  # Beispiel: grün
                }
            },
            {
                "name": "Komm. ESt-Anteil",
                "type": "bar",
                "data": area_est_yearly,
                "itemStyle": {
                    "color": colors['light_grey']  # Beispiel: blau
                }
            },
            {
                "name": "Komm. GewSt-Anteil",
                "type": "bar",
                "data": area_gewst_yearly,
                "itemStyle": {
                    "color": colors['yellow']  # Beispiel: orange
                }
            }
        ]
    }
    return(echarts_data, f"pachteinnahmen.json")

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
                    "color": colors['red']}, "data": [wind_eeg_yearly]},  # Wert als Liste
            {"name": "FF-PV", "type": "bar", "itemStyle": {
                    "color": colors['blue']}, "data": [pv_eeg_yearly]},  # Wert als Liste
            {"name": "APV", "type": "bar", "itemStyle": {
                    "color": colors['green']}, "data": [apv_eeg_yearly]}   # Wert als Liste
        ]
    }
    return(echarts_data, f"eeg_participation.json")


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
            "name": "Gewerbesteuer",
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

    return(echarts_data, filename)

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
                    "color": colors['red']}, "data": [wind_sr_bb_yearly]},  # Wert als Liste
            {"name": "FF-PV", "type": "bar", "itemStyle": {
                    "color": colors['blue']}, "data": [pv_sr_bb_yearly]},  # Wert als Liste
            {"name": "APV", "type": "bar", "itemStyle": {
                    "color": colors['green']}, "data": [apv_sr_bb_yearly]}   # Wert als Liste
        ]
    }
    return(echarts_data_sr, f"wind_solar_euro.json")
def create_echarts_data_total_mun_income(trade_tax_plant, eeg_income, sr_bb_income,
                                        area_costs_total, area_gewst_total, area_est_total, sum_wea_plot, sum_agri_pv_plot, sum_ff_pv_plot, property_tax):
    legend_data = []
    series_data = []
    def add_series(name, data, yAxisIndex=0):
        if any(value > 0 for value in data):
            series_data.append({"name": name, "type": "bar", "data": data, "yAxisIndex": yAxisIndex})
        if yAxisIndex == 0 and any(value > 0 for value in data):
            legend_data.append(name)


    add_series("GewSt.-Einnahmen Anlagengewinne", trade_tax_plant)
    add_series("EEG-Beteiligung", eeg_income)
    add_series("Wind-/Solar-Euro", sr_bb_income)
    add_series("Direkte Pachteinnahmen", area_costs_total)
    add_series("GewSt.-Einnahmen Pacht", area_gewst_total)
    add_series("ESt.-Einnahmen Pacht", area_est_total)
    add_series("Grundsteuer A", property_tax)
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
                "name": "Einnahmen",
                "axisLabel": {
                    "formatter": "{value}".replace(",", ".")
                },
                "splitNumber": 5
            },
            {
                "type": "value",
                "name": "Gesamteinnahmen",
                "axisLabel": {
                    "formatter": "{value}".replace(",", ".")
                },
                "position": "right",
                "splitNumber": 5
            }
        ],
        "series": [
            {"name": "GewSt.-Einnahmen Anlagengewinne", "type": "bar", "itemStyle": {"color": colors['blue_lighter']}, "data": trade_tax_plant},
            {"name": "EEG-Beteiligung", "type": "bar", "itemStyle": {"color": colors['green_darker']}, "data": eeg_income},
            {"name": "Wind-/Solar-Euro", "itemStyle": {"color": colors['orange']}, "type": "bar", "data": sr_bb_income},
            {"name": "Direkte Pachteinnahmen", "type": "bar", "itemStyle": {"color": colors['grey']}, "data": area_costs_total},
            {"name": "GewSt.-Einnahmen Pacht", "type": "bar", "itemStyle": {"color": colors['yellow']}, "data": area_gewst_total},
            {"name": "ESt.-Einnahmen Pacht", "type": "bar", "itemStyle": {"color": colors['light_grey']}, "data": area_est_total},
            {"name": "Grundsteuer A", "type": "bar", "itemStyle": {"color": colors['light_green']}, "data": property_tax},
            {"name": "Gesamteinnahmen WEA", "type": "bar", "itemStyle": {"color": colors['red']}, "data": sum_wea_plot, "yAxisIndex": 1},
            {"name": "Gesamteinnahmen FF-PV", "type": "bar", "itemStyle": {"color": colors['blue']}, "data": sum_ff_pv_plot, "yAxisIndex": 1},
            {"name": "Gesamteinnahmen APV", "type": "bar", "itemStyle": {"color": colors['green']}, "data": sum_agri_pv_plot, "yAxisIndex": 1},
        ],
    }
    return(echarts_data, f"gesamteinnahmen.json")

def main(form_data):
    results = {}  # Define results dictionary before the try block to ensure accessibility in case of an error

    def process_form_data(form_data):
        data = {}
        try:

            # Processing of area owners based on the entries
            area_ownertype = {
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

                if wea_ownertype_key in form_data and form_data[wea_ownertype_key]:
                    ownertype = {
                        'ownertype': form_data.get(wea_ownertype_key, 'default_ownertype'),
                        'area_share': float(form_data.get(wea_area_share_key, 0))
                    }
                    area_ownertype['wea'].append(ownertype)
                    found_any = True

                if apvv_ownertype_key in form_data and form_data[apvv_ownertype_key]:
                    ownertype = {
                        'ownertype': form_data.get(apvv_ownertype_key, 'default_ownertype'),
                        'area_share': float(form_data.get(apvv_area_share_key, 0))  # Convert to float
                    }
                    area_ownertype['apvv'].append(ownertype)
                    found_any = True

                if apvh_ownertype_key in form_data and form_data[apvh_ownertype_key]:
                    ownertype = {
                        'ownertype': form_data.get(apvh_ownertype_key, 'default_ownertype'),
                        'area_share': float(form_data.get(apvh_area_share_key, 0))  # Convert to float
                    }
                    area_ownertype['apvh'].append(ownertype)
                    found_any = True

                if pv_ownertype_key in form_data and form_data[pv_ownertype_key]:
                    ownertype = {
                        'ownertype': form_data.get(pv_ownertype_key, 'default_ownertype'),
                        'area_share': float(form_data.get(pv_area_share_key, 0))  # Convert to float
                    }
                    area_ownertype['pv'].append(ownertype)
                    found_any = True

                if not found_any:
                    break

                counter += 1

            # Add default values for area owners
            default_ownertype = {
                'ownertype': 'Landes-/Bundeseigentum',
                'area_share': 0
            }

            if not area_ownertype['wea']:
                area_ownertype['wea'].append(default_ownertype)
            if not area_ownertype['apvv']:
                area_ownertype['apvv'].append(default_ownertype)
            if not area_ownertype['apvh']:
                area_ownertype['apvh'].append(default_ownertype)
            if not area_ownertype['pv']:
                area_ownertype['pv'].append(default_ownertype)

            # Ensure that the lists are the same length
            max_length = max(len(area_ownertype['wea']), len(area_ownertype['apvv']),
                             len(area_ownertype['apvh']), len(area_ownertype['pv']))
            def extend_list(lst):
                while len(lst) < max_length:
                    lst.append({'ownertype': 'N/A', 'area_share': 0})
                return lst

            area_ownertype['wea'] = extend_list(area_ownertype['wea'])
            area_ownertype['apvv'] = extend_list(area_ownertype['apvv'])
            area_ownertype['apvh'] = extend_list(area_ownertype['apvh'])
            area_ownertype['pv'] = extend_list(area_ownertype['pv'])

            data['area_ownertype'] = area_ownertype
        except Exception as e:
            print(json.dumps({"status": "error", "message": f"Fehler beim Verarbeiten der Formulardaten: {str(e)}"}))
            sys.exit(1)

        return data

    def parse_float(value, default=0.0):
        try:
            # Ersetze Komma durch Punkt und konvertiere zu float
            return float(value.replace(',', '.'))
        except (ValueError, AttributeError):
            return default

    ffpv_area_max = int(form_data.get('ffpv_area_max', 0))
    apvv_area_max = int(form_data.get('apvv_area_max', 0))
    apvh_area_max = int(form_data.get('apvh_area_max', 0))
    wea_area_max = int(form_data.get('wea_area_max', 0))
    wea_eeg_share = int(form_data.get('wea_eeg_share', 100))
    wind_euro_share = int(form_data.get('wind_euro_share', 100))
    rotor_diameter = int(form_data.get('rotor_diameter', 140))
    system_output = int(form_data.get('system_output', 4))
    wea_p_max = int(form_data.get('wea_p_max', 0))
    pv_p_max = int(form_data.get('pv_p_max', 0))
    apv_ver_p_max = int(form_data.get('apv_ver_p_max', 0))
    apv_hor_p_max = int(form_data.get('apv_hor_p_max', 0))
    area_ownertype = process_form_data(form_data).get('area_ownertype', {})
    ownertype = process_form_data(form_data).get('ownertype', {})
    levy_rate = int(form_data.get('levy_rate', 407))
    levy_rate_a = int(form_data.get('levy_rate_a', 310)) / 100
    grassland_number = parse_float(form_data.get('grassland_number'), 30.0) / 100

    mun_key_value = int(form_data.get('mun_key_value', 0.003))

    choosen_mun = form_data.get('choosen_mun', 0)
    check_county = form_data.get('check_county', 'check_county_bb')
    # standard levy rate if None is given
    if mun_key_value == 0:
        mun_key_value = 0.3
    else:
        mun_key_value = mun_key_value * 100

    # standard mun value key if None is given
    if levy_rate == 0:
        levy_rate = 4.07
    else:
        levy_rate = levy_rate / 100

    if levy_rate_a == 0:
        levy_rate_a = 3.1
    else:
        levy_rate_a = levy_rate_a

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
        N_wea = np.floor((wea_area_max * 10000) / A_wea)
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
        N_wea = np.floor(wea_p_max / system_output)
        wea_area_max = (A_wea * N_wea) / 10000
    else:
        wea_area_max = wea_area_max
        A_wea = (np.pi * rotor_diameter * 5 * rotor_diameter * 3)/5
        N_wea = np.floor((wea_area_max * 10000)/A_wea)
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

    # calculate wea area for property_tax
    wea_area_property_tax = N_wea * property_tax_a['wea_area_taxable_ha'] * 10000 # delimited site area of the wind turbines


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

    est_income = calc_tax_income(annual_income) # calculates income tax of average annual income
    def round_down_to_hundred(number):
        return np.floor(number / 100) * 100
    def process_area(max_area, ownertype, area_share, area_costs, tax_assesment_amount,
                     levy_rate, annual_income, est_income, mun_ekst_share, mun_key_value):
        area_share = area_share / 100  # Convert to decimal if percentage is given
        if ownertype == 'Gewerbliches Eigentum':
            area_gewst = int(((max_area * area_costs * area_share)
                               * tax_assesment_amount * levy_rate))
            area_gewst_total = area_gewst - int(
                (((max_area * area_share * area_costs) * tax_assesment_amount / levy_rate) * 0.35))
            area_income = 0
            lease_est_income = 0
            property_tax_a_tot = round_down_to_hundred(
                ((wea_area_property_tax * property_tax_a['valuation_factor_earnings']) +
                 (grassland_number * wea_area_property_tax * property_tax_a['yield_indicator'])) *
                property_tax_a['net_earnings_factor']
            ) * property_tax_a['tax_base'] * levy_rate_a * area_share # calculates property tax with the higher earnings value
        elif ownertype == 'Privateigentum':
            area_income_max = area_costs * (max_area * area_share) + annual_income
            taxes_list = []
            for income in [area_income_max]:  # List for comprehension
                taxes = calc_tax_income(income)
                taxes_list.append(taxes - est_income)
            lease_est_income = taxes_list[0] * mun_ekst_share * mun_key_value
            area_gewst_total = 0
            area_income = 0
            property_tax_a_tot = round_down_to_hundred(
                ((wea_area_property_tax * property_tax_a['valuation_factor_earnings']) +
                 (grassland_number * wea_area_property_tax * property_tax_a['yield_indicator'])) *
                property_tax_a['net_earnings_factor']
            ) * property_tax_a['tax_base'] * levy_rate_a * area_share  # calculates property tax with the higher earnings value
        elif ownertype == 'Gemeindeeigentum':
            area_income = area_costs * max_area * area_share
            area_gewst_total = 0
            lease_est_income = 0
            property_tax_a_tot = 0
        else:
            area_income = 0
            area_gewst_total = 0
            lease_est_income = 0
            property_tax_a_tot = round_down_to_hundred(
                ((wea_area_property_tax * property_tax_a['valuation_factor_earnings']) +
                 (grassland_number * wea_area_property_tax * property_tax_a['yield_indicator'])) *
                property_tax_a['net_earnings_factor']
            ) * property_tax_a['tax_base'] * levy_rate_a * area_share  # calculates property tax with the higher earnings value
        return area_income, area_gewst_total, lease_est_income, property_tax_a_tot

    # Variables to accumulate the results
    apvh_area_income = apvh_area_gewst_total = lease_est_income_apvh = 0
    apvv_area_income = apvv_area_gewst_total = lease_est_income_apvv = 0
    pv_area_income = lease_trade_tax_pv = lease_est_income_pv = 0
    wea_area_income = lease_trade_tax_wea = lease_est_income_wea = 0
    property_tax_a_wea = property_tax_a_tot = 0
    # Processing each ownertype for each category
    if 'apvh' in area_ownertype:
        for apvh_ownertype in area_ownertype['apvh']:
            ownertype_input_apvh = (
                apvh_area_max, apvh_ownertype['ownertype'], apvh_ownertype['area_share'], apv_area_costs,
                tax_assesment_amount, levy_rate, annual_income, est_income, mun_ekst_share, mun_key_value
            )
            area_income, area_gewst_total, lease_est_income, property_tax_a_tot = process_area(*ownertype_input_apvh)
            apvh_area_income += area_income
            apvh_area_gewst_total += area_gewst_total
            lease_est_income_apvh += lease_est_income

    if 'apvv' in area_ownertype:
        for apvv_ownertype in area_ownertype['apvv']:
            ownertype_input_apvv = (
                apvv_area_max, apvv_ownertype['ownertype'], apvv_ownertype['area_share'], apv_area_costs,
                tax_assesment_amount, levy_rate, annual_income, est_income,
                mun_ekst_share, mun_key_value
            )
            area_income, area_gewst_total, lease_est_income, property_tax_a_tot = process_area(*ownertype_input_apvv)
            apvv_area_income += area_income
            apvv_area_gewst_total += area_gewst_total
            lease_est_income_apvv += lease_est_income

    if 'pv' in area_ownertype:
        for pv_ownertype in area_ownertype['pv']:
            ownertype_input_pv = (
                ffpv_area_max, pv_ownertype['ownertype'], pv_ownertype['area_share'], pv_area_costs,
                tax_assesment_amount, levy_rate, annual_income, est_income,
                mun_ekst_share, mun_key_value
            )
            area_income, area_gewst_total, lease_est_income, property_tax_a_tot = process_area(*ownertype_input_pv)
            pv_area_income += area_income
            lease_trade_tax_pv += area_gewst_total
            lease_est_income_pv += lease_est_income

    if 'wea' in area_ownertype:
        for wea_ownertype in area_ownertype['wea']:
            ownertype_input_wea = (
                wea_p_max, wea_ownertype['ownertype'], wea_ownertype['area_share'], wea_area_costs,
                tax_assesment_amount, levy_rate, annual_income, est_income,
                mun_ekst_share,
                mun_key_value
            )
            area_income, area_gewst_total, lease_est_income, property_tax_a_tot = process_area(*ownertype_input_wea)
            property_tax_a_wea += property_tax_a_tot
            wea_area_income += area_income
            lease_trade_tax_wea += area_gewst_total
            lease_est_income_wea += lease_est_income

    area_costs_yearly = [wea_area_income, pv_area_income, apvh_area_income + apvv_area_income]
    area_gewst_yearly = [lease_trade_tax_wea, lease_trade_tax_pv, apvh_area_gewst_total + apvv_area_gewst_total]
    area_est_yearly = [lease_est_income_wea, lease_est_income_pv, lease_est_income_apvh + lease_est_income_apvv]

    '''
    EEG participation
    '''
    wind_eeg_yearly = ((wind['flh'] * wea_p_max) * eeg_participation) * wea_eeg_share
    pv_eeg_yearly = ((ffpv['flh'] * pv_p_max) * eeg_participation)
    apv_eeg_yearly = (((apvv['flh'] * apv_ver_p_max) + (apvh['flh'] * apv_hor_p_max))) * eeg_participation

    '''
    Special Regulation BB - Wind-/Solar-Euro
    '''

    wind_sr_bb_yearly = (wea_p_max * bb_euro_mw['wind']) * wind_euro_share
    pv_sr_bb_yearly = pv_p_max * bb_euro_mw['pv']
    apv_sr_bb_yearly = (apv_ver_p_max + apv_hor_p_max) * bb_euro_mw['pv']


    '''
    PROPERTY TAX
    '''

    '''
     INVESTMENT COSTS
     '''

    # calculate electricity price for each year, based on the actual year
    def get_price_for_year(electricity_price, start_year, target_year):
        if str(target_year) in electricity_price:
            return electricity_price[str(target_year)]
        else:
            last_year = max(int(year) for year in electricity_price.keys())
            return electricity_price[str(last_year)]
    def calculate_profit_year(title, eeg_share_mun, investment_costs, debt_capital_share, interest_rate,
                              repayment_period, annual_opex_first_10,
                              annual_opex_after_10, energy_generated, electricity_price,
                              tax_assesment_amount, levy_rate, redemption_free_years, annual_depreciation,
                              depreciation_duration, degradation, initial_loss_carryforward=0):
        # Initiale Calculation
        debt_capital = investment_costs * debt_capital_share

        if redemption_free_years == 1:
            interest_year_1 = debt_capital * interest_rate
            remaining_debt = debt_capital
            annual_repayment = remaining_debt / (repayment_period - 2)

        else:
            remaining_debt = debt_capital
            annual_repayment = remaining_debt / repayment_period

        accumulated_costs = 0
        accumulated_income = 0
        accumulated_annual_profits = 0
        year = 0
        annual_profits = []
        trade_tax_total = []
        trade_tax = []
        profit_first_year = None
        total_loss_carryforward = initial_loss_carryforward

        for year in range(1, 26):  # Year 1 to 25
            calculation_year = current_year + year - 1
            price_per_amount = get_price_for_year(electricity_price, current_year, calculation_year)

            if year <= 10:
                annual_opex = annual_opex_first_10
            else:
                annual_opex = annual_opex_after_10

            if year > depreciation_duration:
                annual_depreciation = 0

            if year == 1:
                annual_energy_yield = energy_generated
                eeg_annual_amount = eeg_share_mun
            else:
                annual_energy_yield = energy_generated * ((1 - degradation) ** year)
                eeg_annual_amount = eeg_share_mun * ((1 - degradation) ** year)

            if year == 1 and redemption_free_years == 1:
                annual_interests = interest_year_1
                repayment = 0
                annual_costs = annual_opex + annual_interests + eeg_annual_amount
            elif year == 2 and redemption_free_years == 1:
                annual_interests = interest_year_1
                repayment = 0
                annual_costs = annual_opex + annual_interests + eeg_annual_amount
            else:
                annual_interests = remaining_debt * interest_rate
                repayment = min(annual_repayment, remaining_debt)
                remaining_debt = max(0, remaining_debt - repayment)
                annual_costs = annual_opex + eeg_annual_amount + annual_interests

            accumulated_costs += annual_costs
            annual_income = annual_energy_yield * price_per_amount

            if annual_income > 0:
                accumulated_income += annual_income

            annual_profit = annual_income - annual_costs - annual_depreciation

            accumulated_annual_profits += annual_profit

            if annual_profit < 0:
                total_loss_carryforward += -annual_profit
                adjusted_profit = 0
            else:
                adjusted_profit = annual_profit

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

            annual_profits.append((year, adjusted_profit))

            if adjusted_profit > 0:
                trade_tax_total_value = (adjusted_profit * 0.9) * tax_assesment_amount * levy_rate
                trade_tax_value = trade_tax_total_value - (((adjusted_profit * 0.9) * tax_assesment_amount) * 0.35)
            else:
                trade_tax_total_value = 0
                trade_tax_value = 0

            trade_tax_total.append((year, trade_tax_total_value))
            trade_tax.append((year, trade_tax_value))

            if annual_profit > 0 and year >= 3:
                if profit_first_year is None:
                    profit_first_year = year

        return (
            profit_first_year if profit_first_year is not None else "no profit"), annual_profits, trade_tax, accumulated_annual_profits

    def run_scenario(params, results):

        installed_capacity = params.get("installed_capacity", 0)
        eeg_participation = params.get("eeg_participation", 0)
        profil = params.get("profil", pd.Series([0]))
        investment_costs = params.get("investment_costs", 0)
        opex10 = params.get("opex10", 0)
        opex20 = params.get("opex20", 0)
        sr_bb_euro = params.get("sr_bb_euro", 0)
        energy_generated = params.get("energy_generated", 0)
        redemption_free_years = params.get("redemption_free_years", 0)
        degradation = params.get("degradation", 0)
        title = params.get("title", "Unknown Scenario")

        investment_costs = investment_costs * installed_capacity
        debt_capital_share = params.get("debt_capital_share", 0.8)  # Standard 80%
        interest_rate = params.get("interest_rate", 0.05)  # Standard 5%
        repayment_period = params.get("repayment_period", 15)
        depreciation_duration = params.get("depreciation_duration", 0)
        if choosen_mun == 0 or check_county == "check_county_sh":
            sr_bb_euro = 0
        else:
            sr_bb_euro = installed_capacity * sr_bb_euro

        eeg_share_mun = ((profil * installed_capacity) * eeg_participation)
        annual_opex_first_10 = opex10 * installed_capacity + sr_bb_euro
        annual_opex_after_10 = opex20 * installed_capacity + sr_bb_euro
        energy_generated = energy_generated * installed_capacity * 1000
        redemption_free_years = redemption_free_years
        if depreciation_duration != 0:
            annual_depreciation = investment_costs / depreciation_duration
        else:
            annual_depreciation = 0
        profit_year, annual_profits, trade_tax, accumulated_annual_profits = calculate_profit_year(title,
                                                                                                    eeg_share_mun,
                                                                                                    investment_costs,
                                                                                                    debt_capital_share,
                                                                                                    interest_rate,
                                                                                                    repayment_period,
                                                                                                    annual_opex_first_10,
                                                                                                    annual_opex_after_10,
                                                                                                    energy_generated,
                                                                                                    electricity_price,
                                                                                                    tax_assesment_amount,
                                                                                                    levy_rate,
                                                                                                    redemption_free_years,
                                                                                                    annual_depreciation,
                                                                                                    depreciation_duration,
                                                                                                    degradation)

        # Saving the trade tax in the result dictionary
        results[params["name"]] = trade_tax

    # Save trade tax results for different scenarios
    trade_tax_results = {}

    # Defining scenarios
    scenarios = [  # Wind 100%
        {"installed_capacity": wea_p_max, "energy_generated": wind['flh'],
         "eeg_participation": eeg_participation,
         "profil": wind['flh'], "sr_bb_euro": bb_euro_mw['wind'],
         "investment_costs": wea_invest_cost,
         "opex10": wind['opex10'], "opex20": wind['opex20'], "debt_capital_share": wind['debt_capital_share'], "interest_rate": wind['interest_rate'],
         "repayment_period": wind['repayment_period'], "title": "Gewerbesteuer der WEA",
         "filename": "komm-wert-gwst-anlagenbetreibende-wind100.png", "bar_color": colors['orange'], "redemption_free_years": 1,
         "name": 'Wind100', "depreciation_duration": wind['depreciation_duration'], "degradation": wind['degradation']},  # FF-PV 100%
        {"installed_capacity": pv_p_max, "energy_generated":  ffpv['flh'],
         "eeg_participation": 2,
         "profil": ffpv['flh'], "sr_bb_euro": bb_euro_mw['pv'], "investment_costs": ffpv_invest_costs,
         "opex10": ffpv['opex'], "opex20": ffpv['opex'], "debt_capital_share": ffpv['debt_capital_share'], "interest_rate": ffpv['interest_rate'],
         "repayment_period": ffpv['repayment_period'], "title": "Gewerbesteuer der FF-PV",
         "filename": "komm-wert-gwst-anlagenbetreibende-ff-pv-100.png", "bar_color": colors['green'],
         "redemption_free_years": 1, "name": 'FFPV100', "depreciation_duration": ffpv['depreciation_duration'],"degradation": ffpv['degradation']},
        # Agri-PV hor. 100%
        {"installed_capacity": apv_hor_p_max, "energy_generated":  apvh['flh'],
         "eeg_participation": eeg_participation,
         "profil": apvh['flh'], "sr_bb_euro": bb_euro_mw['pv'],
         "investment_costs": apvh_invest_costs, "opex10": apvh['opex'], "opex20": apvh['opex'],
         "debt_capital_share": apv_general['debt_capital_share'], "interest_rate": apv_general['interest_rate'], "repayment_period": apv_general['repayment_period'],
         "title": "Max. Gewerbesteuer der Agri-PV-Anlagen (hor.)",
         "filename": "komm-wert-gwst-anlagenbetreibende-agri-pv-hor-1.png", "bar_color": colors['blue'],
         "redemption_free_years": 1, "name": 'APVH100', "depreciation_duration": apv_general['depreciation_duration'], "degradation": apv_general['degradation']},
        # Agri-PV ver. 100%
        {"installed_capacity": apv_ver_p_max, "energy_generated":  apvv['flh'],
         "eeg_participation": eeg_participation,
         "profil": apvv['flh'], "sr_bb_euro": bb_euro_mw['pv'],
         "investment_costs": apvv_invest_costs, "opex10": apvv['opex'], "opex20": apvv['opex'],
         "debt_capital_share": apv_general['debt_capital_share'], "interest_rate": apv_general['interest_rate'], "repayment_period": apv_general['repayment_period'],
         "title": "Max. Gewerbesteuer der Agri-PV-Anlagen (ver.)",
         "filename": "komm-wert-gwst-anlagenbetreibende-agri-pv-ver-1.png", "bar_color": colors['blue'],
         "redemption_free_years": 1, "name": 'APVV100', "depreciation_duration": apv_general['depreciation_duration'], "degradation": apv_general['degradation']},
    ]
    for scenario in scenarios:
        run_scenario(scenario, trade_tax_results)

    scenario_name_for_sum_1 = ["FFPV100"]
    scenario_name_for_sum_2 = ["APVV100", "APVH100"]
    scenario_name_for_sum_3 = ["Wind100"]

    # finding maximum annual trade tax
    def max_annual_sum(trade_tax_results, scenario_name_for_sum):
        tax_sum = [0] * 25

        # Sum up the trade tax per year across the specific scenarios
        for jahr in range(1, 26):
            for scenarioname in scenario_name_for_sum:
                for j, steuer in trade_tax_results[scenarioname]:
                    if j == jahr:
                        tax_sum[jahr - 1] += steuer

        # Find the maximum value of the total trade tax per year
        max_tax = max(tax_sum)
        return max_tax

    max_tax_1 = max_annual_sum(trade_tax_results, scenario_name_for_sum_1)
    max_tax_2 = max_annual_sum(trade_tax_results, scenario_name_for_sum_2)
    max_tax_3 = max_annual_sum(trade_tax_results, scenario_name_for_sum_3)

    # total trade tax over 25 years
    total_trade_tax_1 = sum(
        sum(jahressteuer for jahr, jahressteuer in trade_tax_results[scenarioname] if jahressteuer > 0) for
        scenarioname in scenario_name_for_sum_1)

    total_trade_tax_2 = sum(
        sum(jahressteuer for jahr, jahressteuer in trade_tax_results[scenarioname] if jahressteuer > 0) for
        scenarioname in scenario_name_for_sum_2)
    total_trade_tax_3 = sum(
        sum(jahressteuer for jahr, jahressteuer in trade_tax_results[scenarioname] if jahressteuer > 0) for
        scenarioname in scenario_name_for_sum_3)

    # Create echarts for trade tax
    echart_trade_tax_pv = create_echarts_data_gewerbesteuer(trade_tax_results['FFPV100'], 25,
                                      "gewerbesteuer_ff_pv.json",
                                      "FF-PV", colors['blue'])

    echart_trade_tax_wind = create_echarts_data_gewerbesteuer(trade_tax_results['Wind100'], 25,
                                      "gewerbesteuer_wind.json",
                                      "WEA", colors['red'])

    apv_combined = []
    for year in range(1, 26):
        apv_value = sum(trade_tax_results[name][year - 1][1] for name in scenario_name_for_sum_2)
        apv_combined.append((year, apv_value))

    echart_trade_tax_apv = create_echarts_data_gewerbesteuer(apv_combined, 25,
                                      "gewerbesteuer_agri_pv.json",
                                      "APV", colors['green'])

    '''
    ALL MUN INCOME FOR 25 YEARS
    '''
    years = 25

    # Calculate the amount of energy generated taking into account the power degradation for 25 years
    def calculate_degraded_sum(initial_value, degradation_rate, years=25):
        total = 0
        yearly_eeg = []

        for year in range(1, years + 1):
            degraded_value = initial_value * (1 - degradation_rate) ** year
            total += degraded_value
            yearly_eeg.append(degraded_value)

        return total, yearly_eeg

    wind_eeg_degradation_result, wind_eeg_degradation_yearly = calculate_degraded_sum(wind_eeg_yearly,
                                                                                      wind['degradation'], years)
    pv_eeg_degradation_result, pv_eeg_degradation_yearly = calculate_degraded_sum(pv_eeg_yearly, ffpv['degradation'],
                                                                                  years)
    apv_eeg_degradation_result, apv_eeg_degradation_yearly = calculate_degraded_sum(apv_eeg_yearly, apv_general['degradation'],
                                                                                    years)

    trade_tax_plant = [total_trade_tax_3, total_trade_tax_1,
                             total_trade_tax_2]
    eeg_income = [wind_eeg_degradation_result, pv_eeg_degradation_result, apv_eeg_degradation_result]
    property_tax = [property_tax_a_wea * years, 0, 0]
    # only show wind-/solar-euro for muns in brandenburg
    if choosen_mun != "0" and check_county != "check_county_sh":
        sr_bb_income = [wind_sr_bb_yearly * years, pv_sr_bb_yearly * years, apv_sr_bb_yearly * years]
    else:
        sr_bb_income = [0, 0, 0]

    area_costs_total = np.array(area_costs_yearly) * years
    area_gewst_total = np.array(area_gewst_yearly) * years
    area_est_total = np.array(area_est_yearly) * years

    sum_wea = property_tax_a_wea + total_trade_tax_3 + wind_eeg_degradation_result + wind_sr_bb_yearly * years + area_costs_total[0] + area_gewst_total[0] + area_est_total[0]
    sum_ff_pv = total_trade_tax_1 + pv_eeg_degradation_result + pv_sr_bb_yearly * years  + area_costs_total[1] + area_gewst_total[1] + area_est_total[1]
    sum_agri_pv = total_trade_tax_2 + apv_eeg_degradation_result + apv_sr_bb_yearly * years + area_costs_total[2] + area_gewst_total[2] + area_est_total[2]
    sum_wea_plot = [0, 0, 0, sum_wea, 0, 0]
    sum_agri_pv_plot = [0, 0, 0, 0, 0, sum_agri_pv]
    sum_ff_pv_plot = [0, 0, 0, 0, sum_ff_pv, 0]
    # create charts
    echart_area_lease_income = create_echarts_data_pachteinnahmen(area_costs_yearly, area_est_yearly, area_gewst_yearly)
    echart_eeg = create_echarts_data_eeg(wind_eeg_yearly, pv_eeg_yearly, apv_eeg_yearly)
    echart_srbb = create_echarts_data_srbb(wind_sr_bb_yearly, pv_sr_bb_yearly, apv_sr_bb_yearly)

    echart_total_income = create_echarts_data_total_mun_income(trade_tax_plant, eeg_income, sr_bb_income,
                                        area_costs_total.tolist(), area_gewst_total.tolist(),
                                        area_est_total.tolist(), sum_wea_plot, sum_agri_pv_plot, sum_ff_pv_plot, property_tax)

    # correct format for values displayed on added_value_results.html
    def format_numbers(value):
        return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    def format_numbers_0(value):
        return f"{value:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    apv_area_income = apvh_area_income + apvv_area_income
    lease_est_income_apv = lease_est_income_apvh + lease_est_income_apvv
    lease_trade_tax_apv = apvh_area_gewst_total + apvv_area_gewst_total

    wind_eeg_yearly = format_numbers(wind_eeg_yearly)
    pv_eeg_yearly = format_numbers(pv_eeg_yearly)
    apv_eeg_yearly = format_numbers(apv_eeg_yearly)
    wind_sr_bb_yearly = format_numbers(wind_sr_bb_yearly)
    pv_sr_bb_yearly = format_numbers(pv_sr_bb_yearly)
    apv_sr_bb_yearly = format_numbers(apv_sr_bb_yearly)
    wea_area_income = format_numbers(wea_area_income)
    pv_area_income = format_numbers(pv_area_income)
    apv_area_income = format_numbers(apv_area_income)
    lease_est_income_wea = format_numbers(lease_est_income_wea)
    lease_est_income_pv = format_numbers(lease_est_income_pv)
    lease_est_income_apv = format_numbers(lease_est_income_apv)
    lease_trade_tax_wea = format_numbers(lease_trade_tax_wea)
    lease_trade_tax_pv = format_numbers(lease_trade_tax_pv)
    lease_trade_tax_apv = format_numbers(lease_trade_tax_apv)
    total_trade_tax_1 = format_numbers(total_trade_tax_1)
    total_trade_tax_2 = format_numbers(total_trade_tax_2)
    total_trade_tax_3 = format_numbers(total_trade_tax_3)
    max_tax_1 = format_numbers(max_tax_1)
    max_tax_2 = format_numbers(max_tax_2)
    max_tax_3 = format_numbers(max_tax_3)
    sum_wea = format_numbers(sum_wea)
    sum_ff_pv = format_numbers(sum_ff_pv)
    sum_agri_pv = format_numbers(sum_agri_pv)
    property_tax_a_wea = format_numbers(property_tax_a_wea)
    N_wea = format_numbers_0(N_wea)
    wea_area_property_tax = format_numbers_0(wea_area_property_tax)

    results.update({"wind_eeg_yearly": wind_eeg_yearly,
               "pv_eeg_yearly": pv_eeg_yearly,
               "apv_eeg_yearly":apv_eeg_yearly,
                  "wind_sr_bb_yearly":  wind_sr_bb_yearly,
                    "pv_sr_bb_yearly": pv_sr_bb_yearly,
                    "apv_sr_bb_yearly": apv_sr_bb_yearly,
                    "total_trade_tax_1": total_trade_tax_1,
                    "total_trade_tax_2": total_trade_tax_2,
                    "total_trade_tax_3": total_trade_tax_3,
                    'wea_area_income': wea_area_income,
                    'pv_area_income': pv_area_income,
                    'apv_area_income': apv_area_income,
                    'lease_est_income_wea':lease_est_income_wea,
                    'lease_est_income_pv':lease_est_income_pv,
                    'lease_est_income_apv': lease_est_income_apv,
                    'lease_trade_tax_wea': lease_trade_tax_wea,
                    'lease_trade_tax_pv': lease_trade_tax_pv,
                    'lease_trade_tax_apv': lease_trade_tax_apv,
                    'max_tax_1': max_tax_1,
                    'max_tax_2': max_tax_2,
                    'max_tax_3': max_tax_3,
                    'sum_wea': sum_wea,
                    'sum_ff_pv': sum_ff_pv,
                    'sum_agri_pv': sum_agri_pv,
                    'choosen_mun': choosen_mun,
                    'check_county':check_county,
                    'echart_area_lease_income': echart_area_lease_income,
                    'echart_eeg': echart_eeg,
                    'echart_wind_solar_euro': echart_srbb,
                    'echart_trade_tax_wind': echart_trade_tax_wind,
                    'echart_trade_tax_pv': echart_trade_tax_pv,
                    'echart_trade_tax_apv': echart_trade_tax_apv,
                    'echart_total_income': echart_total_income,
                    'property_tax_a_wea': property_tax_a_wea,
                    'N_wea': N_wea,
                    'wea_area_property_tax':wea_area_property_tax
                    })

    return results

if __name__ == "__main__":
    form_data = {
        'ffpv_area_max': '40',
        'apvv_area_max': '500',
        'apvh_area_max': '300',
        'wea_area_max': '2000',
        'wea_eeg_share': '100',
        'wind_euro_share': '100',
        'rotor_diameter': '130',
        'system_output': '4',
        'wea_p_max': '1500',
        'pv_p_max': '1200',
        'apv_ver_p_max': '800',
        'apv_hor_p_max': '600',
        'area_ownertype': {},
        'levy_rate': '435',
        'choosen_mun': '1',
        'check_county': 'check_county_bb'
    }
    main(form_data)
