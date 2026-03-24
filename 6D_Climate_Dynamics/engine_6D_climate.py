import numpy as np

class FluidManifold6D:
    def __init__(self, T_ref=288.15, P_ref=101325.0, alpha_ref=1.0):
        """
        Initializes the 6D Continuous Torsion Mesh.
        T_ref: Baseline Temp (Kelvin) - Standard is 15C
        P_ref: Baseline Pressure (Pascals) - Standard Sea Level
        """
        self.T_ref = T_ref
        self.P_ref = P_ref
        self.alpha_ref = alpha_ref

    def calculate_metric_condensation(self, T_matrix, P_matrix):
        """
        Eq 1: Calculates the observable 3D volume condensation (alpha)
        based on the thermodynamic Ideal Gas constraints.
        """
        # alpha = alpha_ref * (T/T_ref) * (P_ref/P)
        alpha = self.alpha_ref * (T_matrix / self.T_ref) * (self.P_ref / P_matrix)
        return alpha

    def calculate_metric_shear(self, alpha_matrix):
        """
        Eq 2: Calculates the Metric Shear (Gradient of alpha).
        This represents the baroclinic torque tearing the manifold.
        """
        # np.gradient returns the gradient in the y and x directions
        grad_y, grad_x = np.gradient(alpha_matrix)
        
        # Calculate the magnitude of the shear vector
        metric_shear = np.sqrt(grad_x**2 + grad_y**2)
        return metric_shear

    def find_manifold_flips(self, metric_shear, threshold=0.015):
        """
        Eq 3: Flags the zones where Metric Shear exceeds the hyperbolic
        stability limit. These are the locations of cyclogenesis (storms).
        """
        # Create a binary mask: 1 where a storm flips the manifold, 0 for laminar flow
        flip_zones = np.where(metric_shear > threshold, 1, 0)
        return flip_zones