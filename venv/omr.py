# omr.py
import cv2
import numpy as np
import json
import os

# Helper: load template coords (normalized) and answer key
def load_template_meta(coords_path="sample_data/template_coords.json", key_path="sample_data/answer_key.json"):
    with open(coords_path, "r") as f:
        coords = json.load(f)["coords"]
    with open(key_path, "r") as f:
        answers = json.load(f)["answers"]
    return coords, answers

# Find four big corner squares (fiducials)
def find_fiducials(img_gray):
    # threshold and find contours
    _, th = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    squares = []
    h, w = img_gray.shape
    for cnt in contours:
        x,y,ww,hh = cv2.boundingRect(cnt)
        area = ww*hh
        # accept squares reasonably big
        if area > (0.002 * w * h):
            squares.append((x,y,ww,hh))
    if len(squares) < 4:
        return None
    # take the 4 largest
    squares = sorted(squares, key=lambda r: r[2]*r[3], reverse=True)[:4]
    centers = []
    for (x,y,ww,hh) in squares:
        centers.append((x+ww/2, y+hh/2))
    # sort corners: top-left, top-right, bottom-right, bottom-left
    centers = sorted(centers, key=lambda p: (p[1], p[0]))  # sort by y then x
    top = sorted(centers[:2], key=lambda p: p[0])
    bottom = sorted(centers[2:], key=lambda p: p[0], reverse=True)  # reverse to get br, bl
    ordered = [top[0], top[1], bottom[0], bottom[1]]
    return np.array(ordered, dtype=np.float32)

def warp_to_template(img, src_pts, out_size=(1200,1700)):
    dst_pts = np.array([[60,60], [out_size[0]-60,60], [out_size[0]-60,out_size[1]-60], [60,out_size[1]-60]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(img, M, out_size)
    return warped

def detect_selections(warped_img, norm_coords, opt_radius=18, threshold=0.35):
    # warped_img: color image
    gray = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    h, w = gray.shape
    results = []
    mask_r = int(opt_radius*0.9)
    mask_area = np.pi * (mask_r**2)
    for centers in norm_coords:
        choices = []
        for (nx, ny) in centers:
            cx = int(nx * w)
            cy = int(ny * h)
            # crop ROI
            r = opt_radius+6
            x1,y1 = max(0, cx-r), max(0, cy-r)
            x2,y2 = min(w, cx+r), min(h, cy+r)
            roi = th[y1:y2, x1:x2]
            # create circular mask aligned to center
            hh, ww = roi.shape
            Y, X = np.ogrid[:hh, :ww]
            cy2, cx2 = hh//2, ww//2
            circle_mask = (X - cx2)**2 + (Y - cy2)**2 <= (mask_r**2)
            dark = np.sum(roi[circle_mask] > 0)  # since inverted, filled is white in 'th'
            fill_ratio = dark / (mask_area + 1e-9)
            choices.append(fill_ratio)
        # decide selection
        max_idx = int(np.argmax(choices))
        max_val = choices[max_idx]
        if max_val >= threshold:
            sel = ['A','B','C','D'][max_idx]
        else:
            sel = None
        results.append({
            "choices": choices,
            "selected": sel,
            "max_val": float(max_val)
        })
    return results

def score_results(detected, answer_key):
    n = len(answer_key)
    selected_list = []
    correct_mask = []
    for i in range(n):
        sel = detected[i]["selected"]
        selected_list.append(sel if sel is not None else "")
        correct = (sel == answer_key[i])
        correct_mask.append(correct)
    # per-subject scoring 5 subjects, 20 questions each
    per_subject = []
    for s in range(5):
        start = s*20
        end = start + 20
        score = sum([1 if correct_mask[i] else 0 for i in range(start, end)])
        per_subject.append(score)
    total = sum(per_subject)
    return {
        "selected": selected_list,
        "correct_mask": correct_mask,
        "per_subject": per_subject,
        "total": total
    }

def create_overlay(warped_img, norm_coords, detected, answer_key, out_path="overlay.png"):
    vis = warped_img.copy()
    h,w,_ = vis.shape
    for i, centers in enumerate(norm_coords):
        sel = detected[i]["selected"]
        correct = (sel == answer_key[i])
        for idx,(nx,ny) in enumerate(centers):
            cx = int(nx * w); cy = int(ny * h)
            color = (180,180,180)
            if sel is not None and idx == {'A':0,'B':1,'C':2,'D':3}[sel]:
                color = (0,200,0) if correct else (0,0,255)
            cv2.circle(vis, (cx,cy), 18, color, 3)
        # draw question number
        qx = int(centers[0][0]*w) - 50
        qy = int(centers[0][1]*h)
        cv2.putText(vis, str(i+1), (qx, qy+6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80,80,80), 1)
    cv2.imwrite(out_path, vis)
    return out_path

def process_image(input_path, coords_path="sample_data/template_coords.json", key_path="sample_data/answer_key.json"):
    coords, answers = load_template_meta(coords_path, key_path)
    img = cv2.imread(input_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fid = find_fiducials(gray)
    if fid is None:
        raise RuntimeError("Could not find 4 fiducial markers in the image. Make sure corner squares are visible.")
    warped = warp_to_template(img, fid)
    detected = detect_selections(warped, coords)
    score = score_results(detected, answers)
    overlay_path = os.path.splitext(input_path)[0] + "_overlay.png"
    create_overlay(warped, coords, detected, answers, overlay_path)
    return {
        "warped_image": warped,
        "detected": detected,
        "score": score,
        "overlay_path": overlay_path
    }
