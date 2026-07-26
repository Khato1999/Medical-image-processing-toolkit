"""
Measurement functions for the Medical Image Processing Toolkit.

Phase 8
-------
• ROI Statistics
• Histogram
• Distance Measurement
• Area Measurement
"""

import cv2
import numpy as np


# --------------------------------------------------------
# Utility
# --------------------------------------------------------

def to_gray(image):
    """
    Convert image to grayscale if needed.
    """
    if image.ndim == 2:
        return image

    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# --------------------------------------------------------
# ROI Statistics
# --------------------------------------------------------

def roi_statistics(image):
    """
    Compute statistics of an image or ROI.

    Returns
    -------
    dict
    """

    gray = to_gray(image)

    return {
        "Mean": float(np.mean(gray)),
        "Median": float(np.median(gray)),
        "Minimum": int(np.min(gray)),
        "Maximum": int(np.max(gray)),
        "Range": int(np.max(gray) - np.min(gray)),
        "Standard deviation": float(np.std(gray)),
        "Variance": float(np.var(gray)),
        "Pixels": int(gray.size),
    }


# --------------------------------------------------------
# Histogram
# --------------------------------------------------------

def histogram(image):
    """
    Compute a 256-bin histogram.

    Returns
    -------
    numpy.ndarray
    """

    gray = to_gray(image)

    hist = cv2.calcHist(
        [gray],
        [0],
        None,
        [256],
        [0, 256],
    )

    return hist.flatten()


# --------------------------------------------------------
# Distance Measurement
# --------------------------------------------------------

def distance(point1, point2):
    """
    Euclidean distance between two points.

    Parameters
    ----------
    point1 : (x,y)
    point2 : (x,y)

    Returns
    -------
    float
    """

    x1, y1 = point1
    x2, y2 = point2

    return float(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))


# --------------------------------------------------------
# Polygon Area
# --------------------------------------------------------

def polygon_area(points):
    """
    Area of a polygon using OpenCV.

    Parameters
    ----------
    points : list[(x,y)]

    Returns
    -------
    float
    """

    if len(points) < 3:
        return 0.0

    pts = np.array(points, dtype=np.float32)

    return float(cv2.contourArea(pts))


# --------------------------------------------------------
# Rectangle Area
# --------------------------------------------------------

def rectangle_area(width, height):
    """
    Rectangle area.

    Returns
    -------
    int
    """

    return int(width * height)


# --------------------------------------------------------
# Bounding Box
# --------------------------------------------------------

def bounding_box(points):
    """
    Bounding rectangle around a polygon.

    Returns
    -------
    (x, y, w, h)
    """

    pts = np.array(points)

    return cv2.boundingRect(pts)


# --------------------------------------------------------
# Centroid
# --------------------------------------------------------

def centroid(points):
    """
    Compute centroid of polygon.

    Returns
    -------
    (cx, cy)
    """

    pts = np.array(points)

    m = cv2.moments(pts)

    if m["m00"] == 0:
        return (0, 0)

    cx = int(m["m10"] / m["m00"])
    cy = int(m["m01"] / m["m00"])

    return (cx, cy)


# --------------------------------------------------------
# Min / Max Pixel Position
# --------------------------------------------------------

def min_max_locations(image):
    """
    Find minimum and maximum intensity values and locations.

    Returns
    -------
    min_value
    max_value
    min_location
    max_location
    """

    gray = to_gray(image)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray)

    return (
        min_val,
        max_val,
        min_loc,
        max_loc,
    )


# --------------------------------------------------------
# Image Information
# --------------------------------------------------------

def image_information(image):
    """
    Returns useful image information.

    Returns
    -------
    dict
    """

    h, w = image.shape[:2]

    channels = 1 if image.ndim == 2 else image.shape[2]

    return {
        "Width": w,
        "Height": h,
        "Channels": channels,
        "Pixels": h * w,
    }