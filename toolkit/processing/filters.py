"""Phase 4: Gaussian/median/bilateral/average blur, sharpen, emboss."""

import cv2
import numpy as np

SHARPEN_KERNEL = np.array([
    [0, -1, 0],
    [-1, 5, -1],
    [0, -1, 0],
], dtype=np.float32)

EMBOSS_KERNEL = np.array([
    [-2, -1, 0],
    [-1, 1, 1],
    [0, 1, 2],
], dtype=np.float32)


def gaussian_blur(img, ksize):
    """ksize: 3, 5, or 7."""
    return cv2.GaussianBlur(img, (ksize, ksize), 0)


def median_blur(img, ksize=5):
    """Good at removing salt-and-pepper style noise while keeping edges
    sharper than a comparable Gaussian blur."""
    return cv2.medianBlur(img, ksize)


def bilateral_filter(img, d=9, sigma_color=75, sigma_space=75):
    """Edge-preserving smoothing — denoises flat regions while keeping
    sharp boundaries, useful when you don't want to blur away
    anatomical edges."""
    return cv2.bilateralFilter(img, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)


def average_blur(img, ksize=(5, 5)):
    """Plain box filter."""
    return cv2.blur(img, ksize)


def sharpen(img):
    return cv2.filter2D(img, -1, SHARPEN_KERNEL)


def emboss(img):
    """delta=128 recenters the (mostly negative/near-zero) convolution
    result onto a mid-gray background instead of clipping to black."""
    return cv2.filter2D(img, -1, EMBOSS_KERNEL, delta=128)
