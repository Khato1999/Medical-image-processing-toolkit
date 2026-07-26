import cv2
from .edges import to_gray
import numpy as np


def threshold_segmentation(image, threshold=128):
    gray = to_gray(image)
    _, segmented = cv2.threshold(
        gray,
        threshold,
        255,
        cv2.THRESH_BINARY
    )
    return segmented

def otsu_segmentation(image):
    gray = to_gray(image)

    _, segmented = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return segmented

def adaptive_threshold(image):

    gray = to_gray(image)

    return cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

def detect_contours(image):

    gray = to_gray(image)

    contours, _ = cv2.findContours(
        gray,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    output = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    cv2.drawContours(
        output,
        contours,
        -1,
        (0,255,0),
        2
    )

    return output

def contour_area(image):

    gray = to_gray(image)

    contours,_ = cv2.findContours(
        gray,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    areas=[]

    for c in contours:
        areas.append(cv2.contourArea(c))

    return areas


# --- UI-facing compatibility wrappers -------------------------------------------------

def threshold(image, threshold=128):
    """Compatibility wrapper: UI expects analysis.threshold
    Delegates to threshold_segmentation.
    """
    return threshold_segmentation(image, threshold=threshold)


def otsu(image):
    """Compatibility wrapper for Otsu's method."""
    return otsu_segmentation(image)


def connected_components(image):
    """Compute connected components and return a colored label image.
    The function converts the input to grayscale, thresholds it using Otsu,
    labels connected components, and maps labels to pseudo-colors for display.
    """
    gray = to_gray(image)
    # Binary image via Otsu
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)

    # Map labels to colors deterministically
    h, w = labels.shape
    out = np.zeros((h, w, 3), dtype=np.uint8)
    if num_labels <= 1:
        return out

    # Generate simple color map
    labels_uint = labels.astype(np.int32)
    r = (labels_uint * 37) % 255
    g = (labels_uint * 57) % 255
    b = (labels_uint * 97) % 255
    out[..., 2] = r.astype(np.uint8)  # R
    out[..., 1] = g.astype(np.uint8)  # G
    out[..., 0] = b.astype(np.uint8)  # B

    # Make background (label 0) black
    out[labels == 0] = 0
    return out


def erode(image, ksize=3):
    gray = to_gray(image)
    kernel = np.ones((ksize, ksize), dtype=np.uint8)
    return cv2.erode(gray, kernel)


def dilate(image, ksize=3):
    gray = to_gray(image)
    kernel = np.ones((ksize, ksize), dtype=np.uint8)
    return cv2.dilate(gray, kernel)


def opening(image, ksize=3):
    gray = to_gray(image)
    kernel = np.ones((ksize, ksize), dtype=np.uint8)
    return cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)


def closing(image, ksize=3):
    gray = to_gray(image)
    kernel = np.ones((ksize, ksize), dtype=np.uint8)
    return cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

