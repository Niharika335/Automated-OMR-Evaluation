# template_generator.py
import cv2
import numpy as np
import json
import random
import os

OUT_DIR = "sample_data"
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1200, 1700
MARGIN = 60
TOP_MARGIN = 120
BOTTOM_MARGIN = 120
CORNER_SIZE = 100

def create_blank_template():
    img = 255 * np.ones((H, W, 3), dtype=np.uint8)
    # draw corner squares (fiducials)
    cv2.rectangle(img, (MARGIN, MARGIN), (MARGIN+CORNER_SIZE, MARGIN+CORNER_SIZE), (0,0,0), -1)
    cv2.rectangle(img, (W-MARGIN-CORNER_SIZE, MARGIN), (W-MARGIN, MARGIN+CORNER_SIZE), (0,0,0), -1)
    cv2.rectangle(img, (MARGIN, H-MARGIN-CORNER_SIZE), (MARGIN+CORNER_SIZE, H-MARGIN), (0,0,0), -1)
    cv2.rectangle(img, (W-MARGIN-CORNER_SIZE, H-MARGIN-CORNER_SIZE), (W-MARGIN, H-MARGIN), (0,0,0), -1)
    return img

def generate_bubble_layout():
    # 5 subject columns, each 20 questions -> 100 questions total
    coords = []  # list of questions; each q has 4 option centers [(x,y)...]
    block_w = (W - 2*MARGIN) / 5.0
    available_h = H - TOP_MARGIN - BOTTOM_MARGIN
    row_h = available_h / 20.0
    option_dx = 40
    for col in range(5):
        x_center = int(MARGIN + block_w*col + block_w/2)
        for row in range(20):
            y_center = int(TOP_MARGIN + row*row_h + row_h/2)
            # positions for A-D horizontally
            centers = []
            offsets = [-1.5, -0.5, 0.5, 1.5]
            for off in offsets:
                cx = int(x_center + off*option_dx)
                cy = int(y_center)
                centers.append([cx, cy])
            coords.append(centers)
    return coords

def draw_bubbles(img, coords, radius=18):
    for centers in coords:
        for (cx,cy) in centers:
            cv2.circle(img, (cx,cy), radius, (0,0,0), 2)  # circle outline
    return img

def random_answer_key(n=100):
    choices = ['A','B','C','D']
    return [random.choice(choices) for _ in range(n)]

def fill_answers(img, coords, key, radius=16):
    filled = img.copy()
    for q_idx, centers in enumerate(coords):
        choice = key[q_idx]
        idx = {'A':0,'B':1,'C':2,'D':3}[choice]
        cx,cy = centers[idx]
        cv2.circle(filled, (cx,cy), radius, (0,0,0), -1)
    return filled

def warp_image(img):
    # apply small random perspective perturbation to simulate camera capture
    pts1 = np.float32([[MARGIN, MARGIN], [W-MARGIN, MARGIN], [MARGIN, H-MARGIN], [W-MARGIN, H-MARGIN]])
    jitter = 30
    pts2 = pts1 + np.random.randint(-jitter, jitter, pts1.shape).astype(np.float32)
    M = cv2.getPerspectiveTransform(pts1, pts2)
    warped = cv2.warpPerspective(img, M, (W, H))
    return warped, pts1, pts2

def save_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)

def normalize_coords(coords):
    # save normalized coords between 0 and 1 (relative)
    norm = []
    for centers in coords:
        norm_centers = [[cx / W, cy / H] for (cx,cy) in centers]
        norm.append(norm_centers)
    return norm

def main():
    template = create_blank_template()
    coords = generate_bubble_layout()
    template = draw_bubbles(template, coords)
    key = random_answer_key(len(coords))
    filled = fill_answers(template, coords, key)
    warped, pts1, pts2 = warp_image(filled)

    cv2.imwrite(os.path.join(OUT_DIR, "template.png"), template)
    cv2.imwrite(os.path.join(OUT_DIR, "filled_template.png"), filled)
    cv2.imwrite(os.path.join(OUT_DIR, "sample_captured.png"), warped)

    # Save answer key and normalized coordinates
    save_json({"answers": key}, os.path.join(OUT_DIR, "answer_key.json"))
    save_json({"coords": normalize_coords(coords)}, os.path.join(OUT_DIR, "template_coords.json"))

    print("Sample data created in ./sample_data/ : template.png, filled_template.png, sample_captured.png")
    print("answer_key.json and template_coords.json saved.")

if __name__ == "__main__":
    main()
