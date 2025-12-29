"""Download female eye models from HuBMAP"""
import urllib.request
import os
import ssl

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
ssl._create_default_https_context = ssl._create_unverified_context
BASE_URL = "https://ccf-ontology.hubmapconsortium.org/objects/v1.2"

MODELS = {
    "eye_left_female": f"{BASE_URL}/VH_F_Eye_L.glb",
    "eye_right_female": f"{BASE_URL}/VH_F_Eye_R.glb"
}

for name, url in MODELS.items():
    filepath = os.path.join(MODELS_DIR, f"{name}.glb")
    if os.path.exists(filepath):
        print(f"{name}: already exists")
        continue
    try:
        print(f"Downloading {name}...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as r:
            with open(filepath, 'wb') as f:
                f.write(r.read())
        print(f"  Done: {os.path.getsize(filepath)/1024:.1f} KB")
    except Exception as e:
        print(f"  Failed: {e}")

print("\nFemale eye models downloaded!")
