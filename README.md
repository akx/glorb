# glorb

Generates an STL mesh of the globe, with height data.

## Usage

* Download the GEBCO_2022 grid dataset (netCDF) and unzip it:
  https://www.gebco.net/data_and_products/gridded_bathymetry_data/
* Install dependencies (please enable a virtualenv first): `pip install -e .`
* Run e.g. `python -m glorb.gen -i GEBCO_2022.nc -r 500 -es2=1.2 --map-func=derp -o glorb.stl`

Intermediate results are cached in `cache`; this will allow you to toy with the mapping functions,
etc. without having to recompute the icosahedron sphere, or the heightmap (if the resolution is the same).
You can nuke that directory at will.
