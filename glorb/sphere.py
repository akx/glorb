import numpy as np

from glorb.cache import cache


@cache.memoize(name="icosphere")
def get_icosphere(n: int) -> (np.ndarray, np.ndarray):
    from icosphere import icosphere

    print(f"Generating icosphere (resolution={n})...")
    vertices, faces = icosphere(n)
    return vertices, faces
