import numpy as np

class OceanManifold6D:
    def __init__(self, T_ref=283.15, S_ref=35.0, alpha_ref=1.0):
        """
        Initializes the 6D Continuous Torsion Mesh for Oceanography.
        T_ref: Baseline Deep Ocean Temp (Kelvin) - ~10C
        S_ref: Baseline Salinity (PSU - Practical Salinity Unit) - ~35 PSU
        """
        self.T_ref = T_ref
        self.S_ref = S_ref
        self.alpha_ref = alpha_ref

    def calculate_metric_condensation(self, T_matrix, S_matrix):
        """
        Eq 1: Calculates the 3D volume condensation (alpha) based on 
        the thermodynamic expansion of seawater.
        """
        # alpha = alpha_ref * (T/T_ref) * (S_ref/S)
        # We add 1e-5 to Salinity to prevent division by zero in land-masked areas
        alpha = self.alpha_ref * (T_matrix / self.T_ref) * (self.S_ref / (S_matrix + 1e-5))
        return alpha

    def calculate_metric_shear(self, alpha_matrix):
        """
        Eq 2: Calculates the Metric Shear (Gradient of alpha).
        Represents the geometric stress of the thermocline.
        """
        grad_y, grad_x = np.gradient(alpha_matrix)
        metric_shear = np.sqrt(grad_x**2 + grad_y**2)
        return metric_shear

    def find_manifold_flips(self, metric_shear, threshold=0.015):
        """
        Eq 3: Flags zones where the thermocline stress forces a topological flip.
        """
        flip_zones = np.where(metric_shear > threshold, 1.0, 0.0)
        return flip_zones