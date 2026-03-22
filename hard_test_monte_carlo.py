import numpy as np
import time
import json
from analytical_engine_8D import Manifold8DEngine

def n_body_acceleration(r, mu):
    """Standard Newtonian acceleration for RK4 baseline."""
    r_mag = np.linalg.norm(r)
    return -mu * r / (r_mag**3)

def rk4_step(r, v, dt, mu):
    """Standard 4th Order Runge-Kutta step."""
    k1_v = n_body_acceleration(r, mu)
    k1_r = v

    k2_v = n_body_acceleration(r + 0.5 * dt * k1_r, mu)
    k2_r = v + 0.5 * dt * k1_v

    k3_v = n_body_acceleration(r + 0.5 * dt * k2_r, mu)
    k3_r = v + 0.5 * dt * k2_v

    k4_v = n_body_acceleration(r + dt * k3_r, mu)
    k4_r = v + dt * k3_v

    v_new = v + (dt / 6.0) * (k1_v + 2*k2_v + 2*k3_v + k4_v)
    r_new = r + (dt / 6.0) * (k1_r + 2*k2_r + 2*k3_r + k4_r)
    return r_new, v_new

def run_comparative_audit(iterations=100):
    with open('config.json', 'r') as f:
        config = json.load(f)

    mu = config.get('mu', 132712440041.939)
    engine = Manifold8DEngine(mu=mu)
    
    T_total = 86400.0 * 30  # 30 Days
    dt_rk4 = 60.0           # 60-second steps for RK4 precision
    steps = int(T_total / dt_rk4)

    print(f"🔬 Starting Comparative Audit: 8D Manifold vs. RK4 ({iterations} runs)")
    print(f"   RK4 config: {steps} steps per run | 8D config: 1 Analytical Jump per run\n")

    results = []

    for i in range(iterations):
        # Initial Conditions with slight noise
        r0 = np.array(config['initial_r']) * (1.0 + np.random.normal(0, 0.01, 3))
        v0 = np.array(config['initial_v'])

        # --- 1. THE 8D MANIFOLD JUMP ---
        start_8d = time.time()
        r_8d = engine.propagate(0, None, r0, v0, T_total, {'M_int': 0}, mc_mode=True)
        time_8d = time.time() - start_8d

        # --- 2. THE RK4 STEPPING ---
        start_rk4 = time.time()
        r_rk, v_rk = r0.copy(), v0.copy()
        for _ in range(steps):
            r_rk, v_rk = rk4_step(r_rk, v_rk, dt_rk4, mu)
        time_rk4 = time.time() - start_rk4

        # Calculate Drift
        drift_km = np.linalg.norm(r_8d - r_rk)
        results.append({'8d_t': time_8d, 'rk_t': time_rk4, 'drift': drift_km})

    avg_8d = np.mean([x['8d_t'] for x in results])
    avg_rk = np.mean([x['rk_t'] for x in results])
    avg_drift = np.mean([x['drift'] for x in results])

    print("█" * 50)
    print(f"📊 AUDIT RESULTS (Averages over {iterations} runs)")
    print(f"   8D Manifold Jump Time: {avg_8d:.6f} s")
    print(f"   Standard RK4 Time:     {avg_rk:.6f} s")
    print(f"   Speedup Factor:        {avg_rk / avg_8d:.1f}x faster")
    print(f"   Relative Sync Drift:   {avg_drift:.4f} km")
    print("█" * 50)

if __name__ == "__main__":
    run_comparative_audit()
