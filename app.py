import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- Helper Functions ---
def fetch_gdpnow():
    url = "https://www.atlantafed.org/cqer/research/gdpnow"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find the GDPNow value
    try:
        text = soup.find(text=lambda t: t and "%" in t and "GDPNow" in t)
        value = float(text.split("GDPNow estimate is")[-1].split("%")[0].strip())
        return value
    except:
        return None

def fetch_nyfed_nowcast():
    url = "https://www.newyorkfed.org/research/policy/nowcast"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the Nowcast value
    try:
        paragraph = soup.find("p", text=lambda t: t and "%" in t and "GDP" in t)
        if paragraph:
            percent_text = paragraph.get_text().split("%")[0].split()[-1]
            return float(percent_text)
    except:
        return None

def compute_composite(gdpnow, nowcast):
    # RMSE-based weights (1/variance)
    gdpnow_rmse = 1.5
    nowcast_rmse = 1.8

    w1 = 1 / gdpnow_rmse**2
    w2 = 1 / nowcast_rmse**2

    total = w1 + w2
    w1 /= total
    w2 /= total

    composite = w1 * gdpnow + w2 * nowcast
    return composite, w1, w2

# --- Streamlit App ---
st.set_page_config(page_title="Composite GDP Nowcast", layout="centered")
st.title("📊 Composite GDP Nowcast")

st.write("This dashboard combines the Atlanta Fed's GDPNow and the New York Fed's Nowcast using a weighted average based on historical accuracy.")

with st.spinner("Fetching latest data..."):
    gdpnow = fetch_gdpnow()
    nowcast = fetch_nyfed_nowcast()

if gdpnow is None or nowcast is None:
    st.error("Could not fetch one or both nowcast values. Please check the source websites.")
else:
    composite, w1, w2 = compute_composite(gdpnow, nowcast)

    st.metric("Atlanta Fed GDPNow", f"{gdpnow:.2f}%")
    st.metric("New York Fed Nowcast", f"{nowcast:.2f}%")
    st.markdown("---")
    st.metric("📌 Composite Nowcast (Weighted)", f"{composite:.2f}%")

    st.caption(f"Weights: {w1*100:.1f}% GDPNow, {w2*100:.1f}% NY Fed Nowcast")
    st.caption("Weights based on RMSE: 1.5 (GDPNow) vs 1.8 (Nowcast)")

