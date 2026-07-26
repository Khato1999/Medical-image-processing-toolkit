"""Phase 2: grayscale, resize, rotate, flip, crop."""

import cv2
import numpy as np

ROTATE_MAP = {
    90: cv2.ROTATE_90_CLOCKWISE,
    180: cv2.ROTATE_180,
    270: cv2.ROTATE_90_COUNTERCLOCKWISE,
}


def to_grayscale(img):
    """Convert a BGR image to single-channel grayscale.

    Caller is expected to check `img.ndim == 3` first (an already-gray
    image is passed straight through by cv2.cvtColor only if you use the
    right flag, so we keep the ndim check as a UI-level decision rather
    than silently no-op'ing here).
    """
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def resize_to_percent(img, orig_shape, pct):
    """Resize `img` to `pct`% of `orig_shape` (the *original* image's
    dimensions, not img's current dimensions) â€” so 50% always means half
    of the original size, regardless of prior edits."""
    orig_h, orig_w = orig_shape[:2]
    new_w = max(1, int(orig_w * pct / 100))
    new_h = max(1, int(orig_h * pct / 100))
    interp = cv2.INTER_AREA if pct < 100 else cv2.INTER_LINEAR
    return cv2.resize(img, (new_w, new_h), interpolation=interp)


def rotate(img, angle):
    """Rotate by 90, 180, or 270 degrees (clockwise)."""
    return cv2.rotate(img, ROTATE_MAP[angle])


def flip(img, mode):
    """mode: 'h' for horizontal, 'v' for vertical."""
    flip_code = 1 if mode == "h" else 0
    return cv2.flip(img, flip_code)


def crop(img, x1, y1, x2, y2):
    """Crop to the rectangle [x1, x2) x [y1, y2) in image pixel coords."""
    return img[y1:y2, x1:x2].copy()

def resize_current_percent(img, pct):
    """Resize relative to the current image dimensions."""
    h, w = img.shape[:2]
    new_w = max(1, int(w * pct / 100))
    new_h = max(1, int(h * pct / 100))
    interp = cv2.INTER_AREA if pct < 100 else cv2.INTER_CUBIC
    return cv2.resize(img, (new_w, new_h), interpolation=interp)


def fit_long_edge(img, max_size=512):
    """Resize so the longest edge equals max_size while preserving aspect ratio."""
    h, w = img.shape[:2]
    longest = max(h, w)
    if longest == 0:
        return img.copy()
    scale = max_size / longest
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
    return cv2.resize(img, (new_w, new_h), interpolation=interp)


def rotate_free(img, angle):
    """Rotate by any angle while expanding the canvas to avoid clipping."""
    h, w = img.shape[:2]
    center = (w / 2, h / 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    cos = abs(matrix[0, 0])
    sin = abs(matrix[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    matrix[0, 2] += (new_w / 2) - center[0]
    matrix[1, 2] += (new_h / 2) - center[1]

    return cv2.warpAffine(
        img,
        matrix,
        (new_w, new_h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )


def invert(img):
    """Invert image intensities."""
    return cv2.bitwise_not(img)


def normalize_intensity(img):
    """Stretch intensities to the full 0..255 display range."""
    normalized = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
    return normalized.astype(np.uint8)


def center_crop_square(img):
    """Crop the largest centered square from the image."""
    h, w = img.shape[:2]
    size = min(h, w)
    x1 = (w - size) // 2
    y1 = (h - size) // 2
    return img[y1:y1 + size, x1:x1 + size].copy()

