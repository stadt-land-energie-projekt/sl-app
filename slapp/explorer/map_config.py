"""Actual map setup is done here."""
import dataclasses

from django.utils.translation import gettext_lazy as _
from django_mapengine import legend


@dataclasses.dataclass
class SymbolLegendLayer(legend.LegendLayer):
    """Adds symbol field."""

    symbol: str = "rectangle"


LEGEND = {
    _("Renewables"): [
        SymbolLegendLayer(
            _("Wind turbine"),
            _("Windenergieanlagen"),
            layer_id="wind",
            color="#6A89CC",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("Roof-mounted PV"),
            _("PV-Aufdachanlagen"),
            layer_id="pvroof",
            color="#FFD660",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("Ground-mounted PV"),
            _("PV-Freiflächenanlagen"),
            layer_id="pvground",
            color="#EFAD25",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("Hydro"),
            _("Wasserkraftanlagen"),
            layer_id="hydro",
            color="#A9BDE8",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("Biomass"),
            _("Biomasseanlagen"),
            layer_id="biomass",
            color="#52C41A",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("Combustion"),
            _("Verbrennungskraftwerke"),
            layer_id="combustion",
            color="#E6772E",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("GSGK"),
            _("Geo- oder Solarthermie-, Grubengas- und Klärschlamm-Anlagen"),
            layer_id="gsgk",
            color="#C27BA0",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("Batteriespeicher"),
            _("Batteriespeicher"),
            layer_id="storage",
            color="#8D2D5F",
            symbol="circle",
        ),
    ],
    _("Settlements Infrastructure"): [
        legend.LegendLayer(
            _("Industry"),
            _(
                "Industrie- und Gewerbegebiete werden ausgewiesen, um störende Einwirkungen von Betrieben wie Lärm, "
                "Geruch oder Gefahren auf Wohnbebauung zu vermeiden.",
            ),
            layer_id="industry",
        ),
        legend.LegendLayer(
            _("Road"),
            _("Zu den Straßen gehören unter anderem Bundesautobahnen, Bundesfern-, Landes- und Kreisstraßen."),
            layer_id="road_default",
        ),
        legend.LegendLayer(
            _("Railway"),
            _(
                "Der Bahnverkehr ist ein wichtiger Bestandteil der Verkehrsinfrastruktur. Berücksichtigt "
                "werden Fernverkehrsbahnen, Regionalverkehrsbahnen und S-Bahnen.",
            ),
            layer_id="railway",
        ),
        legend.LegendLayer(
            _("Aviation"),
            _(
                "Zur Infrastruktur des Luftverkehrs gehören neben Start- und Landebahnen die "
                "Flughafengebäude und Hangars.",
            ),
            layer_id="aviation",
        ),
        legend.LegendLayer(
            _("Air Traffic"),
            _("Ein Drehfunkfeuer ist ein Funkfeuer für die Luftfahrtnavigation."),
            layer_id="air_traffic",
        ),
        legend.LegendLayer(
            _("Military"),
            _("Zu den militärisch genutzten Flächen gehören militärische Sperrgebiete und Liegenschaften."),
            layer_id="military",
        ),
        legend.LegendLayer(
            _("Grid"),
            _(
                "Zum Übertragungsnetz zählen die elektrischen Leitungen sowie die dazugehörigen Einrichtungen "
                "wie Schalt- und Umspannwerke der Höchst- und Hochspannungsebenen.",
            ),
            layer_id="grid",
        ),
    ],
    _("Nature Landscape"): [
        legend.LegendLayer(
            _("Nature Conservation Area"),
            _(
                "Naturschutzgebiete dienen dem Schutz der Natur und Landschaft. Sie tragen zur Erhaltung, Entwicklung "
                "und Wiederherstellung der Lebensstätte für bestimmte wild lebende Tier- und Pflanzenarten bei. Aber "
                "auch aus wissenschaftlichen, naturgeschichtlichen und ästhetischen Gründen werden Teile oder die "
                "Gesamtheit der Natur in Schutz genommen.",
            ),
            layer_id="nature_conservation_area",
        ),
        legend.LegendLayer(
            _("Fauna Flora Habitat"),
            _(
                "Die Fauna-Flora-Habitat-Richtlinie ist eine Naturschutz-Richtlinie der Europäischen Union (EU), die "
                "seltene oder bedrohte Arten und Lebensräume schützt. Sie gehört zum Schutzgebietsnetz Natura 2000.",
            ),
            layer_id="fauna_flora_habitat",
        ),
        legend.LegendLayer(
            _("Special Protection Area"),
            _(
                "Die Vogelschutzrichtlinie der Europäischen Union (EU) dient der Erhaltung der wild lebenden, "
                "heimischen Vogelarten. Sie regelt den Schutz dieser Vögel, ihrer Eier und Lebensräume wie Brut-, "
                "Rast- und Überwinterungsgebiete. Die Vogelschutzgebiete gehören zum Schutzgebietsnetz Natura 2000.",
            ),
            layer_id="special_protection_area",
        ),
        legend.LegendLayer(
            _("Biosphere Reserve"),
            _(
                "Biosphärenreservate sind großräumige und für bestimmte Landschaftstypen charakteristische Gebiete "
                "mit interdisziplinärem Ansatz. In diesen von der UNESCO initiierten Modellregionen soll nachhaltige "
                "Entwicklung in ökologischer, ökonomischer und sozialer Hinsicht exemplarisch verwirklicht werden. "
                "Die Biosphärenreservate sind in drei Zonen eingeteilt: Eine naturschutzorientierte Kernzone "
                "(Schutzfunktion), eine am Landschaftsschutz orientierte Pflegezone (Forschungs- und Bildungsfunktion)"
                " und eine sozioökonomisch orientierte Entwicklungszone (Entwicklungsfunktion).",
            ),
            layer_id="biosphere_reserve",
        ),
        legend.LegendLayer(
            _("Landscape Protection Area"),
            _(
                "Landschaftsschutzgebiete sind oft großflächiger angelegt und zielen auf den Erhalt des "
                "Landschaftscharakters, das allgemeine Erscheinungsbild der Landschaft und dessen Schönheit ab. "
                "Sie haben einen geringeren Schutzstatus als etwa Naturschutzgebiete oder Nationalparke und "
                "unterliegen daher weniger strengen Nutzungsbeschränkungen.",
            ),
            layer_id="landscape_protection_area",
        ),
        legend.LegendLayer(
            _("Forest"),
            _(
                "Wald umfasst eine Vielzahl an mit Bäumen und anderer Vegetation bedeckten Fläche "
                "mit unterschiedlicher forstwirtschaftlicher Nutzung und ökologischer Bedeutung. Wälder können in "
                "Nadel-, Laub- und Mischwald sowie anhand der Waldfunktionen (z. B. Schutzwald, Erholungswald) "
                "unterschieden werden.",
            ),
            layer_id="forest",
        ),
        legend.LegendLayer(
            _("Drinking Water Protection Area"),
            _(
                "Wasserschutzgebiete stellen die öffentliche Wasserversorgung durch die Vermeidung "
                "schädlicher Eintragungen in die Gewässer "
                "(Grundwasser, oberirdische Gewässer, Küstengewässer) sicher.",
            ),
            layer_id="drinking_water_protection_area",
        ),
        legend.LegendLayer(
            _("Water"),
            _(
                "Ein Gewässer ist in der Natur fließendes oder stehendes Wasser. "
                "Dazu gehören der Wasserkörper, das Gewässerbett und der Grundwasserleiter.",
            ),
            layer_id="waters",
        ),
        legend.LegendLayer(
            _("Floodplain"),
            _(
                "Bei Überschwemmungsgebieten handelt es sich um die Flächen, "
                "die statistisch gesehen mindestens einmal in hundert Jahren überflutet sein können.",
            ),
            layer_id="floodplain",
        ),
    ],
}
