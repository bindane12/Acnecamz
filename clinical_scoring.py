import math
import json
import os

# Load scientific clinical evidence database
EVIDENCE_PATH = os.path.join(os.path.dirname(__file__), "clinical_evidence.json")
try:
    with open(EVIDENCE_PATH, "r") as f:
        CLINICAL_EVIDENCE = json.load(f)
except Exception as e:
    print(f"Error loading clinical_evidence.json: {e}")
    CLINICAL_EVIDENCE = {}

# Class Mapping Taxonomy
CLASS_MAP = {
    0: {"id": "comedone", "name": "Comedone (Blackhead/Whitehead)", "color": "#00FF00", "type": "non-inflammatory"},
    1: {"id": "papule", "name": "Papule (Red Inflamed Bump)", "color": "#FF3333", "type": "inflammatory"},
    2: {"id": "pustule", "name": "Pustule (Pus-Filled Lesion)", "color": "#FFFF00", "type": "inflammatory"},
    3: {"id": "nodule_cyst", "name": "Nodule / Cyst (Deep Inflamed)", "color": "#AA00FF", "type": "severe-inflammatory"},
    4: {"id": "hyperpigmentation", "name": "Hyperpigmentation (Dark Mark)", "color": "#00E5FF", "type": "post-inflammatory"}
}

# Standardized Facial Zones (Normalized Bounding Box Coordinates)
ZONES = {
    "forehead": {"name": "Forehead", "y_range": (0.15, 0.40), "x_range": (0.20, 0.80)},
    "nose": {"name": "Nose / T-Zone", "y_range": (0.35, 0.65), "x_range": (0.40, 0.60)},
    "left_cheek": {"name": "Left Cheek", "y_range": (0.45, 0.75), "x_range": (0.15, 0.45)},
    "right_cheek": {"name": "Right Cheek", "y_range": (0.45, 0.75), "x_range": (0.55, 0.85)},
    "chin": {"name": "Chin & Jawline", "y_range": (0.70, 0.90), "x_range": (0.30, 0.70)}
}

