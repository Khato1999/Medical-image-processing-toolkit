"""
Reusable professional processing pipelines.

These functions compose the lower-level processing primitives into
clinically useful workflows while keeping every step deterministic and
side-effect free. UI code can call them as one-click presets, and future
batch/export features can reuse the same functions.
"""

import cv2
import numpy as np

from .processing.edges import to_gray


def _as_uint8(image):
    """Return an 8-bit display-safe image without changing valid uint8 data."""
    if image.dtype == np.uint8:
        return image.copy()

    normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
    return normalized.astype(np.uint8)


def _clahe_luminance(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    if image.ndim == 2:
        return clahe.apply(image)

    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def _unsharp_mask(image, amount=0.65, sigma=1.2):
    blurred = cv2.GaussianBlur(image, (0, 0), sigmaX=sigma, sigmaY=sigma)
    return cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)


def clean_contrast_detail(image):
    """General medical-image enhancement: denoise, local contrast, detail."""
    img = _as_uint8(image)
    denoised = cv2.bilateralFilter(img, d=7, sigmaColor=45, sigmaSpace=45)
    contrasted = _clahe_luminance(denoised, clip_limit=2.2, tile_grid_size=(8, 8))
    return _unsharp_mask(contrasted, amount=0.45, sigma=1.0)


def soft_tissue_window(image):
    """Conservative grayscale pipeline for CT/MRI-like soft-tissue viewing."""
    gray = to_gray(_as_uint8(image))
    denoised = cv2.medianBlur(gray, 3)
    contrasted = _clahe_luminance(denoised, clip_limit=1.8, tile_grid_size=(8, 8))
    return cv2.GaussianBlur(contrasted, (3, 3), 0)


def segmentation_ready(image):
    """Prepare a clean binary mask for ROI/connected-component analysis."""
    gray = to_gray(_as_uint8(image))
    denoised = cv2.GaussianBlur(gray, (5, 5), 0)
    enhanced = _clahe_luminance(denoised, clip_limit=2.0, tile_grid_size=(8, 8))
    _, mask = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((3, 3), dtype=np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)


def edge_review(image):
    """Edge-focused review image with stable contrast before Canny."""
    gray = to_gray(_as_uint8(image))
    denoised = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)
    enhanced = _clahe_luminance(denoised, clip_limit=2.0, tile_grid_size=(8, 8))
    edges = cv2.Canny(enhanced, 50, 150)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
