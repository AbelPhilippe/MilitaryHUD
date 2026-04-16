import cv2
import time
import numpy as np

# ===================================
# GLOBAL VARIABLES
# ===================================
ix, iy = -1, -1
bbox = None
tracker = None
tracking = False
frame = None
klase = "default"

box_size = 90
vision_mode = "NORMAL"  # "IR" ou "NORMAL"


# =======================================
#           MOUSE CALLBACK
# =======================================
def mouse_callback(event, x, y, flags, param):
    global ix, iy, bbox, tracker, tracking, frame

    ix, iy = x, y

    if event == cv2.EVENT_LBUTTONDOWN:
        x1 = max(0, x - box_size // 2)
        y1 = max(0, y - box_size // 2)

        bbox = (x1, y1, box_size, box_size)

        tracker = create_tracker()
        tracker.init(frame, bbox)

        tracking = True


# =========================
#      CREATE TRACKER
# =========================
def create_tracker():
    try:
        return cv2.legacy.TrackerCSRT_create()
    except:
        return cv2.TrackerCSRT_create()


# =========================
#     TEXT WITH BORDER
# =========================
def draw_text_with_outline(frame, text, pos, font, scale, color, thickness):
    x, y = pos

    cv2.putText(frame, text, (x, y),
                font, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)

    cv2.putText(frame, text, (x, y),
                font, scale, color, thickness, cv2.LINE_AA)


# =========================
#   SEEKER EFFECT (IR)
# =========================
def apply_ir_effect(crop):
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    noise = np.random.normal(0, 15, gray.shape).astype(np.uint8)
    noisy = cv2.add(gray, noise)

    ir = cv2.applyColorMap(noisy, cv2.COLORMAP_JET)

    return ir


# =========================
#   APPLY VISION MODE
# =========================
def process_seeker_view(crop):
    global vision_mode

    if vision_mode == "IR":
        return apply_ir_effect(crop)
    else:
        return crop


# =========================
#        DRAW HUD
# =========================
def draw_hud(frame, bbox, success, clean_frame):
    h, w = frame.shape[:2]
    color = (0, 255, 0)

    cx, cy = w // 2, h // 2

    # CROSSHAIR CENTRAL
    cv2.line(frame, (cx-80, cy), (cx+80, cy), color, 1)
    cv2.line(frame, (cx, cy-80), (cx, cy+80), color, 1)

    # CENTRAL BOX
    size = 25
    cv2.rectangle(frame, (cx-size, cy-size), (cx+size, cy+size), color, 1)

    if tracking and success:
        x, y, bw, bh = [int(v) for v in bbox]

        tx = x + bw // 2
        ty = y + bh // 2

        # DOTTED BOX
        for i in range(x, x+bw, 10):
            cv2.line(frame, (i, y), (i+5, y), color, 1)
            cv2.line(frame, (i, y+bh), (i+5, y+bh), color, 1)

        for i in range(y, y+bh, 10):
            cv2.line(frame, (x, i), (x, i+5), color, 1)
            cv2.line(frame, (x+bw, i), (x+bw, i+5), color, 1)

        # TARGET CROSSHAIR
        cv2.line(frame, (tx-20, ty), (tx+20, ty), color, 1)
        cv2.line(frame, (tx, ty-20), (tx, ty+20), color, 1)

        # TARGET DATA
        draw_text_with_outline(frame, f"Target XY: {tx}, {ty}",
                               (w-260, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # SEEKER VIEW (CLEAN FRAME)
        crop = clean_frame[y:y+bh, x:x+bw]

        if crop.size != 0:
            processed = process_seeker_view(crop)
            zoom = cv2.resize(processed, (200, 150))

            frame[100:250, w-220:w-20] = zoom

            cv2.rectangle(frame, (w-220, 100), (w-20, 250), color, 1)

            draw_text_with_outline(frame, "SEEKER VIEW",
                                   (w-170, 90),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    else:
        draw_text_with_outline(frame, "Target XY: - -",
                               (w-260, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)


# =========================
#      DRAW TEXT HUD
# =========================
def draw_text(frame):
    h, w = frame.shape[:2]
    color = (0, 255, 0)

    blink_on = int(time.time() * 2) % 2 == 0

    draw_text_with_outline(frame, "| DESIGNER AND DEVELOPER |",
                           (w//2-120, 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    draw_text_with_outline(frame, ">>>>>>> Abel Philippe, 2026 <<<<<<<",
                           (w//2-171, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    draw_text_with_outline(frame, "TARGET SELECTOR", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    draw_text_with_outline(frame, f"Klase: {klase}", (10, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    draw_text_with_outline(frame, "TARGET INPUT", (10, 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    if ix != -1:
        draw_text_with_outline(frame, f"X, Y: {ix}, {iy}",
                               (10, 130),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    else:
        draw_text_with_outline(frame, "X, Y: - -",
                               (10, 130),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    draw_text_with_outline(frame, "TEST SETTINGS", (w-260, 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # 🔥 NOVO: mostrar modo de visão
    draw_text_with_outline(frame, f"VISION MODE: {vision_mode}",
                           (w-260, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    if tracking and blink_on:
        draw_text_with_outline(frame, "SENSOR MODE: TRACKING",
                               (w//2-120, h-40),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


# =========================
# MAIN
# =========================
def main():
    global frame, tracker, bbox, tracking, vision_mode

    cap = cv2.VideoCapture("video.mp4")

    cv2.namedWindow("MILITARY HUD")
    cv2.setMouseCallback("MILITARY HUD", mouse_callback)

    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000 / fps) if fps > 0 else 30

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        clean_frame = frame.copy()

        success = False

        if tracking and tracker is not None:
            success, bbox = tracker.update(frame)

        draw_hud(frame, bbox, success, clean_frame)
        draw_text(frame)

        cv2.imshow("MILITARY HUD", frame)

        key = cv2.waitKey(delay) & 0xFF

        if key == 27:
            break

        elif key == ord('c'):
            tracking = False
            tracker = None
            bbox = None

        # TOGGLE VISION
        elif key == ord('v'):
            if vision_mode == "NORMAL":
                vision_mode = "IR"
            else:
                vision_mode = "NORMAL"

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()