def analyze_clinical_correlations(zone_data, total_counts, unique_categories, seen_actives):
    """
    Computes evidence correlations based on spatial zone distributions, 
    lesion co-occurrences, and active ingredient interactions.
    """
    pattern_correlations = []
    co_occurrence_risks = []
    matched_synergies = []
    matched_conflicts = []

    total_inf = total_counts.get("papule", 0) + total_counts.get("pustule", 0) + total_counts.get("nodule_cyst", 0)
    total_comedone = total_counts.get("comedone", 0)

    # 1. Spatial Zone Pattern Correlations
    zone_patterns = CLINICAL_EVIDENCE.get("zone_pattern_correlations", {})
    
    # Chin/Jawline Hormonal Pattern
    chin_inf = zone_data.get("chin", {}).get("papule", 0) + zone_data.get("chin", {}).get("pustule", 0) + zone_data.get("chin", {}).get("nodule_cyst", 0)
    if total_inf >= 2 and (chin_inf / total_inf) >= 0.35:
        p_info = zone_patterns.get("chin_jawline_inflammatory", {})
        if p_info:
            pattern_correlations.append({
                "pattern_id": "chin_jawline_inflammatory",
                "name": p_info.get("name"),
                "description": p_info.get("description"),
                "recommendation": p_info.get("clinical_recommendation"),
                "pmid": p_info.get("pmid"),
                "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{p_info.get('pmid')}/" if p_info.get("pmid") else None
            })

    # T-Zone Seborrheic Pattern
    tzone_com = zone_data.get("forehead", {}).get("comedone", 0) + zone_data.get("nose", {}).get("comedone", 0)
    if total_comedone >= 3 and (tzone_com / total_comedone) >= 0.50:
        p_info = zone_patterns.get("tzone_comedones", {})
        if p_info:
            pattern_correlations.append({
                "pattern_id": "tzone_comedones",
                "name": p_info.get("name"),
                "description": p_info.get("description"),
                "recommendation": p_info.get("clinical_recommendation"),
                "pmid": p_info.get("pmid"),
                "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{p_info.get('pmid')}/" if p_info.get("pmid") else None
            })

    # Cheek Friction / Barrier Pattern
    cheek_inf = (zone_data.get("left_cheek", {}).get("papule", 0) + zone_data.get("right_cheek", {}).get("papule", 0) +
                 zone_data.get("left_cheek", {}).get("pustule", 0) + zone_data.get("right_cheek", {}).get("pustule", 0))
    if total_inf >= 3 and (cheek_inf / total_inf) >= 0.45:
        p_info = zone_patterns.get("cheek_friction_barrier", {})
        if p_info:
            pattern_correlations.append({
                "pattern_id": "cheek_friction_barrier",
                "name": p_info.get("name"),
                "description": p_info.get("description"),
                "recommendation": p_info.get("clinical_recommendation"),
                "pmid": p_info.get("pmid"),
                "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{p_info.get('pmid')}/" if p_info.get("pmid") else None
            })

    # 2. Lesion Co-occurrence Risk Analysis
    if total_inf >= 2 and total_counts.get("hyperpigmentation", 0) >= 1:
        co_occurrence_risks.append({
            "risk_title": "Post-Inflammatory Hyperpigmentation (PIH) Escalation Risk",
            "severity": "Moderate-High",
            "rationale": "Active inflammatory lesions co-occurring with existing dark marks indicate melanocyte hyper-reactivity to inflammatory cytokines.",
            "protocol": "Combine anti-inflammatory active (Niacinamide / BPO) with early tyrosinase inhibition (Azelaic Acid 10-20%) to mitigate future scarring."
        })

    if total_counts.get("nodule_cyst", 0) >= 1 and total_inf >= 3:
        co_occurrence_risks.append({
            "risk_title": "Deep Tissue Scarring & Structural Damage Risk",
            "severity": "High",
            "rationale": "Deep nodular lesions extend into dermal layers causing follicular rupture and enzymatic degradation of dermal collagen matrix.",
            "protocol": "Early dermatological consultation for systemic evaluation (oral isotretinoin/anti-androgens) to prevent permanent atrophic scarring."
        })

    if total_comedone >= 3 and total_inf >= 2:
        co_occurrence_risks.append({
            "risk_title": "Microcomedone Inflammatory Propagation Cascade",
            "severity": "Moderate",
            "rationale": "Co-existence of non-inflammatory comedones and inflammatory papules suggests active anaerobic C. acnes follicular proliferation.",
            "protocol": "Pair lipophilic pore clearing (Salicylic Acid / Adapalene) with antibacterial oxidative therapy (BPO)."
        })

    # 3. Active Ingredient Synergies & Conflicts Matrix
    rules = CLINICAL_EVIDENCE.get("synergies_and_conflicts", {})
    actives_text = " ".join(seen_actives).lower()

    for syn in rules.get("synergies", []):
        pair = syn.get("pair", [])
        # Check if both keywords present in seen_actives
        if any(pair[0].split()[0].lower() in actives_text for _ in [1]) and any(pair[1].split()[0].lower() in actives_text for _ in [1]):
            matched_synergies.append(syn)

    for con in rules.get("conflicts", []):
        pair = con.get("pair", [])
        if any(pair[0].split()[0].lower() in actives_text for _ in [1]) and any(pair[1].split()[0].lower() in actives_text for _ in [1]):
            matched_conflicts.append(con)

    return {
        "pattern_insights": pattern_correlations,
        "co_occurrence_risks": co_occurrence_risks,
        "matched_synergies": matched_synergies,
        "matched_conflicts": matched_conflicts
    }

# Dynamic Facial Zone Mapping relative to Face Bounding Box
FACE_ZONES = {
    "forehead": {"name": "Forehead", "y_range": (-0.05, 0.35), "x_range": (0.15, 0.85)},
    "nose": {"name": "Nose / T-Zone", "y_range": (0.32, 0.65), "x_range": (0.35, 0.65)},
    "left_cheek": {"name": "Left Cheek", "y_range": (0.40, 0.75), "x_range": (0.00, 0.40)},
    "right_cheek": {"name": "Right Cheek", "y_range": (0.40, 0.75), "x_range": (0.60, 1.00)},
    "chin": {"name": "Chin & Jawline", "y_range": (0.70, 1.05), "x_range": (0.20, 0.80)}
}

import cv2
import numpy as np

def detect_face_bbox(img):
    """Detects face bounding box (fx, fy, fw, fh) using skin color / contour heuristics."""
    if img is None or img.size == 0:
        return None
    
    h, w = img.shape[:2]
    # Simple color-space skin detection heuristic for dynamic framing fallback
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([25, 255, 255], dtype=np.uint8)
    skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
    
    contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) > (w * h * 0.05):
            fx, fy, fw, fh = cv2.boundingRect(largest)
            return (fx, fy, fw, fh)
            
    # Default fallback: center region of image
    return (int(w * 0.125), int(h * 0.1), int(w * 0.75), int(h * 0.85))

