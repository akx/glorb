import multiprocessing
import os

import numpy as np
import tqdm

from netCDF4 import Dataset

from glorb.cache import cache

# For subprocesses.
FILE_ENVVAR = "_GLORB_GEBCO_FILE"
_GEBCO_DATASET = None


def get_elevations_worker(latlon_indices):
    global _GEBCO_DATASET
    if _GEBCO_DATASET is None:
        _GEBCO_DATASET = Dataset(os.environ[FILE_ENVVAR])
    elev = _GEBCO_DATASET.variables["elevation"]
    return [elev[lat, lon] for lat, lon in latlon_indices]


def get_elevations(filename: str, vertices: np.ndarray) -> np.ndarray:
    """
    Get elevations for a set of sphere vertices.

    :param filename: GEBCO CDF dataset file
    :param vertices: vertex array
    :return: elevation array matching the vertex array
    """
    os.environ[FILE_ENVVAR] = os.path.realpath(filename)
    assert os.path.isfile(filename)
    n_vertices = len(vertices)
    cache_key = "_".join(map(str, [os.environ[FILE_ENVVAR], n_vertices]))
    if cache_key in cache:
        print("Loading elevations from cache")
        return cache[cache_key]
    with Dataset(os.environ[FILE_ENVVAR]) as nc:
        elev_var = nc.variables["elevation"]
        lon_dim = nc.dimensions["lon"].size
        lat_dim = nc.dimensions["lat"].size
        assert elev_var.shape == (lat_dim, lon_dim)
        lats = np.rad2deg(np.arcsin(vertices[:, 2]))
        lons = np.rad2deg(np.arctan2(vertices[:, 1], vertices[:, 0]))
        lat_indices = (((lats + 90) / 180 * lat_dim) % lat_dim).astype(int)
        lon_indices = (((lons + 180) / 360 * lon_dim) % lon_dim).astype(int)
        latlon_indices = np.stack([lat_indices, lon_indices], axis=1)
        chunk_size = 1000
        latlon_indices_chunks = np.array_split(
            latlon_indices,
            len(latlon_indices) // chunk_size,
        )
        print(
            f"Finding elevations in {len(latlon_indices_chunks)} "
            f"chunks of {chunk_size} indices each...",
        )
        with multiprocessing.Pool() as pool:
            elevation_chunks = list(
                tqdm.tqdm(
                    pool.imap(get_elevations_worker, latlon_indices_chunks),
                    total=len(latlon_indices_chunks),
                    unit="chunk",
                    unit_scale=True,
                ),
            )
            elevations = np.concatenate(elevation_chunks)
        print("Saving elevations to cache")
        cache[cache_key] = elevations
    return elevations
