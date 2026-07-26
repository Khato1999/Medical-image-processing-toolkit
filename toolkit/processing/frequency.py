"""
frequency.py

Phase 10
Frequency Domain Processing

Functions
---------
fft_spectrum()
low_pass()
high_pass()
band_pass()
band_stop()
inverse_fft()

Author: Khato
"""

import cv2
import numpy as np


def _to_gray(image):
    """Convert image to grayscale if necessary."""
    if image.ndim == 2:
        return image

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


# ==========================================================
# FFT HELPERS
# ==========================================================

def compute_fft(image):
    """
    Compute centered FFT.

    Returns
    -------
    dft_shift : complex FFT centered at spectrum origin
    """

    gray = _to_gray(image)

    fft = np.fft.fft2(gray)

    return np.fft.fftshift(fft)


def inverse_fft(dft_shift):
    """
    Return image reconstructed from centered FFT.
    """

    shifted_back = np.fft.ifftshift(dft_shift)

    image_back = np.fft.ifft2(shifted_back)

    image_back = np.real(image_back)

    image_back = cv2.normalize(
        image_back,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    )

    return image_back.astype(np.uint8)

def fft_reconstruction(image):
    """
    FFT -> Inverse FFT

    Used to demonstrate perfect reconstruction.
    """

    dft_shift = compute_fft(image)

    return inverse_fft(
        dft_shift
    )

# ==========================================================
# FFT SPECTRUM
# ==========================================================

def fft_spectrum(image):
    """
    Create visualization of FFT magnitude spectrum.
    """

    dft_shift = compute_fft(image)

    magnitude = np.abs(dft_shift)

    magnitude = np.log(
        magnitude + 1
    )

    magnitude = cv2.normalize(
        magnitude,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    )

    return magnitude.astype(np.uint8)


def spectrum_from_fft(dft_shift):
    """
    Build a viewable magnitude-spectrum image directly from an
    already-computed centered FFT, instead of recomputing the FFT from
    an image. Used after masking part of dft_shift (e.g. the
    crop-to-zero-out-a-region interaction) so the display reflects the
    modified spectrum without needing the original image again.
    """

    magnitude = np.abs(dft_shift)

    magnitude = np.log(
        magnitude + 1
    )

    magnitude = cv2.normalize(
        magnitude,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    )

    return magnitude.astype(np.uint8)

# ==========================================================
# LOW PASS
# ==========================================================

def low_pass(image, radius=30):
    """
    Keep low frequencies only.
    Produces a blurred image.
    """

    dft_shift = compute_fft(image)

    rows, cols = dft_shift.shape

    crow = rows // 2
    ccol = cols // 2

    mask = np.zeros(
        (rows, cols),
        dtype=np.uint8,
    )

    cv2.circle(
        mask,
        (ccol, crow),
        radius,
        1,
        -1,
    )

    filtered = dft_shift * mask

    return inverse_fft(filtered)


# ==========================================================
# HIGH PASS
# ==========================================================

def high_pass(image, radius=30):
    """
    Remove low frequencies.
    Enhances edges and fine detail.
    """

    dft_shift = compute_fft(image)

    rows, cols = dft_shift.shape

    crow = rows // 2
    ccol = cols // 2

    mask = np.ones(
        (rows, cols),
        dtype=np.uint8,
    )

    cv2.circle(
        mask,
        (ccol, crow),
        radius,
        0,
        -1,
    )

    filtered = dft_shift * mask

    return inverse_fft(filtered)


# ==========================================================
# BAND PASS
# ==========================================================

def band_pass(
    image,
    inner_radius=20,
    outer_radius=60,
):
    """
    Keep only middle frequencies.
    Useful for texture analysis.
    """

    dft_shift = compute_fft(image)

    rows, cols = dft_shift.shape

    crow = rows // 2
    ccol = cols // 2

    mask = np.zeros(
        (rows, cols),
        dtype=np.uint8,
    )

    cv2.circle(
        mask,
        (ccol, crow),
        outer_radius,
        1,
        -1,
    )

    cv2.circle(
        mask,
        (ccol, crow),
        inner_radius,
        0,
        -1,
    )

    filtered = dft_shift * mask

    return inverse_fft(filtered)


# ==========================================================
# BAND STOP
# ==========================================================

def band_stop(
    image,
    inner_radius=20,
    outer_radius=60,
):
    """
    Remove a band of frequencies.
    Useful for periodic noise suppression.
    """

    dft_shift = compute_fft(image)

    rows, cols = dft_shift.shape

    crow = rows // 2
    ccol = cols // 2

    mask = np.ones(
        (rows, cols),
        dtype=np.uint8,
    )

    cv2.circle(
        mask,
        (ccol, crow),
        outer_radius,
        0,
        -1,
    )

    cv2.circle(
        mask,
        (ccol, crow),
        inner_radius,
        1,
        -1,
    )

    filtered = dft_shift * mask

    return inverse_fft(filtered)


# ==========================================================
# FILTERED FFT SPECTRUMS
# ==========================================================

def low_pass_spectrum(image, radius=30):

    dft_shift = compute_fft(image)

    rows, cols = dft_shift.shape

    mask = np.zeros(
        (rows, cols),
        dtype=np.uint8,
    )

    cv2.circle(
        mask,
        (cols // 2, rows // 2),
        radius,
        1,
        -1,
    )

    filtered = dft_shift * mask

    magnitude = np.log(
        np.abs(filtered) + 1
    )

    magnitude = cv2.normalize(
        magnitude,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    )

    return magnitude.astype(np.uint8)


def high_pass_spectrum(image, radius=30):

    dft_shift = compute_fft(image)

    rows, cols = dft_shift.shape

    mask = np.ones(
        (rows, cols),
        dtype=np.uint8,
    )

    cv2.circle(
        mask,
        (cols // 2, rows // 2),
        radius,
        0,
        -1,
    )

    filtered = dft_shift * mask

    magnitude = np.log(
        np.abs(filtered) + 1
    )

    magnitude = cv2.normalize(
        magnitude,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    )

    return magnitude.astype(np.uint8)