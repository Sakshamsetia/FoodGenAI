import numpy as np
import cv2
import torch
from transformers import DPTForDepthEstimation, DPTImageProcessor
import pandas as pd
import clip
from PIL import Image
from scipy.spatial import ConvexHull

def estimate_volume(depth_map, mask, pixel_size_mm=1.0, focal_length_px=500.0):
    """
    Estimates the volume of a food item using depth data without Open3D.
    
    Args:
        depth_map (np.array): Depth image (in mm).
        mask (np.array): Binary mask of the food region (1=food, 0=background).
        pixel_size_mm (float): Physical size of a pixel in mm.
        focal_length_px (float): Camera focal length in pixels.
    
    Returns:
        float: Estimated volume in mm³.
    """
    # Step 1: Extract 3D points from the masked region
    height, width = depth_map.shape
    u, v = np.meshgrid(np.arange(width), np.arange(height))
    u = u[mask == 1].flatten()
    v = v[mask == 1].flatten()
    z = depth_map[mask == 1].flatten()  # Depth in mm
    
    # Convert depth pixels to 3D coordinates (in mm)
    x = (u - width // 2) * (z / focal_length_px) * pixel_size_mm
    y = (v - height // 2) * (z / focal_length_px) * pixel_size_mm
    
    points = np.column_stack((x, y, z))
    
    # Step 2: Remove outliers using z-score filtering
    mean = np.mean(points, axis=0)
    std = np.std(points, axis=0)
    valid_points = points[np.all(np.abs((points - mean) / std) < 3, axis=1)]
    
    if len(valid_points) < 4:  # Need at least 4 points for convex hull
        return 0.0
    
    # Step 3: Compute convex hull and volume
    try:
        hull = ConvexHull(valid_points)
        volume = hull.volume  # Volume in mm³
    except:
        # Fallback: approximate volume as sum of voxels
        voxel_volume = (pixel_size_mm ** 2) * np.mean(z)
        volume = np.sum(mask) * voxel_volume
    
    return volume

def classify_image(image_path, class_names, device):
    """
    Classify an image using CLIP's zero-shot capabilities
    
    Args:
        image_path: Path to input image
        class_names: List of possible class names
        device: Device to run the model on
    
    Returns:
        dict: Class probabilities
    """
    # Prepare inputs
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    text_inputs = torch.cat([clip.tokenize(f"a photo of a {c}") for c in class_names]).to(device)
    
    # Calculate features
    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text_inputs)
        
        # Compute similarity
        logits_per_image = (image_features @ text_features.T).softmax(dim=-1)
        probs = logits_per_image.cpu().numpy()[0]
    
    return {class_names[i]: float(probs[i]) for i in range(len(class_names))}

def estimate_calories():
    # Initialize device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Load food categories
    data = pd.read_csv("food.csv")["Category"].unique()
    
    # Load CLIP model
    global model, preprocess
    model, preprocess = clip.load("ViT-B/32", device=device)
    
    # Classify the image
    results = classify_image("./images/img.jpg", data, device)
    class_name = sorted(results.items(), key=lambda x: -x[1])[0][0]
    print(f"Classified food: {class_name}")
    
    # Load and process depth map
    processor = DPTImageProcessor.from_pretrained("Intel/dpt-large")
    depth_model = DPTForDepthEstimation.from_pretrained("Intel/dpt-large").to(device)
    
    image = cv2.imread("./images/img.jpg")
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Predict depth
    inputs = processor(images=image_rgb, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = depth_model(**inputs)
        predicted_depth = outputs.predicted_depth
    
    # Interpolate depth map
    depth_map = torch.nn.functional.interpolate(
        predicted_depth.unsqueeze(1),
        size=image.shape[:2],
        mode="bicubic",
        align_corners=False,
    ).squeeze().cpu().numpy()
    
    # Scale depth map to reasonable mm range (0-1000mm)
    depth_map = (depth_map - depth_map.min()) * 1000
    
    # Create food mask with morphological cleaning
    _, mask = cv2.threshold(depth_map.astype(np.uint8), 0, 255, 
                          cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask = (mask > 0).astype(np.uint8)
    
    # Clean up mask with morphological operations
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Estimate volume
    volume_mm3 = estimate_volume(depth_map, mask)
    volume_ml = volume_mm3 / 1000000  # Convert to milliliters (1 ml = 1000 mm³)
    
    print(f"Estimated Volume: {volume_ml:.2f} ml")
    return class_name, volume_ml/1000000
