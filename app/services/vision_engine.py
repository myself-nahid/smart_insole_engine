import cv2
import numpy as np
from PIL import Image

class VisionEngine:
    def process_image(self, image_bytes):
        # Convert bytes to OpenCV format
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 1. Segmentation (Thresholding)
        # Convert to HSV to isolate heatmap colors from white background
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Mask: Keep everything that isn't white/grey background
        mask = cv2.inRange(hsv, (0, 50, 50), (180, 255, 255))
        
        # 2. Auto-Split (Left/Right)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Sort by area, keep top 2 (Left and Right foot)
        feet_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
        
        if len(feet_contours) < 1:
            raise ValueError("No footprints detected")

        # Sort left/right based on X coordinate
        feet_contours.sort(key=lambda c: cv2.boundingRect(c)[0])
        
        left_foot_stats = self.analyze_foot(feet_contours[0], "Left")
        right_foot_stats = self.analyze_foot(feet_contours[1], "Right") if len(feet_contours) > 1 else None

        return {"left": left_foot_stats, "right": right_foot_stats}

    def analyze_foot(self, contour, side):
        # Get Bounding Box
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)

        # 3. CSI Calculation (simplified logic)
        # In production, we would rotate the contour via PCA to be perfectly vertical first.
        # Here we approximate by slicing width at specific heights.
        
        # Simulate scanning the width at 50% height (Isthmus) and 80% height (Forefoot)
        # NOTE: Real implementation requires pixel traversal mask.
        
        # Logic Placeholder:
        # Assuming average foot for demo. 
        # Real code uses cv2.countNonZero inside a row slice.
        estimated_csi = 35.0 # Normal arch placeholder
        
        arch_type = "Normal"
        if estimated_csi > 45: arch_type = "Flat"
        elif estimated_csi < 30: arch_type = "High"

        return {
            "side": side,
            "width_px": w,
            "height_px": h,
            "csi": estimated_csi,
            "arch_type": arch_type,
            "contour": contour.tolist() # Serializable for frontend
        }