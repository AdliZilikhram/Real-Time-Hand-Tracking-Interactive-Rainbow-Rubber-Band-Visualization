
import cv2
import mediapipe as mp
import numpy as np
import math
import colorsys


# ==========================================
# HANDSYNC AI - CONFIGURATION
# ==========================================

CAMERA_INDEX = 0
MAX_HANDS = 2

DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.7

FINGER_ANGLE_THRESHOLD = 150

SMOOTHING = 0.65

LINE_THICKNESS = 5
GLOW_STRENGTH = 25

FINGER_IDS = {
    "Thumb": (2, 3, 4),
    "Index": (5, 6, 7, 8),
    "Middle": (9, 10, 11, 12),
    "Ring": (13, 14, 15, 16),
    "Pinky": (17, 18, 19, 20)
}

# Ordered continuous loop
FINGER_ORDER = [
    ("Left", "Thumb"),
    ("Left", "Index"),
    ("Left", "Middle"),
    ("Left", "Ring"),
    ("Left", "Pinky"),
    ("Right", "Pinky"),
    ("Right", "Ring"),
    ("Right", "Middle"),
    ("Right", "Index"),
    ("Right", "Thumb")
]


# ==========================================
# MATHEMATICAL FUNCTIONS
# ==========================================

def calculate_angle(a, b, c):

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    denominator = (
        np.linalg.norm(ba) *
        np.linalg.norm(bc)
    )

    if denominator == 0:
        return 0

    cosine = np.dot(ba, bc) / denominator

    cosine = np.clip(cosine, -1.0, 1.0)

    return math.degrees(math.acos(cosine))


# ==========================================
# FINGER DETECTION
# ==========================================

def detect_finger_states(landmarks, width, height):

    points = [
        (int(p.x * width), int(p.y * height))
        for p in landmarks
    ]

    finger_states = {}

    for finger, ids in FINGER_IDS.items():

        if finger == "Thumb":
            a, b, c = ids
        else:
            a, b, c = ids[0], ids[1], ids[2]

        angle = calculate_angle(
            points[a],
            points[b],
            points[c]
        )

        finger_states[finger] = (
            angle > FINGER_ANGLE_THRESHOLD
        )

    return finger_states, points


# ==========================================
# SMOOTHING
# ==========================================

class PositionSmoother:

    def __init__(self, alpha=0.65):
        self.alpha = alpha
        self.positions = {}

    def update(self, key, new_position):

        if key not in self.positions:
            self.positions[key] = np.array(
                new_position, dtype=float
            )

        else:
            old = self.positions[key]

            self.positions[key] = (
                self.alpha * old +
                (1 - self.alpha) * np.array(new_position)
            )

        return tuple(
            self.positions[key].astype(int)
        )

    def reset(self):
        self.positions.clear()


# ==========================================
# RAINBOW COLOUR GENERATOR
# ==========================================

def rainbow_colour(position, total):

    hue = (position / max(total, 1)) % 1.0

    red, green, blue = colorsys.hsv_to_rgb(
        hue, 1.0, 1.0
    )

    return (
        int(blue * 255),
        int(green * 255),
        int(red * 255)
    )


# ==========================================
# CONTINUOUS CURVE GENERATOR
# ==========================================

def create_smooth_curve(points, steps=12):

    if len(points) < 3:
        return points

    points = np.array(points, dtype=float)

    result = []

    count = len(points)

    for i in range(count):

        p0 = points[(i - 1) % count]
        p1 = points[i]
        p2 = points[(i + 1) % count]
        p3 = points[(i + 2) % count]

        for t in np.linspace(0, 1, steps, endpoint=False):

            t2 = t * t
            t3 = t2 * t

            point = 0.5 * (
                (2 * p1) +
                (-p0 + p2) * t +
                (2*p0 - 5*p1 + 4*p2 - p3) * t2 +
                (-p0 + 3*p1 - 3*p2 + p3) * t3
            )

            result.append(
                tuple(point.astype(int))
            )

    return result


# ==========================================
# RUBBER BAND RENDERING
# ==========================================


