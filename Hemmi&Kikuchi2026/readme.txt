Supplementary Files for:
Scale-dependent gravity-referenced slopes on Phobos using diffusion-smoothed shape models with recomputed effective gravity

Authors:
Ryodo Hemmi
Institute of Space and Astronautical Science, Japan Aerospace Exploration Agency (JAXA/ISAS)

Hiroshi Kikuchi
Gakushuin University


OVERVIEW
--------
This Zenodo record contains the supplementary data products and analysis software
associated with the manuscript:

Scale-dependent gravity-referenced slopes on Phobos using diffusion-smoothed shape
models with recomputed effective gravity

The native input is the global stereophotoclinometric Phobos shape model v004 of
Ernst et al. (2023), with an approximate mean facet-edge scale of 18 m. The
native model is treated as the unsmoothed reference and has no assigned e-fold
smoothing wavelength L. For compact labeling in filenames, figures, and tables,
it is represented by "18 m," which denotes its approximate mean facet-edge scale
rather than an applied smoothing wavelength.

Volume-preserved diffusion-smoothed models were generated independently from the
native shape at e-fold wavelengths:

L = 80, 100, 125, 150, 175, 200, 250, 500, 1000, and 2000 m.

Effective gravity was recomputed for each shape model from Phobos self-gravity,
centrifugal acceleration, Euler acceleration, and the Martian tidal contribution.

Sampling-window sensitivity was evaluated for:

W = 1, 2, 4, 6, and 10 degrees.

Using the 11,080 m IAU 2015 Phobos reference-sphere radius, 1 degree corresponds
to an arc length of approximately 193.4 m. The physical east-west width of a
longitude interval decreases approximately as cos(latitude) on the reference
sphere.

To keep the archive compact, diffusion-smoothed OBJ models and large working
GeoPackage files are not redistributed. The smoothed OBJ models can be regenerated
from the publicly available native v004 shape model with smooth_mesh.py. The final
facet-level CSV products are included directly so users can inspect, reuse, or
reanalyze the derived gravity, slope, and azimuth results without repeating the
computationally expensive GFandSlope calculations.


ORIGINAL PHOBOS SHAPE MODEL
---------------------------
The native input model is the global Phobos stereophotoclinometric shape model v004
of Ernst et al. (2023).

Source:
https://sbmt.jhuapl.edu/shared-files/

Input filename used in this study:

phobos_g_018m_spc_obj_0000n00000_v004.obj

The original native shape model is not redistributed in this record. Obtain it
from the original public source above.


ZENODO FILES
------------

1. Individually compressed facet-level products (*.csv.gz)

The final facet-level products are distributed as 11 separate gzip-compressed
CSV files:

v004_0018_surface_TA000.csv.gz
v004_0080_surface_TA000.csv.gz
v004_0100_surface_TA000.csv.gz
v004_0125_surface_TA000.csv.gz
v004_0150_surface_TA000.csv.gz
v004_0175_surface_TA000.csv.gz
v004_0200_surface_TA000.csv.gz
v004_0250_surface_TA000.csv.gz
v004_0500_surface_TA000.csv.gz
v004_1000_surface_TA000.csv.gz
v004_2000_surface_TA000.csv.gz

The naming convention is:

v004_<scale4>_surface_TA000.csv.gz

where <scale4> is a zero-padded four-digit scale label in meters. The 0018
product is the native unsmoothed reference; 18 m denotes its approximate mean
facet-edge scale rather than an applied smoothing wavelength. The remaining
labels correspond to the applied e-fold wavelengths:

L = 80, 100, 125, 150, 175, 200, 250, 500, 1000, and 2000 m.

The files are provided separately rather than in a single approximately 8 GB
combined archive. This permits scale-selective downloads and avoids requiring
users to retrieve the entire facet-level dataset. Each .csv.gz file decompresses
to the correspondingly named .csv file.

Each CSV begins with commented metadata lines followed by facet-level data.
Principal columns are:

facet_id
lat_deg
lon_deg
dynamic_slope_deg
dynamic_slope_azimuth_deg
facet_area
g_total_x_m_s2
g_total_y_m_s2
g_total_z_m_s2
g_total_mag_m_s2

The header records the calculation epoch, adopted density, Martian geometry,
angular velocity, and other calculation metadata.

The products preserve a common facet ordering between the native model and all
smoothing wavelengths.

