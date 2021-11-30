"""
Module interfacing with the OpenStreetMap API to get map tiles
"""
import os
import math
import requests
import numpy as np
import matplotlib.pyplot as plt

URL = 'https://tile.osm.ch/switzerland/{z}/{x}/{y}.png'
FILE = 'maps/{z}-{x}-{y}.png'
MAP_FOLDER = 'maps'


def get_tile(x, y, z):
    """Saves the requested tile if it not already exists

    :param x: "column" number of the tile
    :param y: "row" number of the tile
    :param z: zoom value for the tile
    :return: status code:
    1 saved new file, -1 tile not found, 0 using cached version
    """
    file_name = FILE.format(x=x, y=y, z=z)
    if not os.path.exists(file_name):
        # request the file and save it
        url = URL.format(x=x, y=y, z=z)
        r = requests.get(url)
        if r.ok:
            with open(file_name, 'wb') as f:
                f.write(r.content)
                return 1
        else:
            print(f'Could not get {url} because : {r.status_code}\n{r}')
            return -1
    else:
        # Using cached version
        return 0


def deg2num(lat_deg, lon_deg, zoom):
    """Convert a latitude and longitude to tile infos (x, y, z)

    :param lat_deg: latitude in degrees
    :param lon_deg: longitude in degrees
    :param zoom: zoom level (1 to 16)
    :return: tile coords (x, y)
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x_tile = int((lon_deg + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return x_tile, y_tile


def num2deg(x_tile, y_tile, zoom):
    """Convert tile coords into latitude and longitude of the NW corner of the tile

    :param x_tile: "column" of the tile
    :param y_tile: "row" of the tile
    :param zoom: zoom level of the tile
    :return: latitude and longitude of the north-west corner of the tile
    """
    n = 2.0 ** zoom
    lon_deg = x_tile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


def bboxtile(x_tile, y_tile, zoom, nb_x_tiles=1, nb_y_tiles=1):
    """Compute the bounding box of a tile based on its x, y and zoom values.
    Can also compute the bounding box for anarrray of tiles based on the number
    of tiles in rows and columns

    :param x_tile: "column" of the tile
    :param y_tile: "row" of the tile
    :param zoom: zoom level of the tile
    :param nb_x_tiles: number of tiles in the columns (width)
    :param nb_y_tiles: number of tiles in the rows (height)
    :return: bounding box (left, right, bottom, top) in latitude and longitude
    """
    n = 2.0 ** zoom
    # long min
    lon_min_deg = x_tile / n * 360.0 - 180.0
    # long max
    lon_max_deg = (x_tile + nb_x_tiles) / n * 360.0 - 180.0
    # lat max
    lat_max_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
    lat_max_deg = math.degrees(lat_max_rad)
    # lat min
    lat_min_rad = math.atan(math.sinh(math.pi * (1 - 2 * (y_tile + nb_y_tiles) / n)))
    lat_min_deg = math.degrees(lat_min_rad)
    # left, right, bottom, top
    return lon_min_deg, lon_max_deg, lat_min_deg, lat_max_deg


def compute_aspect(bbox, map_size):
    """Compute the aspect ratio to give to matplotlib imshow function.
    Is based on the bounding box (in degrees) and the number of tiles used

    :param bbox: bounding box of the map (in lat long coords)
    :param map_size: tuple of the number of tiles used
    :return: aspect ratio for imshow
    """
    # compute the bounding box aspect ratio : dy/dx
    aspect_bbox = (bbox[1] - bbox[0]) / (bbox[3] - bbox[2])
    # compute the map aspect ratio
    aspect_map = map_size[0] / map_size[1]
    return aspect_bbox * aspect_map


def plot_map_status(map_status, zoom, map_size, x_tile_min, x_tile_max,
                    y_tile_min, y_tile_max):
    """Plot a status map of the fetched tiles

    :param map_status: 2D array of the tiles status codes
    :param zoom: zoom level
    :param map_size: tuple of the map size
    :param x_tile_min: min coord for x
    :param x_tile_max: max coord for x
    :param y_tile_min: min coord for y
    :param y_tile_max: max coord for y
    """
    fig, ax = plt.subplots()
    ax.imshow(map_status, cmap='viridis', alpha=0.7, aspect='equal', vmin=-1,
              vmax=1)
    ax.set_title(f'Status of tile maps {zoom=}')
    ax.spines[:].set_visible(False)
    ax.set_xticks(np.arange(map_size[1]) - .5, minor=True)
    ax.set_yticks(np.arange(map_size[0]) - .5, minor=True)
    ax.grid(which='minor', color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_xticks(np.arange(map_size[1]), )
    ax.set_yticks(np.arange(map_size[0]))
    ax.set_xticklabels([str(i) for i in np.arange(x_tile_min, x_tile_max + 1)],
                       minor=False, rotation=90)
    ax.set_yticklabels([str(i) for i in np.arange(y_tile_min, y_tile_max + 1)],
                       minor=False)
    plt.show()


def get_stitched_map_and_bbox(df, zoom, verbose=False):
    """Get a map spanning all the coords in df

    :param df: dataframe of the tiles
    :param zoom: desired zoom level
    :param verbose: whether to display status informations
    :return: stitched map, bounding box of the map, map size
    """
    long_min = df.ll_x.min()  # long min
    long_max = df.ur_x.max()  # long max
    lat_min = df.ll_y.min()  # lat min
    lat_max = df.ur_y.max()  # lat max

    x_tile_min, y_tile_max = deg2num(lat_min, long_min, zoom)
    x_tile_max, y_tile_min = deg2num(lat_max, long_max, zoom)

    map_size = ((y_tile_max - y_tile_min) + 1, (x_tile_max - x_tile_min) + 1)
    if verbose:
        print(f'tiles used : {map_size}')
        print(f'Using {zoom=}, will stitch {map_size[0] * map_size[1]} tiles')
        print(f'Using tiles in x : from {x_tile_min} to {x_tile_max}')
        print(f'Using tiles in y : from {y_tile_min} to {y_tile_max}')

    # check maps folder existence
    if not os.path.exists(MAP_FOLDER):
        os.mkdir(MAP_FOLDER)

    tiles_status = np.zeros(map_size)

    for i, x_tile_num in enumerate(range(x_tile_min, x_tile_max + 1)):
        for j, y_tile_num in enumerate(range(y_tile_min, y_tile_max + 1)):
            # look if the image already exists
            tiles_status[j, i] = get_tile(x=x_tile_num, y=y_tile_num, z=zoom)
    if verbose:
        print('Done!')
        plot_map_status(tiles_status, zoom, map_size, x_tile_min, x_tile_max,
                        y_tile_min, y_tile_max)

    # stitch the map together
    background_map = []
    for i, x_tile_num in enumerate(range(x_tile_min, x_tile_max + 1)):
        map_col = []
        for j, y_tile_num in enumerate(range(y_tile_min, y_tile_max + 1)):
            file_name = FILE.format(x=x_tile_num, y=y_tile_num, z=zoom)
            map_col.append(plt.imread(file_name))
        background_map.append(np.vstack(map_col))

    stitched_map = np.concatenate(background_map, axis=1)
    bbox = bboxtile(x_tile_min, y_tile_min, zoom, nb_x_tiles=map_size[1],
                    nb_y_tiles=map_size[0])

    return stitched_map, bbox, map_size
