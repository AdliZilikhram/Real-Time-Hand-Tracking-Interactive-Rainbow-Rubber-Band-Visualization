# HandSync AI 🖐️🌈

**Real-Time Hand Tracking & Interactive Rainbow Rubber Band Visualization**

HandSync AI is a computer vision project that uses real-time hand tracking to create an interactive rainbow rubber-band visualization. By detecting hand landmarks and tracking individual fingertips, the system generates a continuous, colourful surface that responds dynamically to hand movements.

## ✨ Features

- **Real-Time Hand Detection:** Detects and tracks left and right hands using MediaPipe.
- **21 Hand Landmarks:** Tracks key points across each detected hand.
- **Finger State Detection:** Identifies extended and folded fingers using joint-angle calculations.
- **Adaptive Hand Tracking:** Continues generating the rubber band even when only one hand is visible.
- **Continuous Rubber Band:** Connects active fingertips into one continuous closed shape.
- **Rainbow Gradient:** Generates colourful gradients using HSV colour mapping.
- **Two-Sided Colour Effect:** Creates contrasting colour regions across the rubber-band surface.
- **Transparent Surface:** Uses alpha blending to preserve visibility of the webcam background.
- **Smooth Animation:** Applies coordinate smoothing and curved polygon interpolation.
- **Glow Effect:** Adds a neon-inspired visual appearance.

## 🛠️ Technologies

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| MediaPipe | Hand detection and landmark tracking |
| OpenCV | Webcam processing and visualisation |
| NumPy | Mathematical calculations and coordinate processing |
| HSV Colour Space | Rainbow gradient generation |

## 🏗️ System Architecture

1. Webcam captures live video frames.
2. MediaPipe detects hands and extracts 21 landmarks.
3. Finger detection calculates joint angles to determine finger states.
4. Active fingertips are collected from available hands.
5. The rubber-band generator creates a continuous closed curve.
6. The rendering engine applies gradient colours, transparency and glowing effects.
7. OpenCV displays the final visualisation in real time.

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/HandSync-AI.git
```

### 2. Navigate into the project

```bash
cd HandSync-AI
```

### 3. Create a virtual environment

```bash
python -m venv project_env
```

### 4. Activate the environment

Windows PowerShell:

```powershell
.\project_env\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python main.py
```

Press `Q` to close the application.

## 📸 Preview

Add your application screenshot or demonstration GIF here.

```markdown
![HandSync AI Demo](assets/demo.png)
```

## 🔬 Computer Vision Concepts

This project explores several important concepts:

- Hand landmark detection
- Joint-angle calculation
- Coordinate transformations
- Real-time image processing
- Polygon masking
- HSV colour mapping
- Alpha blending
- Curve interpolation
- Position smoothing

## 🗺️ Future Improvements

- [ ] PyQt5 desktop graphical interface
- [ ] Advanced fingertip proximity detection
- [ ] Realistic elastic deformation
- [ ] Liquid ripple animation
- [ ] Floating rainbow particles
- [ ] Dynamic lighting
- [ ] Advanced gesture recognition
- [ ] Performance optimisation

## 🎯 Project Objective

The objective of HandSync AI is to explore how computer vision, mathematical algorithms and interactive graphics can be combined to create an engaging real-time hand-tracking application.

## 👨‍💻 Author

**Mohamad Adli Zilikhram Bin Saharudin**

Interested in Artificial Intelligence, Computer Vision, Machine Learning and Software Development.

---

*HandSync AI – Connecting movement with creativity.*
