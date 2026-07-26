"""Phase 5: Sobel, Scharr, Laplacian, Canny edge detection."""

import cv2


def to_gray(img):
    """Edge detectors operate on single-channel intensity gradients, so
    color images are converted to grayscale first."""
    return img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def sobel(img):
    gray = to_gray(img)
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = cv2.magnitude(gx, gy)
    return cv2.convertScaleAbs(magnitude)


def scharr(img):
    """Same idea as Sobel, but with the more rotation-accurate 3x3
    Scharr kernel."""
    gray = to_gray(img)
    gx = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
    gy = cv2.Scharr(gray, cv2.CV_64F, 0, 1)
    magnitude = cv2.magnitude(gx, gy)
    return cv2.convertScaleAbs(magnitude)


def laplacian(img):
    gray = to_gray(img)
    lap = cv2.Laplacian(gray, cv2.CV_64F, ksize=3)
    return cv2.convertScaleAbs(lap)


def canny(img, threshold1, threshold2):
    gray = to_gray(img)
    return cv2.Canny(gray, threshold1, threshold2)
