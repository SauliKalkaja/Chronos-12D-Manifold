import numpy as np
import json
import time
from analytical_engine_8D import Manifold8DEngine

def n_body_accel(r, mu):
    return -mu * r / (np.linalg.norm(r)**3)

def rk4_step(r, v, dt, mu):
    k1_v = n_body_accel(r, mu)
    k1_r = v
    k2_v = n_body_accel(r + 0.5*dt*k1_r, mu)
    k2_r = v + 0.5*dt*k1_v
    k3_v = n_body_accel(r + 0.5*dt*k2_r, mu)
    k3_r = v + 0.5*dt*k2_v
    k4_v = n_body_accel(r + dt*k3_r, mu)
    k4_r = v + dt*k3_v
    v_new = v + (dt/6.0)*(k1_v + 2*k2_v + 2*k3_v + k4_v)
    r_new = r + (dt/6.0)*(k1_r + 2*k2_r + 2*k3_r + k4_r)
    return r_new, v_new

def run_monte_carlo(iterations=50):
    with open('config.json', 'r') as f:
        config = json.load(f)

    engine = Manifold8DEngine(mu=config['mu'])
    T_total = 86400.0 * 30
    dt_rk4 = 60.0 # 1-minute steps
    
    print(f"🚀 Starting {iterations}-run Symplectic vs. RK4 Audit...")

    results = []
    for i in range(iterations):
        # Inject positional noise
        r0 = np.array(config['initial_r']) * (1.0 + np.random.normal(0, 0.01, 3))
        v0 = np.array(config['initial_v'])

        # --- 8D Manifold Jump ---
        t0 = time.time()
        r_8d = engine.propagate(0, None, r0, v0, T_total, {'M_int': 0}, mc_mode=True)
        t_8d = time.time() - t0

        # --- Standard RK4 ---
        t1 = time.time()
        r_rk, v_rk = r0.copy(), v0.copy()
        for _ in range(int(T_total/dt_rk4)):
            r_rk, v_rk = rk4_step(r_rk, v_rk, dt_rk4, config['mu'])
        t_rk = time.time() - t1

        drift = np.linalg.norm(r_8d - r_rk)
        results.append((t_8d, t_rk, drift))

    avg_8d = np.mean([x[0] for x in results])
    avg_rk = np.mean([x[1] for x in results])
    
    print("\n" + "█"*40)
    print(f"✅ Audit Finished.")
    print(f"   8D Jump Speed: {avg_8d:.6f} s")
    print(f"   RK4 Step Speed: {avg_rk:.6f} s")
    print(f"   Speedup: {avg_rk/avg_8d:.1f}x")
    print(f"   Mean Path Sync Drift: {np.mean([x[2] for x in results]):.4f} km")
    print("█"*40)

if __name__ == "__main__":
    run_monte_carlo()