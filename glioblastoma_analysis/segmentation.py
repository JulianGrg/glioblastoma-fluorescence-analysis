"""Original tissue segmentation, with unchanged numerical parameters."""
import numpy as np
from skimage import filters, morphology, measure

def get_sample_mask_and_max(image):
    # 1. Smooth slightly (preserve structures)
    smoothed = filters.gaussian(image, sigma=1)

    # 2. Threshold (Otsu works well here)
    thresh = filters.threshold_otsu(smoothed)
    mask = smoothed > thresh

    # 3. Clean mask
    mask = morphology.remove_small_objects(mask, min_size=8000)
    mask = morphology.remove_small_holes(mask, area_threshold=8000)

    # 4. Keep largest connected component
    labeled = measure.label(mask)
    regions = measure.regionprops(labeled)
    
    if len(regions) == 0:
        raise ValueError("No sample detected")

    largest_region = max(regions, key=lambda r: r.area)
    mask = labeled == largest_region.label

    # Optional: smooth edges a bit
    mask = morphology.binary_closing(mask, morphology.disk(5))

    # 5. Extract max intensity
    max_intensity = image[mask].max()
    stddev = np.std(image[mask])
    min_intensity = image[mask].min()
    mean_intensity = image[mask].mean()

    return mask, max_intensity, stddev, min_intensity, mean_intensity
