```python
from cellpose import models
import cv2
import numpy as np
from skimage import measure, exposure
from pathlib import Path


# =========================
# スコア計算
# =========================
def compute_cell_score_from_pixels(pixels):

    if len(pixels) == 0:
        return 0

    ref = np.array([190, 204, 203])  # #BECCCB

    dist = np.linalg.norm(pixels - ref, axis=1)
    color_score = np.mean(dist) / 255

    r = pixels[:, 0].astype(float)
    g = pixels[:, 1].astype(float)
    b = pixels[:, 2].astype(float)

    brightness = 0.299*r + 0.587*g + 0.114*b
    dark_score = 1 - np.mean(brightness) / 255

    return 0.6 * color_score + 0.4 * dark_score


# =========================
# スコア（全細胞）
# =========================
def compute_scores(img_rgb, masks):

    scores = []

    for r in measure.regionprops(masks):

        if r.area < 20:
            continue

        cell = (masks == r.label)
        pixels = img_rgb[cell]

        score = compute_cell_score_from_pixels(pixels)

        scores.append({
            "label": r.label,
            "score": score
        })

    return scores


# =========================
# 可視化
# =========================
def visualize_cells(img_rgb, masks, scores, threshold):

    vis = img_rgb.copy()
    score_dict = {s["label"]: s["score"] for s in scores}

    for r in measure.regionprops(masks):

        label = r.label
        cell_mask = (masks == label)

        score = score_dict.get(label, 0)

        if score >= threshold:
            color = np.array([255, 0, 0])   # 老化
        else:
            color = np.array([0, 255, 0])   # 正常

        vis[cell_mask] = vis[cell_mask] * 0.5 + color * 0.5

    return vis


# =========================
# メイン関数（Streamlit用）
# =========================
def analyze(img_path):

    img_path = Path(img_path)

    img_bgr = cv2.imread(str(img_path))
    if img_bgr is None:
        raise FileNotFoundError("画像読み込めません")

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # 前処理
    img_rgb = exposure.equalize_adapthist(img_rgb, clip_limit=0.03)
    img_rgb = (img_rgb * 255).astype(np.uint8)

    # Cellpose
    model = models.Cellpose(model_type='cyto2', gpu=False)

    masks, _, _, _ = model.eval(
        img_rgb,
        diameter=40,
        channels=[0, 0],
        flow_threshold=0.6,
        cellprob_threshold=0.0
    )

    total_cells = len(np.unique(masks)) - 1

    # スコア
    scores = compute_scores(img_rgb, masks)

    all_scores = np.array([s["score"] for s in scores])
    threshold = np.percentile(all_scores, 60)

    positive = sum(1 for s in scores if s["score"] >= threshold)

    # 可視化
    vis = visualize_cells(img_rgb, masks, scores, threshold)

    out_path = img_path.with_name("result_overlay.png")
    cv2.imwrite(str(out_path), cv2.cvtColor(vis, cv2.COLOR_RGB2BGR))

    return {
        "total": total_cells,
        "positive": positive,
        "ratio": positive / total_cells if total_cells > 0 else 0,
        "output_image": str(out_path)
    }
```
