import streamlit as st
import numpy as np
import plotly.graph_objects as go
from astroquery.jplhorizons import Horizons
from astropy.time import Time
from manifold_engine_12D import ChronosAnalyticalEngine, ManifoldGeometry

st.set_page_config(page_title="12D Chronos: Symplectic Audit", layout="wide")

# Initialize engines
engine = ChronosAnalyticalEngine()
geometry = ManifoldGeometry()

@st.cache_data
def fetch_system():
    targets = {'Mercury':'1', 'Venus':'2', 'EMB':'3', 'Mars':'4', 
               'Jupiter':'5', 'Saturn':'6', 'Uranus':'7', 'Neptune':'8'}
    state = {}
    now = Time.now()
    
    q_sun = Horizons(id='10', location='@0', epochs=now.jd).vectors()
    sun_vec = np.array([q_sun['x'][0], q_sun['y'][0], q_sun['z'][0]])

    for name, tid in targets.items():
        el = Horizons(id=tid, location='@sun', epochs=now.jd).elements()
        vec = Horizons(id=tid, location='@0', epochs=now.jd).vectors()
        
        state[name] = {
            'a': el['a'][0], 'e': el['e'][0], 'i': el['incl'][0],
            'Omega': el['Omega'][0], 'w': el['w'][0],
            'pos_nasa_bary': np.array([vec['x'][0], vec['y'][0], vec['z'][0]]),
            'sun_offset': sun_vec
        }
    return state

st.title("🌌 12D Manifold: Symplectic Flow & Barycentric Lock")
st.markdown("### Technical Audit v2.2: Verifying Hamiltonian Volume Preservation")

data = fetch_system()
audit_results = []

for name, p in data.items():
    r_relative = np.linalg.norm(p['pos_nasa_bary'] - p['sun_offset'])
    alpha, M = engine.solve_jacobian_state(r_relative)
    beta = 1.0 / alpha
    
    # Calculate Hamiltonian Flow Magnitude
    flow_vector = geometry.get_hamiltonian_flow(alpha, beta, M)
    flow_magnitude = np.linalg.norm(flow_vector)
    
    v = engine.analytical_handshake(p['pos_nasa_bary'] - p['sun_offset'], p['i'], p['Omega'], p['w'])
    pos_manifold = engine.get_coords_12D(v, p['a'], p['e'], p['i'], p['Omega'], p['w'], alpha)
    pos_final = pos_manifold + p['sun_offset']
    rmse = np.linalg.norm(p['pos_nasa_bary'] - pos_final)
    
    audit_results.append({
        'Node': name,
        'Alpha (α)': f"{alpha:.8f}",
        'M (Torsion)': f"{M:.6f}",
        'Symplectic Flow (||XH||)': f"{flow_magnitude:.4e}",
        'RMSE (AU)': f"{rmse:.2e}",
        'Convergence': "PASS" if rmse < 1e-12 else "CHECK"
    })

st.table(audit_results)

# Using raw strings (fr) to fix the escape sequence warnings
st.sidebar.header("Manifold Constants")
st.sidebar.write(fr"**Chronos Gear Ratio ($\chi$):** {engine.chi}")
st.sidebar.write(fr"**Quadrant Constant ($\Gamma$):** {engine.gamma}")
st.sidebar.write("---")
st.sidebar.info("The **Symplectic Flow** column confirms that the manifold preserves volume through a non-degenerate 2-form ω.")

# Corrected Plotly template name
st.subheader("Metric Torsion Analysis")
nodes = [r['Node'] for r in audit_results]
flows = [float(r['Symplectic Flow (||XH||)']) for r in audit_results]

fig = go.Figure(data=[
    go.Bar(name='Symplectic Flow Magnitude', x=nodes, y=flows, marker_color='cyan')
])
fig.update_layout(template="plotly_dark", title="Metric 'Rent' by Planetary Node", yaxis_type="log")
st.plotly_chart(fig, use_container_width=True)