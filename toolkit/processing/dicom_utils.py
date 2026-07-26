import pydicom
import cv2 
import numpy as np
def load_dicom(path):

    ds = pydicom.dcmread(path)

    image = ds.pixel_array

    image = cv2.normalize(
        image,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    image = image.astype("uint8")

    return image, ds

def apply_window(image,
                 center,
                 width):

    low = center - width//2
    high = center + width//2

    image = np.clip(image, low, high)

    image = (
        image-low
    )/(high-low)

    image*=255

    return image.astype(np.uint8)