"""Module holds helper function for distilling."""

import logging
from collections import defaultdict

from django_mapengine import distill


def check_distill_coordinates() -> dict:
    """Return coordinates for all static tiles."""
    tiles = list(distill.get_coordinates_for_distilling("static"))
    coordinates = defaultdict(lambda: {"x": [None, None], "y": [None, None]})
    for tile in tiles:
        z = tile[2]
        if not coordinates[z]["x"][0] or coordinates[z]["x"][0] > tile[0]:
            coordinates[z]["x"][0] = tile[0]
        if not coordinates[z]["x"][1] or coordinates[z]["x"][1] < tile[0]:
            coordinates[z]["x"][1] = tile[0]
        if not coordinates[z]["y"][0] or coordinates[z]["y"][0] > tile[1]:
            coordinates[z]["y"][0] = tile[1]
        if not coordinates[z]["y"][1] or coordinates[z]["y"][1] < tile[1]:
            coordinates[z]["y"][1] = tile[1]
    return coordinates


if __name__ == "__main__":
    logging.info(check_distill_coordinates())
