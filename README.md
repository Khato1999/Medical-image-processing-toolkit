# <img width="1254" height="1254" alt="my_logo" src="https://github.com/user-attachments/assets/5127791b-d75f-419f-963e-92b76f58616f" />
 Medical Image Processing Toolkit

A desktop application for medical image processing built with **Python**, **PyQt6**, **OpenCV**, and **NumPy**.

The toolkit provides a user-friendly graphical interface for loading medical images, applying image processing algorithms, analyzing image quality, and experimenting with classical computer vision techniques.

---

## Features

### Phase 1 – Image Viewer
- Open medical images
- Side-by-side Original and Processed view
- Image information display
- Save processed images

### Phase 2 – Basic Processing
- Grayscale conversion
- Resize
- Rotate
- Horizontal/Vertical flip
- Interactive crop

### Phase 3 – Image Enhancement
- Brightness adjustment
- Contrast adjustment
- Gamma correction
- Histogram Equalization
- CLAHE (Contrast Limited Adaptive Histogram Equalization)

### Phase 4 – Image Filtering
- Gaussian Blur
- Median Blur
- Average Blur
- Bilateral Filter
- Sharpen
- Emboss

### Phase 5 – Edge Detection
- Sobel
- Scharr
- Laplacian
- Canny Edge Detection
- Adjustable Canny Thresholds

### Phase 6 – Image Analysis
- Binary Thresholding
- Adaptive Thresholding
- Otsu Thresholding

### Phase 7 – Morphological Operations
- Erosion
- Dilation
- Opening
- Closing
- Connected Components

### Phase 8 – Image Measurements
- Histogram Visualization
- Image Statistics
  - Mean
  - Standard Deviation
  - Minimum
  - Maximum
  - Median

### Phase 9 – Region Analysis
- Contour Detection
- Area Measurement
- Perimeter Measurement
- Bounding Boxes

### Phase 10 – Frequency Domain Processing
- Fourier Transform
- Magnitude Spectrum
- Low-pass Filter
- High-pass Filter

### Phase 11 – Image Registration
- Feature Detection
- Feature Matching
- Image Alignment
- Homography Estimation

---

## Technologies Used

- Python 3
- PyQt6
- OpenCV
- NumPy
- Matplotlib

---

## Installation

Clone the repository

```bash
git clone https://github.com/Khato1999/Medical-image-processing-toolkit.git
```

Move into the project

```bash
cd Medical-image-processing-toolkit
```

Install the required packages

```bash
pip install -r requirements.txt
```

Run the application

```bash
python main.py
```

---

## Project Structure

```
Medical-image-processing-toolkit/
│
├── main.py
├── README.md
├── requirements.txt
│
└── toolkit/
    ├── __init__.py
    ├── widgets.py
    ├── main_window.py
    │
    └── processing/
        ├── __init__.py
        ├── basic.py
        ├── enhancement.py
        ├── filters.py
        ├── edges.py
        ├── analysis.py
        ├── morphology.py
        ├── measurements.py
        ├── frequency.py
        └── registration.py
```

---

## Example Workflow

1. Open an image.
2. Apply preprocessing (crop, rotate, resize).
3. Improve contrast using CLAHE.
4. Remove noise using Gaussian or Bilateral filtering.
5. Detect edges.
6. Segment objects.
7. Analyze regions.
8. Measure image statistics.
9. Apply frequency-domain filtering.
10. Register multiple images.

---

## Future Improvements

- 3D image visualization
- Volume rendering
- More medical segmentation algorithms
- Deep Learning integration
- GPU acceleration
- Batch processing
- Plugin system

---

## Educational Purpose

This project was developed as a learning project to explore medical image processing concepts including:

- Computer Vision
- Digital Image Processing
- Medical Imaging
- GUI Development
- Python Software Engineering

---

## License

This project is released under the MIT License.

---

## Author

**Khato**

Biomedical Engineering Student  
Eindhoven University of Technology (TU/e)

GitHub:
https://github.com/Khato1999
