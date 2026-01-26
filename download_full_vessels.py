"""Download full-body blood vessels from HuBMAP VCCF"""
import urllib.request
import os
import ssl

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
ssl._create_default_https_context = ssl._create_unverified_context
BASE_URL = "https://ccf-ontology.hubmapconsortium.org/objects/v1.2"

# Full body vascular models from HuBMAP
MODELS = {
    "blood_vasculature_full": f"{BASE_URL}/VH_M_Blood.glb",
    "blood_vessels_arterial": f"{BASE_URL}/VH_M_Large_Blood_Vessels.glb",
}

for name, url in MODELS.items():
    filepath = os.path.join(MODELS_DIR, f"{name}.glb")
    if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
        print(f"{name}: already exists")
        continue
    try:
        print(f"Downloading {name} from {url}...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=120) as r:
            with open(filepath, 'wb') as f:
                f.write(r.read())
        print(f"  Done: {os.path.getsize(filepath)/1024:.1f} KB")
    except Exception as e:
        print(f"  Failed: {e}")

print("\nDone!")