In these files, dynamic_slope_deg is the gravity-referenced slope angle defined in the manuscript.

These CSV files are the principal derived source products. Large GeoPackage
working copies are not redistributed because they are derived from these CSV files
and substantially increase the archive size.


2. phobos_slope_summary_products.zip

Machine-readable summary products used in the manuscript:

global_slope_summary.csv
    Global area-weighted slope statistics for the native reference and every
    applied L; values reported in Table 2.

global_slope_histograms.csv
    Differential and cumulative global slope-frequency distributions used in
    Figure 4.

roi_scale_response.csv
    Scale-response statistics for the four representative equatorial regions
    used in Figure 5.

roi_slope_histograms.csv
    Area-weighted regional slope-frequency distributions used in Figure 5.

grid_scale_response.csv
    Fixed-grid slope and azimuth statistics used in the global mapping analysis.

grid_window_summary.csv
    Sampling-window sensitivity results for W = 1, 2, 4, 6, and 10 degrees.

vector_response_summary.csv
    Surface-normal and effective-gravity vector-response statistics used in
    Figure 8.

analysis_manifest.json
    Analysis settings, input conventions, scale values, and weighting choices.


3. phobos_slope_code.zip

Principal scripts:

smooth_mesh.py
    Generates diffusion-smoothed triangular OBJ meshes using a cotangent stiffness
    matrix, barycentric lumped mass matrix, implicit-Euler integration, e-fold
    wavelength calibration, and optional post-diffusion volume preservation.

phobos_slope_analysis.py
    Calculates global slope-frequency distributions, representative-region
    statistics, fixed-grid statistics, sampling-window sensitivity, and
    corresponding surface-normal/effective-gravity vector responses.

Figure-specific plotting scripts and GIS project files are not included. The
publication figures were assembled from the machine-readable products using
standard plotting/GIS software.


4. phobos_slope_gravity_reproduction.zip

This archive contains:

run_gfandslope.sh
gfandslope.cfg.template
readme_gravity.txt
NoSpin_result_TA000_scripts_package/

The first three files document and reproduce the GFandSlope self-gravity calculation.
The NoSpin_result_TA000_scripts_package/ directory contains the post-processing code provided by H. Kikuchi.
This code reads the precomputed GFandSlope output, reverses the outward-pointing self-gravity vector,
and adds the centrifugal, Euler, and Martian tidal accelerations to generate
the final facet-level effective-gravity, slope, and azimuth products.

The supplied shell script is an illustrative single-model example and
does not reproduce the complete smoothing sequence without editing the
input-file list.

GFandSlope:
https://github.com/AiGIS-PyAiGIS/GFandSlope

GFandSlope itself is not redistributed here.

GFandSlope commit used:

c75f8dcafb38c08f6da74806adbb70f212bd9066

The GFandSlope stage used:

period: 0.0
density: 1862.297786 kg/m^3
input_points: NONE
gpu: 0

The period was intentionally set to 0.0 because GFandSlope was used for the
shape-derived self-gravity stage.
Centrifugal, Euler, and Martian tidal accelerations were added subsequently
by the accompanying wrapper. The angular velocity was obtained from the
J2000-to-IAU_PHOBOS state transformation, and the angular acceleration
used in the Euler term was calculated by a centered finite difference of
the SPICE-derived angular velocity evaluated 1 s before and 1 s after the nominal
epoch. At the nominal epoch,

|omega| = 2.2348606662528733e-4 rad/s,

|omega_dot| approximately 1.0386e-11 rad/s^2.

Calculation metadata are retained in the commented headers of the generated CSV
files.

Nominal orbital geometry:

true anomaly = 0 degrees
epoch = 2029 JAN 01 04:27:47.401 UTC

See readme_gravity.txt for details.

The accompanying gravity-wrapper files are stored in
NoSpin_result_TA000_scripts_package/:

README_NoSpin_result_TA000_scripts.md
requirements_NoSpin_result_TA000.txt
input/ (empty)
script/make_NoSpin_result_TA000.py (run with --alpha-dt 1.0 by default)
script/run_make_NoSpin_result_TA000.sh
spice/ (the SPICE kernels required by the wrapper)

Note: Some intermediate filenames retain the legacy string "NoSpin". These names are
      preserved for provenance. The final products used in the manuscript include
      centrifugal, Euler, and Martian tidal accelerations.


