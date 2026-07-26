"""
registration.py

Phase 11
Image Registration

Functions:
- register_ecc()
- orb_matches()
- draw_matches()

Author: Khato
"""

import cv2
import numpy as np


def _to_gray(image):
    """Convert image to grayscale if necessary."""
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# ==========================================================
# ECC REGISTRATION
# ==========================================================

def register_ecc(reference, moving):
    """
    Align moving image to reference image using
    Enhanced Correlation Coefficient (ECC).

    Returns
    -------
    aligned_image
    warp_matrix
    correlation
    """

    ref_gray = _to_gray(reference)
    mov_gray = _to_gray(moving)

    warp_matrix = np.eye(2, 3, dtype=np.float32)

    criteria = (
        cv2.TERM_CRITERIA_EPS |
        cv2.TERM_CRITERIA_COUNT,
        100,
        1e-6,
    )

    try:

        cc, warp_matrix = cv2.findTransformECC(
            ref_gray,
            mov_gray,
            warp_matrix,
            cv2.MOTION_EUCLIDEAN,
            criteria,
        )

        aligned = cv2.warpAffine(
            moving,
            warp_matrix,
            (reference.shape[1], reference.shape[0]),
            flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
        )

        return aligned, warp_matrix, cc

    except cv2.error:

        return moving.copy(), warp_matrix, 0.0


# ==========================================================
# ORB FEATURE MATCHING
# ==========================================================

def orb_matches(image1, image2, max_features=1000):

    gray1 = _to_gray(image1)
    gray2 = _to_gray(image2)

    orb = cv2.ORB_create(max_features)

    kp1, des1 = orb.detectAndCompute(gray1, None)
    kp2, des2 = orb.detectAndCompute(gray2, None)

    if des1 is None or des2 is None:
        return kp1, kp2, []

    matcher = cv2.BFMatcher(
        cv2.NORM_HAMMING,
        crossCheck=True,
    )

    matches = matcher.match(des1, des2)

    matches = sorted(
        matches,
        key=lambda x: x.distance,
    )

    return kp1, kp2, matches


# ==========================================================
# DRAW MATCHES
# ==========================================================

def draw_matches(
    image1,
    image2,
    kp1,
    kp2,
    matches,
    max_matches=50,
):
    """
    Draw feature correspondences.
    """

    output = cv2.drawMatches(
        image1,
        kp1,
        image2,
        kp2,
        matches[:max_matches],
        None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    )

    return output


# ==========================================================
# AFFINE REGISTRATION
# ==========================================================

def affine_registration(reference, moving):

    kp1, kp2, matches = orb_matches(reference, moving)

    if len(matches) < 3:
        return moving.copy()

    src_pts = np.float32(
        [
            kp2[m.trainIdx].pt
            for m in matches
        ]
    ).reshape(-1, 1, 2)

    dst_pts = np.float32(
        [
            kp1[m.queryIdx].pt
            for m in matches
        ]
    ).reshape(-1, 1, 2)

    matrix, _ = cv2.estimateAffine2D(
        src_pts,
        dst_pts,
    )

    if matrix is None:
        return moving.copy()

    aligned = cv2.warpAffine(
        moving,
        matrix,
        (
            reference.shape[1],
            reference.shape[0],
        ),
    )

    return aligned


# ==========================================================
# HOMOGRAPHY REGISTRATION
# ==========================================================

def perspective_registration(reference, moving):

    kp1, kp2, matches = orb_matches(reference, moving)

    if len(matches) < 4:
        return moving.copy()

    src_pts = np.float32(
        [
            kp2[m.trainIdx].pt
            for m in matches
        ]
    ).reshape(-1, 1, 2)

    dst_pts = np.float32(
        [
            kp1[m.queryIdx].pt
            for m in matches
        ]
    ).reshape(-1, 1, 2)

    H, _ = cv2.findHomography(
        src_pts,
        dst_pts,
        cv2.RANSAC,
        5.0,
    )

    if H is None:
        return moving.copy()

    aligned = cv2.warpPerspective(
        moving,
        H,
        (
            reference.shape[1],
            reference.shape[0],
        ),
    )

    return aligned


# ==========================================================
# IMAGE DIFFERENCE
# ==========================================================

def registration_difference(reference, aligned):

    gray1 = _to_gray(reference)
    gray2 = _to_gray(aligned)

    return cv2.absdiff(gray1, gray2)
