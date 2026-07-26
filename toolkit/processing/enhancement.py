"""Phase 3: brightness / contrast / gamma, histogram equalization, CLAHE."""

import cv2
import numpy as np


def adjust_brightness_contrast_gamma(img, brightness=0, contrast=1.0, gamma=1.0):
    """
    brightness: -100..100 (added to every pixel)
    contrast:   0.5..2.0  (multiplied into every pixel, around 0)
    gamma:      0.1..3.0  (power-law tone curve; 1.0 = no change)
    """
    adjusted = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)

    if abs(gamma - 1.0) > 1e-3:
        inv_gamma = 1.0 / gamma
        table = np.array(
            [((i / 255.0) ** inv_gamma) * 255 for i in range(256)]
        ).astype("uint8")
        adjusted = cv2.LUT(adjusted, table)

    return adjusted


def histogram_equalization(img):
    """Equalize contrast. Color images are equalized on luminance only
    (via YCrCb) so hue/saturation aren't distorted."""
    if img.ndim == 2:
        return cv2.equalizeHist(img)

    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)


def clahe(img, clip_limit=2.0, tile_grid_size=(8, 8)):
    """Contrast-Limited Adaptive Histogram Equalization — the standard
    choice for X-ray/CT, since it adapts to local contrast instead of
    equalizing the whole image at once (which over/under-corrects
    regions with very different local contrast)."""
    clahe_obj = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    if img.ndim == 2:
        return clahe_obj.apply(img)

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    lab[:, :, 0] = clahe_obj.apply(lab[:, :, 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