COORDINATE AND WEIGHTING CONVENTIONS
------------------------------------
All vector comparisons are performed in a common Phobos-fixed Cartesian frame.

The primary regional and global mapping analysis uses W = 2 degrees.

Facets are assigned to sampling windows using native-model facet centroids, and
the same facet assignments are retained across all smoothing wavelengths.

The sampling-window sensitivity analysis additionally uses:

W = 1, 4, 6, and 10 degrees.

Global slope-frequency and regional/grid statistics use facet-area weighting from
the corresponding shape model.

Cross-scale surface-normal and effective-gravity vector comparisons use
native-model facet areas as fixed weights.


REPRODUCTION WORKFLOW
---------------------
1. Obtain the native v004 Phobos OBJ shape model from the public Small Body
   Mapping Tool archive.

2. Generate the volume-preserved diffusion-smoothed models:

python smooth_mesh.py phobos_g_018m_spc_obj_0000n00000_v004.obj \
  -L 80 100 125 150 175 200 250 500 1000 2000 \
  --preserve_volume --keep

3. For each native/smoothed OBJ model, use GFandSlope's
   util/Mesh2GFandSlopeInput.py to generate the GFandSlope polygon input.

4. Run GFandSlope with run_gfandslope.sh and gfandslope.cfg.template to
   calculate shape-derived self-gravity.

5. Run the accompanying gravity wrapper in NoSpin_result_TA000_scripts_package/
   to reverse the outward-pointing GFandSlope GravAcc vector and add centrifugal,
   Euler, and Martian tidal accelerations, thereby generating the final
   effective-gravity, slope, and azimuth facet products.

6. In the original analysis workflow, working GeoPackage files were generated
   from the facet-level CSV products with GDAL. These large intermediate GPKG
   files are not redistributed.

7. Run the principal statistical analysis:

python -u phobos_slope_analysis.py \
  --gpkg-dir v004gpkg \
  --native-scale 18 \
  --native-obj phobos_g_018m_spc_obj_0000n00000_v004.obj \
  --obj-pattern 'phobos_g_018m_spc_obj_0000n00000_v004_diffuse_efold_{L}_preserve.obj' \
  --output-dir slope_analysis \
  --chunk-size 200000 \
  --obj-normal-chunk-size 500000 \
  --regional-weight current \
  --vector-weight native \
  --global-hist-bin-width-deg 0.5 \
  --roi-hist-bin-width-deg 0.5 \
  --fine-quantile-bin-width-deg 0.001 \
  --grid-sizes-deg 1 2 4 6 10 \
  --grid-quantile-bin-width-deg 0.1 \
  --gravity-mag-bin-width-pct 0.001 \
  --gravity-mag-max-pct 100 \
  --plots

The machine-readable summary products in phobos_slope_summary_products.zip are
the outputs supporting the principal statistical results and figures reported in
the manuscript.


EXTERNAL SOFTWARE
-----------------
GFandSlope:
https://github.com/AiGIS-PyAiGIS/GFandSlope

Small Body Mapping Tool:
https://sbmt.jhuapl.edu/

mkgraticule_planet:
https://doi.org/10.5281/zenodo.20397280
https://github.com/ryodohemmi/mkgraticule_planet


RELATED PUBLICATION
-------------------
Hemmi, R., & Kikuchi, H.
"Scale-dependent gravity-referenced slopes on Phobos using diffusion-smoothed
shape models with recomputed effective gravity."
The Planetary Science Journal.

Article DOI:
[ARTICLE DOI WHEN AVAILABLE]


CITATION
--------
If you use these supplementary products or scripts, please cite both the
associated journal article and this Zenodo record:

Hemmi, R., & Kikuchi, H. (2026).
Supplementary Files for "Scale-dependent gravity-referenced slopes on Phobos
using diffusion-smoothed shape models with recomputed effective gravity."
Zenodo.
https://doi.org/10.5281/zenodo.22067338


LICENSE
-------
Creative Commons Attribution 4.0 International (CC BY 4.0)

GFandSlope is external software, is distributed separately under its own license,
and is not redistributed as part of this Zenodo record.


CONTACT
-------
Ryodo Hemmi
Institute of Space and Astronautical Science
Japan Aerospace Exploration Agency (JAXA/ISAS)
hemmi.ryodo@jaxa.jp
