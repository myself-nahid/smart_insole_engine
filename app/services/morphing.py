import trimesh
import numpy as np
import os
from app.config import TEMPLATE_DIR

class MorphingEngine:
    def generate_3d_model(self, target_size, weight, foot_data):
        # --- CONFIGURATION ---
        MASTER_SIZE = 44
        MASTER_FILENAME = f"base_{MASTER_SIZE}.obj"
        
        # 1. Load Template
        stl_path = os.path.join(TEMPLATE_DIR, MASTER_FILENAME)
        
        mesh = None
        if os.path.exists(stl_path):
            print(f"Loading template: {stl_path}")
            mesh = trimesh.load(stl_path)
        else:
            # FALLBACK: Create a box, BUT DON'T RETURN YET.
            # We want to scale this box so you can see the logic works.
            print(f"WARNING: Template {MASTER_FILENAME} not found. Using Fallback Box.")
            mesh = trimesh.creation.box(extents=(100, 270, 5))

        # 2. Calculate Size Scaling (X/Y Axis)
        # Ratio: Target 22 / Master 44 = 0.5
        size_ratio = int(target_size) / MASTER_SIZE
        
        # 3. Calculate Thickness Modifiers (Z Axis)
        # Weight Logic: 75kg is standard (1.0). 150kg is double thickness (2.0).
        weight_mod = float(weight) / 75.0
        # Clamp limits (0.5x to 1.5x) to prevent errors
        weight_mod = max(0.5, min(weight_mod, 1.5)) 

        # Arch Logic
        arch_mod = 1.0
        if foot_data.get('arch_type') == 'High':
            arch_mod = 1.25
        elif foot_data.get('arch_type') == 'Flat':
            arch_mod = 0.8

        scale_x = size_ratio
        scale_y = size_ratio
        scale_z = size_ratio * weight_mod * arch_mod

        # 4. Apply Transformation
        matrix = trimesh.transformations.compose_matrix(
            scale=[scale_x, scale_y, scale_z]
        )
        
        mesh.apply_transform(matrix)
        
        return mesh

    def export_mesh(self, mesh, output_path):
        mesh.export(output_path)
        return output_path