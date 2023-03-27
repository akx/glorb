import time

import numpy as np

from glorb.cache import cache


@cache.memoize(name="icosphere")
def get_icosphere(n: int) -> (np.ndarray, np.ndarray):
    from icosphere import icosphere

    print(f"Generating icosphere (resolution={n})...")
    t0 = time.time()
    vertices, faces = icosphere(n)
    t1 = time.time()
    print(f"Generated icosphere in {t1 - t0:.2f}s; {len(vertices)} vertices")
    return vertices, faces
