# Glioblastoma fluorescence analysis

Python microscopy workflow accompanying *Functional genomic profiling identifies Mitochondrial Complex I as a determinant of regorafenib response in glioblastoma* (Salbini, Formato and colleagues).

This repository extracts Olympus VSI scenes, defines a fluorescence-derived mask using one reference channel, and measures maximum, minimum, and mean intensity in every channel within that mask. 

## Scope and relationship to the manuscript

The supplied notebook reports raw per-channel intensity measurements within a shared mask; it does not perform GFP/DAPI normalization.

Channel 1 (zero-based, the second channel) was GFP in the original dataset and remains the default (`MASK_CHANNEL = 1`). For other datasets, verify the acquisition channel mapping and set `MASK_CHANNEL` to the appropriate reference channel. With GFP as the reference, the mask is GFP-derived and does not necessarily cover all tissue.

## Repository contents

```text
analysis.ipynb                           Main sequential workflow
glioblastoma_analysis/
   segmentation.py                      Reference-channel segmentation function
   plotting.py                          Overlay and saved contour functions
   pipeline.py                          VSI/TIFF handling and intensity measurements
requirements.txt                        Exact direct dependency versions
environment.yml                        Conda environment with Python 3.12
```


## Installation

Use Python 3.12, matching the original notebook's Python minor version. From the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --prefix "$VIRTUAL_ENV" --name glioblastoma-fluorescence-analysis --display-name "Glioblastoma fluorescence analysis"
python -m jupyterlab analysis.ipynb
```

On Windows, activate with `.venv\Scripts\activate` and use `%VIRTUAL_ENV%` instead of `$VIRTUAL_ENV` in Command Prompt.

Alternatively, from the repository root:

```bash
conda env create -f environment.yml
conda activate glioblastoma-fluorescence-analysis
python -m jupyterlab analysis.ipynb
```

Select the environment's Python kernel in JupyterLab. SlideIO contains native components; installation requires a compatible wheel for the operating system and Python version. See the [SlideIO package documentation](https://pypi.org/project/slideio/2.7.2/).

## Input data and execution

1. Set `INPUT_DIR` to the folder where the vsi images to analyze are located.
2. Open `analysis.ipynb` from the repository root and configure `INPUT_DIR`, `OUTPUT_DIR`, and `MASK_CHANNEL`.
3. Leave `FILENAMES = None` to process all `.vsi` files in sorted order, or supply an explicit filename list for a subset.
4. Run all cells. Inspect the saved mask contours before accepting measurements.

Scenes are read at full resolution and must have shape height × width × channels. Each scene must contain the mask channel. Memory use scales with the full scene size; TIFF exports are uncompressed and can require substantial disk space. Only the largest connected component of the segmented reference-channel signal is retained. With GFP as the reference, this can exclude disconnected GFP-positive regions; inspect the mask before interpreting the measurements. 

By default the workflow exports TIFFs, saves contour previews and writes measurements in one pass. Set `USE_SAVED_TIFFS = True` to remeasure exported TIFFs; original VSI files remain necessary to identify scenes and channel counts. Use a distinct output folder for each dataset/run: matching output filenames and the final CSV are overwritten. 

## Algorithm and outputs

For each scene, the reference channel is smoothed with Gaussian sigma 1 using scikit-image's original default intensity conversion. Otsu thresholding creates a mask, objects smaller than 8,000 pixels and holes smaller than 8,000 pixels are removed, the largest connected component is retained, and binary closing uses a disk of radius 5 pixels. All these parameters can be changed and adapted in `segmentation.py`.

The resulting mask is applied to **original, unsmoothed** intensities for all channels. Channel export order remains descending. 

Outputs in `OUTPUT_DIR`:

- `<stem>_scene_<n>_channel_<c>.tif`: original channel pixels.
- `<stem>_scene_<n>_channel_<c>_MASK.png`: mask contour for visual review; these are previews, not binary mask files.
- `results.csv`: one row per input file, scene and channel.

| Column | Meaning |
| --- | --- |
| `Image` | Source VSI filename |
| `Image_name` | Exported channel TIFF filename, encoding scene and channel |
| `Intensity_max` | Maximum raw intensity inside the shared mask |
| `Intensity_min` | Minimum raw intensity inside the shared mask |
| `Mean_intensity` | Mean raw intensity inside the shared mask |


