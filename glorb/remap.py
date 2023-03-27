import numpy as np


def remap_elevations(
    norm_elevations: np.ndarray,
    func_name: str,
    power_1: float,
    power_2: float,
):
    assert (norm_elevations >= 0).all()
    assert (norm_elevations <= 1).all()
    if func_name == "power":
        return norm_elevations**power_1
    elif func_name == "double-power":
        return (norm_elevations**power_1 + norm_elevations**power_2) / 2
    elif func_name == "derp":
        # Quintic regression on mycurvefit with
        #         0                  0
        #         0.2                0.2
        #         0.5                0.3
        #         0.8                0.5
        #         0.9                0.65
        #         1                  1
        return (
            1.265654e-14
            + 2.761508 * norm_elevations
            - 14.75159 * norm_elevations**2
            + 37.35516 * norm_elevations**3
            - 41.62698 * norm_elevations**4
            + 17.2619 * norm_elevations**5
        )
    raise NotImplementedError(f"Unknown func_name: {func_name}")
