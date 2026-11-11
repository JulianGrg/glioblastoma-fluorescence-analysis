"""Export VSI channels and quantify intensities inside a shared tissue mask."""
from pathlib import Path
import numpy as np
import pandas as pd
import tifffile as tif
from .segmentation import get_sample_mask_and_max
from .plotting import plot_mask_contour

COLUMNS = ['Image', 'Image_name', 'Intensity_max', 'Intensity_min', 'Mean_intensity']


def analyze_scene(block, image_name, scene_num, output_dir, mask_channel=1,
                  save_tiffs=True, save_contours=True):
    """Analyze an H × W × C scene; mask channel is a zero-based index.

    Statistics use original intensities, not the smoothed segmentation image.
    The same mask is applied to every channel. Population standard deviation
    remains available from get_sample_mask_and_max but is not in the legacy CSV.
    """
    if block.ndim != 3:
        raise ValueError(f'Expected an H x W x C scene; got {block.shape}')
    if not 0 <= mask_channel < block.shape[-1]:
        raise ValueError(f'Mask channel {mask_channel} unavailable in {block.shape}')
    mask, *_ = get_sample_mask_and_max(block[:, :, mask_channel])
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for channel in range(block.shape[-1] - 1, -1, -1):
        image = block[:, :, channel]
        name = f'{Path(image_name).stem}_scene_{scene_num}_channel_{channel}'
        values = image[mask]
        if save_tiffs:
            tif.imwrite(output_dir / f'{name}.tif', image, compression=None)
        if save_contours:
            plot_mask_contour(image, mask, output_dir / f'{name}_MASK.png')
        rows.append([image_name, f'{name}.tif', values.max(), values.min(), values.mean()])
    return rows


def analyze_slides(input_dir, output_dir, filenames=None, mask_channel=1,
                   save_tiffs=True, save_contours=True, use_saved_tiffs=False):
    """Process all scenes of selected VSI files and write results_2.csv.

    If use_saved_tiffs=True, quantify previously exported TIFFs. The VSI files
    are still required to determine scene and channel counts. Existing output
    files with matching names are replaced. Use a separate directory per run.
    """
    import slideio
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    if not input_dir.is_dir():
        raise FileNotFoundError(f'Input directory does not exist: {input_dir}')
    paths = (sorted(input_dir.glob('*.vsi')) if filenames is None
             else [input_dir / name for name in filenames])
    if not paths:
        raise FileNotFoundError(f'No .vsi files selected in {input_dir}')
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in paths:
        print(f'Processing {path.name}')
        slide = slideio.open_slide(str(path), 'VSI')
        try:
            for scene_num in range(slide.num_scenes):
                scene = slide.get_scene(scene_num)
                if use_saved_tiffs:
                    block = np.stack([
                        tif.imread(output_dir / f'{path.stem}_scene_{scene_num}_channel_{ch}.tif')
                        for ch in range(scene.num_channels)
                    ], axis=-1)
                else:
                    block = scene.read_block()
                rows.extend(analyze_scene(
                    block, path.name, scene_num, output_dir, mask_channel,
                    save_tiffs and not use_saved_tiffs, save_contours))
                del block, scene
        finally:
            del slide
    results = pd.DataFrame(rows, columns=COLUMNS)
    results.to_csv(output_dir / 'results.csv', index=False)
    return results
