import argparse

import numpy as np
from stl import mesh

from glorb.get_elevations import get_elevations
from glorb.remap import remap_elevations
from glorb.sphere import get_icosphere


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gebco-file", "-i", required=True)
    ap.add_argument("--output-file", "-o", required=True)
    ap.add_argument("--resolution", "-r", type=int, default=5)
    ap.add_argument("--sphere-radius", "-sr", type=float, default=50)
    ap.add_argument("--max-elev", "-e2", type=float, default=8900)  # Everest, rounded
    ap.add_argument("--max-elev-radius-scale", "-es2", type=float)
    ap.add_argument("--min-elev", "-e1", type=float, default=0)
    ap.add_argument("--min-elev-radius-scale", "-es1", type=float, default=1)
    ap.add_argument("--map-power1", "-mp1", type=float, default=1)
    ap.add_argument("--map-power2", "-mp2", type=float, default=1)
    ap.add_argument("--map-func", "-mf", choices=["power", "double-power", "derp"])
    args = ap.parse_args()

    min_elev = args.min_elev
    max_elev = args.max_elev
    min_elev_radius_scale = args.min_elev_radius_scale
    max_elev_radius_scale = args.max_elev_radius_scale

    if max_elev_radius_scale is None:
        assert min_elev == 0  # TODO: support this case
        earth_radius = 6371 * 1000  # meters
        max_elev_radius_scale = (earth_radius + max_elev) / earth_radius

    if min_elev > max_elev:
        raise ValueError("min_elev must be <= max_elev")
    if min_elev_radius_scale > max_elev_radius_scale:
        print(
            "Warning: min_elev_radius_scale > max_elev_radius_scale; "
            "this will result in a concave surface",
        )

    print(f"{min_elev}m -> {min_elev_radius_scale}x")
    print(f"{max_elev}m -> {max_elev_radius_scale}x")

    vertices, faces = get_icosphere(args.resolution)
    print(f"Number of vertices: {len(vertices)}")
    print(f"Number of faces: {len(faces)}")

    elevations = get_elevations(args.gebco_file, vertices)
    print(f"Elevation bounds in samples: {elevations.min()}..{elevations.max()}")
    print("Rescaling elevations...")
    clamped_elevations = np.clip(elevations, min_elev, max_elev)
    norm_elevations = (clamped_elevations - min_elev) / (max_elev - min_elev)
    mapped_elevations = remap_elevations(
        norm_elevations,
        func_name=args.map_func,
        power_1=args.map_power1,
        power_2=args.map_power2,
    )
    elev_radius_scales = (
        mapped_elevations * (max_elev_radius_scale - min_elev_radius_scale)
        + min_elev_radius_scale
    )
    print("Applying elevations...")
    vertices *= (args.sphere_radius * elev_radius_scales)[:, np.newaxis]

    print("Creating mesh...")
    icomesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            icomesh.vectors[i][j] = vertices[f[j], :]
    print("Saving mesh...")
    icomesh.save(args.output_file)


if __name__ == "__main__":
    main()
