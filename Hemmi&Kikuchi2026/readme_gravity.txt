Gravity-calculation reproduction notes
=======================================

WORKFLOW
--------
The final effective-gravity, gravity-referenced slope, and downslope-azimuth
products used in the paper were generated in three stages:

1. GFandSlope was used to calculate shape-derived self-gravity for each Phobos
   shape model. Under the adopted mesh convention, GravAcc in the GFandSlope
   output is directed outward.

2. The accompanying wrapper in NoSpin_result_TA000_scripts_package/ read the
   GFandSlope output, reversed the sign of GravAcc to obtain the inward
   self-gravity acceleration, and added centrifugal, Euler, and Martian tidal
   accelerations. In compact notation,

       g_total = -GravAcc + g_centrifugal + g_Euler + g_tide

3. The same wrapper calculated and wrote the final total effective-gravity
   vector (g_total), gravity-referenced slope, and downslope azimuth for every
   facet.

GFandSlope was intentionally run with:

    period: 0.0

because rotation was not applied inside the GFandSlope self-gravity calculation.
Rotational acceleration was added explicitly in the subsequent wrapper stage.


NOTE ON FILE NAMES
------------------
Some intermediate files generated or supplied during the gravity-calculation
workflow contain the legacy string "NoSpin" in their filenames.

These original filenames are retained in this archive for provenance and to keep
the archived workflow consistent with the actual processing history.

Despite the legacy "NoSpin" naming, the final calculations used in the study
include centrifugal and Euler accelerations. The final products also include
the Martian tidal acceleration.


NOTE ON period: 0.0
-------------------
The GFandSlope configuration used:

    period: 0.0

Rotation-related acceleration terms were not applied within GFandSlope.

Centrifugal and Euler accelerations were evaluated separately by the subsequent
wrapper using:

    |omega| = 2.2348606662528733e-4 rad/s
    |omega_dot| approximately 1.0386e-11 rad/s^2

The angular acceleration used in the Euler term was calculated by a centered
finite difference of the SPICE-derived angular velocity evaluated 1 s before
and 1 s after the nominal epoch. The wrapper also added the Martian tidal
acceleration.

Therefore, the final effective-gravity, gravity-referenced slope, and
downslope-azimuth products include rotation despite the period: 0.0 setting in
the GFandSlope configuration.


GFANDSLOPE CONFIGURATION
------------------------
For each model, the GFandSlope configuration used the following settings:

    period: 0.0
    density: 1862.297786 kg/m^3
    input_points: NONE
    gpu: 0

The input polygon and output paths vary with model scale and are
generated from gfandslope.cfg.template by run_gfandslope.sh.

The GFandSlope stage was applied to the complete model sequence used in the
paper. The scale labels are:

    18, 80, 100, 125, 150, 175, 200, 250, 500, 1000, 2000 m

The 18 m case is the native unsmoothed reference. It has no assigned e-fold
smoothing wavelength L; 18 m denotes its approximate mean facet-edge scale.
The remaining cases are volume-preserved diffusion-smoothed models generated
independently from the native model at:

    L = 80, 100, 125, 150, 175, 200, 250, 500, 1000, 2000 m

The archived run_gfandslope.sh is an illustrative single-model example. Edit
its input and output paths, or adapt it into a loop, to process the complete
model sequence.


GFANDSLOPE SOURCE REVISION
--------------------------
GFandSlope repository:

    https://github.com/AiGIS-PyAiGIS/GFandSlope

GFandSlope commit used:

    c75f8dcafb38c08f6da74806adbb70f212bd9066

The local working tree differed from the repository only in executable file
permissions; no source-code content modifications were present in the files used
for the calculations.


ORIGINAL EXECUTION ENVIRONMENT
------------------------------
The original GFandSlope calculations were run under WSL with:

    GPU: NVIDIA RTX A4500
    GPU compute capability: 8.6
    CUDA Toolkit: 12.6
    nvcc: V12.6.85

GFandSlope was built with:

    cd ~/GFandSlope/src
    make

The OBJ mesh was converted to the GFandSlope polygon input format using the
utility distributed with GFandSlope:

    python util/Mesh2GFandSlopeInput.py <input.obj>


CONFIGURATION TEMPLATE
----------------------
gfandslope.cfg.template contains:

    period: @PERIOD@
    density: @DENSITY@
    input_polygon: @INPUT_POLYGON@
    input_points: NONE
    output: @OUTPUT@
    gpu: @GPU_ID@

run_gfandslope.sh substitutes the values and paths required for the selected
model and writes the corresponding work/v004_<scale>.cfg file immediately
before execution.


USAGE
-----
Assuming the GFandSlope repository and the Phobos OBJ products are located at:

    ~/GFandSlope
    ~/phobos_slope

run:

    chmod +x run_gfandslope.sh
    ./run_gfandslope.sh

Optional paths and parameters can be overridden through the environment
variables documented in run_gfandslope.sh.

For the selected scale label, the script generates:

    work/v004_<scale>.obj.txt
    work/v004_<scale>.cfg
    work/v004_<scale>_surface.txt

The temporary work/v004_<scale>.obj symbolic link is removed after successful
execution.


SUBSEQUENT EFFECTIVE-GRAVITY PROCESSING
---------------------------------------
The GFandSlope output represents the self-gravity stage of the workflow.

After GFandSlope, run the accompanying gravity wrapper included in this archive.
That stage adds:

    centrifugal acceleration
    Euler acceleration
    Martian tidal acceleration

and produces the final:

    total effective-gravity vector (g_total)
    gravity-referenced slope
    downslope azimuth

The nominal orbital geometry used in the study is:

    true anomaly: 0 degrees
    epoch UTC: 2029 JAN 01 04:27:47.401

The final facet-level products are distributed in the Zenodo record as 11
separate gzip-compressed CSV files:

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

The 0018 file is the native unsmoothed reference; the other files correspond
to the applied smoothing wavelengths. Each file retains commented metadata
headers containing calculation parameters such as the adopted density, Mars
distance and direction, angular velocity, epoch, and true anomaly.

The accompanying wrapper package contains:

    NoSpin_result_TA000_scripts_package/
      README_NoSpin_result_TA000_scripts.md
      requirements_NoSpin_result_TA000.txt
      input/ (empty)
      script/make_NoSpin_result_TA000.py
      script/run_make_NoSpin_result_TA000.sh
      spice/ (SPICE kernels required by the wrapper)

The wrapper is run with --alpha-dt 1.0 by default, corresponding to the centered
finite difference described above.

GFandSlope alone is therefore not sufficient to reproduce the final products
reported in the paper; the accompanying gravity wrapper must also be applied.