def classify_lesion_crop(crop_img, radius):
    """Classifies an individual lesion crop into 5 clinical classes using color & size analysis."""
    if crop_img is None or crop_img.size == 0:
        return 0  # default comedone
        
    b, g, r = cv2.split(crop_img)
    # Redness Index
    mean_redness = float(np.mean(r.astype(float) - 0.5 * (g.astype(float) + b.astype(float))))
    
    # HSV color analysis
    hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
    val = hsv[:, :, 2]
    sat = hsv[:, :, 1]
    hue = hsv[:, :, 0]
    
    mean_val = float(np.mean(val))
    
    # Check for pus (bright center or yellowish center)
    pus_mask = ((val > 170) & (sat < 90)) | ((hue >= 10) & (hue <= 35) & (val > 150))
    pus_fraction = float(np.sum(pus_mask) / pus_mask.size)
    
    if pus_fraction >= 0.12 and mean_redness > 12:
        return 2  # Pustule
    elif mean_redness > 24:
        if radius >= 14:
            return 3  # Nodule/Cyst
        else:
            return 1  # Papule
    elif mean_redness < 12 and mean_val < 115:
        return 4  # Hyperpigmentation
    else:
        return 0  # Comedone

def analyze_facial_scan(detections, img_width=1, img_height=1, image_matrix=None):
    """
    Analyzes list of detection dicts: [{'x': cx, 'y': cy, 'r': r, 'conf': conf, 'class_id': int}]
    Returns clinical diagnostic dictionary.
    """
    zone_data = {
        z_key: {
            "name": z_info["name"],
            "comedone": 0,
            "papule": 0,
            "pustule": 0,
            "nodule_cyst": 0,
            "hyperpigmentation": 0,
            "total": 0
        }
        for z_key, z_info in ZONES.items()
    }
    
    total_counts = {
        "comedone": 0,
        "papule": 0,
        "pustule": 0,
        "nodule_cyst": 0,
        "hyperpigmentation": 0
    }

    processed_detections = []

    # Safe image dimensions fallback
    w = img_width if img_width > 0 else 1
    h = img_height if img_height > 0 else 1

    # Detect face bounding box for dynamic relative zoning
    face_box = detect_face_bbox(image_matrix) if image_matrix is not None else None
    if face_box:
        fx, fy, fw, fh = face_box
    else:
        fx, fy, fw, fh = 0, 0, w, h

    for det in detections:
        cx, cy, r = det["x"], det["y"], det["r"]
        
        # 1. Dynamic Class Classification via Image Crop Feature Extraction
        if image_matrix is not None and image_matrix.size > 0:
            y1 = max(0, int(cy - r))
            y2 = min(image_matrix.shape[0], int(cy + r))
            x1 = max(0, int(cx - r))
            x2 = min(image_matrix.shape[1], int(cx + r))
            crop = image_matrix[y1:y2, x1:x2]
            class_id = classify_lesion_crop(crop, r)
        else:
            class_id = det.get("class_id", 0)
            
        if class_id not in CLASS_MAP:
            class_id = 0
            
        class_info = CLASS_MAP[class_id]
        class_key = class_info["id"]
        
        total_counts[class_key] = total_counts.get(class_key, 0) + 1
        
        # 2. Dynamic Relative Coordinate Calculation
        if fw > 0 and fh > 0:
            cx_norm = (cx - fx) / fw
            cy_norm = (cy - fy) / fh
            zone_schema = FACE_ZONES
        else:
            cx_norm = cx / w
            cy_norm = cy / h
            zone_schema = ZONES
        
        assigned_zone = "general_face"
        for z_key, z_info in zone_schema.items():
            if (z_info["x_range"][0] <= cx_norm <= z_info["x_range"][1] and 
                z_info["y_range"][0] <= cy_norm <= z_info["y_range"][1]):
                zone_data[z_key][class_key] += 1
                zone_data[z_key]["total"] += 1
                assigned_zone = z_key
                break

        det_copy = dict(det)
        det_copy["class_id"] = class_id
        det_copy["class_name"] = class_info["name"]
        det_copy["class_key"] = class_key
        det_copy["color"] = class_info["color"]
        det_copy["zone"] = assigned_zone
        processed_detections.append(det_copy)

    # 1. Calculate Hayashi Severity Score (Based on half-face inflammatory counts)
    inflammatory_count = total_counts["papule"] + total_counts["pustule"] + total_counts["nodule_cyst"]
    half_face_inf = math.ceil(inflammatory_count / 2)
    
    if half_face_inf <= 5:
        hayashi_grade = "Mild"
        severity_color = "#00FF00"
    elif half_face_inf <= 20:
        hayashi_grade = "Moderate"
        severity_color = "#FFFF00"
    elif half_face_inf <= 50:
        hayashi_grade = "Severe"
        severity_color = "#FF9900"
    else:
        hayashi_grade = "Very Severe"
        severity_color = "#FF0000"

    # 2. Plain-Language Skin Condition Description Generator
    summary_parts = []
    if total_counts["comedone"] > 0:
        summary_parts.append(f"{total_counts['comedone']} non-inflammatory comedone(s)")
    if total_counts["papule"] > 0:
        summary_parts.append(f"{total_counts['papule']} red papule(s)")
    if total_counts["pustule"] > 0:
        summary_parts.append(f"{total_counts['pustule']} pus-filled pustule(s)")
    if total_counts["nodule_cyst"] > 0:
        summary_parts.append(f"{total_counts['nodule_cyst']} deep cystic bump(s)")
    if total_counts["hyperpigmentation"] > 0:
        summary_parts.append(f"{total_counts['hyperpigmentation']} post-acne dark mark(s)")

    if not summary_parts:
        skin_description = "Your scan shows clear skin with no active acne lesions detected."
    else:
        # Find zone with highest concentration
        most_affected_key = max(zone_data.keys(), key=lambda k: zone_data[k]["total"])
        highest_zone_total = zone_data[most_affected_key]["total"]
        
        if highest_zone_total > 0:
            zone_desc = f" The highest lesion concentration is located on the {zone_data[most_affected_key]['name']}."
        else:
            zone_desc = ""

        skin_description = (
            f"Skin Diagnosis: {hayashi_grade} Acne. Scan identified " +
            ", ".join(summary_parts) + "." + zone_desc
        )

    # 3. Targeted Active Ingredients & Skincare Routine (Scientifically Backed)
    am_routine = ["Gentle Hydrating Cleanser", "Broad-Spectrum Sunscreen (SPF 30+)"]
    pm_routine = ["Gentle Cleanser", "Lightweight Non-Comedogenic Moisturizer"]
    
    scientific_evidence_list = []
    
    # Track which categories are detected
    categories_to_recommend = []
    if total_counts.get("comedone", 0) >= 1:
        categories_to_recommend.append("comedone")
    if total_counts.get("papule", 0) >= 1:
        categories_to_recommend.append("papule")
    if total_counts.get("pustule", 0) >= 1:
        categories_to_recommend.append("pustule")
    if total_counts.get("hyperpigmentation", 0) >= 1:
        categories_to_recommend.append("hyperpigmentation")
    if total_counts.get("nodule_cyst", 0) >= 1:
        categories_to_recommend.append("nodule_cyst")

    # Add secondary evidence categories based on correlations
    if total_counts.get("hyperpigmentation", 0) >= 1 or (inflammatory_count >= 2 and total_counts.get("hyperpigmentation", 0) >= 1):
        categories_to_recommend.append("post_inflammatory_erythema")
    if total_counts.get("comedone", 0) >= 3:
        categories_to_recommend.append("seborrhea_oily")
    if inflammatory_count >= 4:
        categories_to_recommend.append("barrier_compromise")

    unique_categories = list(set(categories_to_recommend))

    # Add routines based on clinical evidence database
    if "comedone" in unique_categories:
        pm_routine.insert(1, "BHA Salicylic Acid Liquid (2% - 2-3 nights per week)")
    if "papule" in unique_categories or "pustule" in unique_categories:
        am_routine.insert(1, "Niacinamide Serum (4-5%)")
        pm_routine.insert(1, "Benzoyl Peroxide Spot Treatment (2.5%)")
    if "hyperpigmentation" in unique_categories:
        am_routine.insert(1, "Azelaic Acid Serum (10-20%)")
    if "barrier_compromise" in unique_categories:
        pm_routine.append("Ceramide Barrier Repair Cream (1-2%)")

    # Fetch active ingredients and scientific references
    seen_actives = set()
    for cat in unique_categories:
        evidence_data = CLINICAL_EVIDENCE.get(cat, {})
        for active in evidence_data.get("actives", []):
            active_name = active["name"]
            if active_name not in seen_actives:
                seen_actives.add(active_name)
                evidence_info = active.get("evidence", {})
                pmid = evidence_info.get("pmid")
                scientific_evidence_list.append({
                    "active_name": active_name,
                    "concentration": active.get("concentration"),
                    "scientific_basis": active.get("scientific_basis"),
                    "citation": evidence_info.get("citation"),
                    "title": evidence_info.get("title"),
                    "journal": evidence_info.get("journal"),
                    "pmid": pmid,
                    "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None
                })

    # Run multi-evidence correlation engine
    clinical_correlations = analyze_clinical_correlations(zone_data, total_counts, unique_categories, seen_actives)

    return {
        "processed_detections": processed_detections,
        "total_lesions": len(detections),
        "hayashi_grade": hayashi_grade,
        "severity_color": severity_color,
        "total_counts": total_counts,
        "zone_breakdown": zone_data,
        "skin_description": skin_description,
        "targeted_actives": [
            f"{item['active_name']} ({item['concentration']}): {item['scientific_basis']}"
            for item in scientific_evidence_list
        ],
        "scientific_evidence": scientific_evidence_list,
        "clinical_correlations": clinical_correlations,
        "skincare_routine": {
            "AM": am_routine,
            "PM": pm_routine
        }
    }
