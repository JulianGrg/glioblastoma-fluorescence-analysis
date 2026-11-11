"""Visual checks of the region used for quantification."""
import matplotlib.pyplot as plt
from skimage import measure

def plot_mask_overlay(image, mask, alpha=0.3):
    plt.figure(figsize=(8, 8))
    
    # Show original image
    plt.imshow(image, cmap='gray')
    
    # Overlay mask in red
    plt.imshow(mask, cmap='Reds', alpha=alpha)
    
    plt.title("Mask overlay (red = used for max intensity)")
    plt.axis('off')
    plt.show()

def plot_mask_contour(image, mask, output_path):
    plt.figure(figsize=(8, 8))
    plt.imshow(image, cmap='gray')

    contours = measure.find_contours(mask, 0.5)
    
    for contour in contours:
        plt.plot(contour[:, 1], contour[:, 0], linewidth=2, color='red')

    plt.title("Mask contour (used region)")
    plt.axis('off')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close()
