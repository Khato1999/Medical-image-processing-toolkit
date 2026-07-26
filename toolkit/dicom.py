"""
DICOM utilities
"""

import cv2
import numpy as np
import pydicom


def load_dicom(filename):
    """
    Read a DICOM image.

    Returns
    -------
    image
    dataset
    """

    ds = pydicom.dcmread(filename)

    image = ds.pixel_array.astype(np.float32)

    image -= image.min()

    if image.max() > 0:
        image /= image.max()

    image *= 255

    image = image.astype(np.uint8)

    if image.ndim == 2:
        return image, ds

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return image, ds


def metadata(ds):

    fields = [
        "PatientName",
        "PatientID",
        "PatientSex",
        "PatientAge",
        "StudyDate",
        "StudyDescription",
        "SeriesDescription",
        "Modality",
        "Manufacturer",
        "InstitutionName",
        "Rows",
        "Columns",
        "SliceThickness",
        "PixelSpacing",
        "WindowCenter",
        "WindowWidth",
    ]

    info = {}

    for field in fields:

        if hasattr(ds, field):
            info[field] = str(getattr(ds, field))
        else:
            info[field] = "N/A"

    return info


def window_level(image, center, width):

    image = image.astype(np.float32)

    low = center - width / 2
    high = center + width / 2

    image = np.clip(image, low, high)

    image -= low

    image /= width

    image *= 255

    return image.astype(np.uint8)