import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

class FineStructure8D_Solver:
    def __init__(self):
        self.Gamma_16D = 3.0 / 16.0 
        # Spin torsion constant (scaled for clear visualization of the split)
        self.k_spin = 1.5e-3 

    def effective_potential(self, r, spin_alignment):
        """
        Calculates the 8D geometric stress including the antisymmetric spin torsion.
        spin_alignment: 0 (No Spin), -1 (Antiparallel p1/2), +1 (Parallel p3/2)
        """
        # Base classical metric shear (Coulomb 1/r^2 potential)
        M_Z = 1.0 / (r**2)
        
        # Antisymmetric spin torsion (scales as 1/r^3 due to metric penetration)
        M_spin = self.k_spin / (r**3)
        
        # Total Torsion Matrix Trace
        M_total = M_Z + (spin_alignment * M_spin)
        
        # Spatiotemporal Lock (Beta buffer expansion)
        beta = (M_total + np.sqrt(M_total**2 + 4.0)) / 2.0
        
        # Total Effective Geometric Stress (Energy)
        E_eff = -(1.0 / r) + self.Gamma_16D * beta
        return E_eff

    def find_state(self, spin_alignment):
        # O(1) geometric minimization
        res = minimize_scalar(self.effective_potential, args=(spin_alignment,), bounds=(0.1, 2.0), method='bounded')
        return res.x, res.fun

# --- EXECUTE THE EXPERIMENT ---
solver = FineStructure8D_Solver()

# 1. Base State (Unperturbed)
r_base, E_base = solver.find_state(0)

# 2. Antiparallel State (e.g., p_1/2) -> Spin torsion subtracts from central torsion
r_anti, E_anti = solver.find_state(-1)

# 3. Parallel State (e.g., p_3/2) -> Spin torsion adds to central torsion
r_para, E_para = solver.find_state(1)

print("--- 8D FINE STRUCTURE SPLITTING RESULTS ---")
print(f"Base State (No Spin):     r = {r_base:.5f} a0  |  Energy = {E_base:.5f} Ha")
print(f"Antiparallel (-M_spin):   r = {r_anti:.5f} a0  |  Energy = {E_anti:.5f} Ha (Deeper/Tighter)")
print(f"Parallel (+M_spin):       r = {r_para:.5f} a0  |  Energy = {E_para:.5f} Ha (Shallower/Wider)")
print(f"Energy Delta (Split):     {abs(E_para - E_anti):.5f} Ha")

# --- PLOT THE BIFURCATION ---
r_vals = np.linspace(0.3, 0.45, 500)
E_base_vals = [solver.effective_potential(r, 0) for r in r_vals]
E_anti_vals = [solver.effective_potential(r, -1) for r in r_vals]
E_para_vals = [solver.effective_potential(r, 1) for r in r_vals]

plt.figure(figsize=(10, 6))
plt.plot(r_vals, E_base_vals, label='Base State (No Spin)', color='black', linestyle='--')
plt.plot(r_vals, E_anti_vals, label='Antiparallel Lock ($p_{1/2}$)', color='blue')
plt.plot(r_vals, E_para_vals, label='Parallel Lock ($p_{3/2}$)', color='red')

# Mark the minima (the O(1) lock points)
plt.scatter([r_anti, r_base, r_para], [E_anti, E_base, E_para], color=['blue', 'black', 'red'], zorder=5)

plt.title("8D Symplectic Manifold: Native Fine Structure Splitting", fontsize=14)
plt.xlabel("Radial Metric Condensation ($a_0$)", fontsize=12)
plt.ylabel("Effective Geometric Stress (Hartrees)", fontsize=12)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.savefig("fine_structure_bifurcation.png", dpi=300)
print("\nPlot saved as 'fine_structure_bifurcation.png'")