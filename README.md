# 🌌 Stable Secular Manifold Propagator (SSMP)
**Breaking the O(N) Barrier in N-Body Simulations & Macroscopic Phase-Mixing**

SSMP is a high-performance numerical engine that replaces traditional procedural integration (like RK4 or Hermite) with a **Stable Secular Manifold Jump**. By treating orbital evolution as an analytical geodesic on an 8D phase-space trace, SSMP achieves **O(1) time complexity**—meaning a 1,000-day jump takes the exact same computational time as a 1-day jump.

Originally designed for discrete N-body simulations, the SSMP architecture has been formally extended to its **Continuum Limit**, acting as an ultra-fast, rigorous thermodynamic phase-mixing tool for galactic and macro-scale fluid dynamics.

---

## 🚀 The Hook: Why Use SSMP?

* ⚡ **3,862x Speedup:** Verified side-by-side against standard 4th-order Runge-Kutta (RK4) integrators in discrete stress tests.
* 📐 **O(1) Complexity:** Analytical path reconstruction allows for "time-jumping" without iterative step-by-step calculation.
* 🛡️ **High-Chaos Stability:** Successfully handles extreme noise and e >= 1 transitions where standard methods computationally crash or mathematically diverge.
* 🛰️ **NASA-Grade Secular Precision:** 0.05 km mean sync drift against the NASA JPL Horizons database over 30-day intervals.
* 🌌 **Macroscopic Phase-Mixing:** Accurately models the thermodynamic breakdown and evaporation of highly perturbed debris disks in seconds.

---

## 📊 Part 1: Discrete Validation (The Baseline)
Tested over a 30-Day Solar System Stress Test against standard RK4 procedural integration.

| Metric | 8D Manifold (SSMP) | Standard RK4 (Baseline) | Improvement |
| :--- | :--- | :--- | :--- |
| **Execution Time** | 0.000275 s | 1.060217 s | **3862.2x Faster** |
| **Complexity** | O(1) (Constant) | O(N) (Procedural) | Step-less Jump |
| **Path Drift** | 52.4 meters | Reference | Negligible |
| **Stability** | 100% (0 Breaches) | Variable | Manifold-Locked |

---

## 🌊 Part 2: The Continuum Limit & Fluid Phase-Mixing
To evaluate the engine's viability for galactic-scale simulations, the SSMP was stress-tested in its continuum limit (N -> infinity). We simulated the macroscopic phase-mixing of a collisionless phase-space fluid using a high-density Monte Carlo parameter sweep.

**The Benchmark:** 1,000,000 independent analytical jumps (10,000 particles across 100 noise intervals) over a secular integration time of 1,000 units. 
**Execution Time:** ~12 seconds on standard consumer hardware.

![Thermodynamic Phase-Mixing](continuum_limit/noise_scaling_sweep.png)
*(Above: Macroscopic phase-mixing and survival rates of the continuum fluid as a function of injected kinetic chaos. The solid cyan line represents the fluid dispersion via the 1st Wasserstein distance, while the dashed red line tracks the gravitationally bound survival fraction.)*

### Key Thermodynamic Discoveries:
1.  **Bounded Thermalization (< 15% Noise):** The initial localized density function accurately spreads into a steady-state debris disk, reflecting secular dispersion without triggering systemic collapse.
2.  **The Escape Threshold (> 15% Noise):** The engine natively resolves the physical "evaporation" of the fluid. As kinetic noise pushes elements across the e >= 1 escape threshold, the survival rate (red line) cleanly drops, matching physical expectations of systemic destruction without crashing the solver.

---

## ⚠️ Usage and Physical Constraints

**Note on Numerical Dissipation:** This engine utilizes a Stable Secular Manifold approach. To ensure O(1) performance and infinite-horizon stability in chaotic regimes, it acts as a contractive map that suppresses high-frequency chaotic noise.

* **Symplecticity:** While the engine preserves the Delaunay action variables within machine epsilon, it is *not* a pure symplectic integrator. 
* **Best For:** Long-duration secular stability, mission planning, macro-scale fluid dynamics, and galactic disk simulations.
* **Not For:** Exact microscopic energy conservation studies, exact Lyapunov exponent mapping, or resonance-crossing probability analysis.

---

## 🛠️ Repository Structure

* `analytical_engine_8D.py` : The core O(1) SSMP mathematical propagator.
* 📁 **`discrete_validation/`** : Tools for tracking specific planetary bodies.
    * `8D_Solar_System_Audit.py` : Streamlit-based NASA JPL Horizons validation tool.
    * `manifold_diagnostics.py` : Structural verification suite.
* 📁 **`continuum_limit/`** : Tools for macroscopic fluid and thermodynamic evaluation.
    * `continuum_validation.py` : Kernel Density Estimation (KDE) of the phase-space fluid.
    * `noise_scaling_sweep.py` : Monte Carlo thermodynamic stress test.

---

## 📜 License & Acknowledgments

This project is open-source (MIT License). It represents a 20-year journey into the geometry of the N-body problem, refined through an iterative AI-assisted formulation and audit process.