def draw_rubber_band(frame, active_points):

    if len(active_points) < 3:
        return frame

    height, width = frame.shape[:2]

    # ======================================
    # 1. GENERATE CLOSED RUBBER BAND SHAPE
    # ======================================

    curve = create_smooth_curve(active_points)

    polygon = np.array(
        curve, dtype=np.int32
    )

    # ======================================
    # 2. CREATE POLYGON MASK
    # ======================================

    mask = np.zeros(
        (height, width), dtype=np.uint8
    )

    cv2.fillPoly(
        mask,
        [polygon],
        255
    )

    # ======================================
    # 3. CREATE TWO-SIDED HSV GRADIENT
    # ======================================

    y, x = np.mgrid[0:height, 0:width]

    center_y = np.mean(polygon[:, 1])

    # Back surface: purple and blue
    back_hue = (
        130 + (x / max(width, 1)) * 25
    ) % 180

    # Front surface: pink, red and orange
    front_hue = (
        165 + (x / max(width, 1)) * 35
    ) % 180

    # Blend both surfaces smoothly
    transition = np.clip(
        (y - center_y + 40) / 80,
        0, 1
    )

    hue = (
        back_hue * (1 - transition) +
        front_hue * transition
    )

    saturation = np.full(
        (height, width), 220, dtype=np.float32
    )

    brightness = (
        220 - 25 * np.sin(
            x / max(width, 1) * np.pi
        )
    )

    hsv = np.dstack([
        hue,
        saturation,
        brightness
    ]).astype(np.uint8)

    gradient = cv2.cvtColor(
        hsv, cv2.COLOR_HSV2BGR
    )

    # ======================================
    # 4. CLIP GRADIENT INSIDE POLYGON
    # ======================================

    surface = cv2.bitwise_and(
        gradient,
        gradient,
        mask=mask
    )

    # ======================================
    # 5. TRANSPARENT SURFACE
    # ======================================

    frame = cv2.addWeighted(
        frame, 0.68,
        surface, 0.32,
        0
    )

    # ======================================
    # 6. GLOWING SURFACE EDGES
    # ======================================

    glow_mask = cv2.GaussianBlur(
        mask,
        (0, 0),
        15
    )

    glow = cv2.cvtColor(
        glow_mask,
        cv2.COLOR_GRAY2BGR
    )

    glow_colour = np.zeros_like(frame)

    glow_colour[:, :, 0] = 255
    glow_colour[:, :, 1] = 80
    glow_colour[:, :, 2] = 220

    glow = cv2.bitwise_and(
        glow_colour,
        glow,
    )

    frame = cv2.addWeighted(
        frame, 1.0,
        glow, 0.18,
        0
    )

    # ======================================
    # 7. RAINBOW OUTER BOUNDARY
    # ======================================

    overlay = frame.copy()

    for i in range(len(curve)):

        start = curve[i]

        end = curve[
            (i + 1) % len(curve)
        ]

        colour = rainbow_colour(
            i, len(curve)
        )

        cv2.line(
            overlay,
            start,
            end,
            colour,
            8,
            cv2.LINE_AA
        )

    # Soft boundary glow
    blurred = cv2.GaussianBlur(
        overlay,
        (0, 0),
        8
    )

    frame = cv2.addWeighted(
        frame, 0.7,
        blurred, 0.3,
        0
    )

    # Sharp boundary
    for i in range(len(curve)):

        start = curve[i]

        end = curve[
            (i + 1) % len(curve)
        ]

        colour = rainbow_colour(
            i, len(curve)
        )

        cv2.line(
            frame,
            start,
            end,
            colour,
            3,
            cv2.LINE_AA
        )

    return frame



# ==========================================
# MAIN APPLICATION
# ==========================================

def main():

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    camera = cv2.VideoCapture(CAMERA_INDEX)

    smoother = PositionSmoother(SMOOTHING)

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=MAX_HANDS,
        model_complexity=1,
        min_detection_confidence=DETECTION_CONFIDENCE,
        min_tracking_confidence=TRACKING_CONFIDENCE
    ) as hands:

        while camera.isOpened():

            success, frame = camera.read()

            if not success:
                break

            frame = cv2.flip(frame, 1)

            height, width, _ = frame.shape

            rgb = cv2.cvtColor(
                frame, cv2.COLOR_BGR2RGB
            )

            results = hands.process(rgb)

            hand_data = {}

            active_points = []

            if results.multi_hand_landmarks:

                for hand_landmarks, handedness in zip(
                    results.multi_hand_landmarks,
                    results.multi_handedness
                ):

                    hand_label = (
                        handedness.classification[0].label
                    )

                    # Drawing hand skeleton
                    mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )

                    states, points = detect_finger_states(
                        hand_landmarks.landmark,
                        width,
                        height
                    )

                    hand_data[hand_label] = {
                        "states": states,
                        "points": points
                    }

            # Construct one continuous rubber band
            
            # ======================================
            # ADAPTIVE RUBBER BAND CONNECTION
            # ======================================

            # Process whichever hands are currently detected

            if hand_data:

                # Preserve the natural ordering of the loop
                active_order = []

                for hand_name, finger_name in FINGER_ORDER:

                    # Skip a hand if it is not detected
                    if hand_name not in hand_data:
                        continue

                    hand = hand_data[hand_name]

                    # Skip folded fingers
                    if not hand["states"][finger_name]:
                        continue

                    landmark_id = FINGER_IDS[finger_name][-1]

                    position = hand["points"][landmark_id]

                    key = f"{hand_name}_{finger_name}"

                    smooth_position = smoother.update(
                        key, position
                    )

                    active_order.append(smooth_position)

                # Draw the continuous rubber band
                if len(active_order) >= 3:

                    frame = draw_rubber_band(
                        frame, active_order
                    )

            else:
                # No hands detected
                smoother.reset()


            # Application information
            cv2.putText(
                frame,
                "HANDSYNC AI",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Press Q to quit",
                (20, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "HandSync AI - Rainbow Rubber Band",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
