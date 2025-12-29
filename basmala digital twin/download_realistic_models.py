"""
Download realistic 3D organ models from HuBMAP CCF Reference Library.
These are anatomically correct models from the Human Reference Atlas.
License: CC BY 4.0
"""

import urllib.request
import os
import ssl

# Create models directory
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# HuBMAP CCF 3D Reference Object Library - Direct GLB links
# Source: https://hubmapconsortium.github.io/ccf/pages/ccf-3d-reference-library.html
BASE_URL = "https://ccf-ontology.hubmapconsortium.org/objects/v1.2"

MODELS = {
    "heart": {
        "name": "Human Heart (Male)",
        "url": f"{BASE_URL}/VH_M_Heart.glb"
    },
    "kidney_left": {
        "name": "Human Kidney Left (Male)", 
        "url": f"{BASE_URL}/VH_M_Kidney_L.glb"
    },
    "kidney_right": {
        "name": "Human Kidney Right (Male)",
        "url": f"{BASE_URL}/VH_M_Kidney_R.glb"
    },
    "pancreas": {
        "name": "Human Pancreas (Male)",
        "url": f"{BASE_URL}/VH_M_Pancreas.glb"
    },
    "blood_vasculature": {
        "name": "Blood Vasculature (Male)",
        "url": f"{BASE_URL}/VH_M_Blood_Vasculature.glb"
    },
    "eye_left": {
        "name": "Human Eye Left (Male)",
        "url": f"{BASE_URL}/VH_M_Eye_L.glb"
    },
    "eye_right": {
        "name": "Human Eye Right (Male)",
        "url": f"{BASE_URL}/VH_M_Eye_R.glb"
    },
    "skin": {
        "name": "Body Skin (Male)",
        "url": f"{BASE_URL}/VH_M_Skin.glb"
    }
}

# Alternative URLs if HuBMAP doesn't work
ALT_MODELS = {
    "heart": "https://raw.githubusercontent.com/AlaricBaraworski/GLBModels/main/heart.glb",
    "body": "https://raw.githubusercontent.com/AlaricBaraworski/GLBModels/main/body.glb"
}

def download_file(url, filepath):
    """Download a file from URL to filepath"""
    try:
        print(f"  Downloading from: {url[:60]}...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=60) as response:
            content = response.read()
            with open(filepath, 'wb') as f:
                f.write(content)
            
            size_mb = len(content) / (1024 * 1024)
            print(f"  ✓ Downloaded {size_mb:.2f} MB")
            return True
    except Exception as e:
        print(f"  ✗ Failed: {str(e)[:80]}")
        return False

def main():
    print("\n" + "="*60)
    print("MedTwin - Downloading Realistic 3D Organ Models")
    print("Source: HuBMAP Human Reference Atlas (CC BY 4.0)")
    print("="*60 + "\n")
    
    success_count = 0
    
    for model_id, model_info in MODELS.items():
        print(f"\n[{model_id}] {model_info['name']}")
        filepath = os.path.join(MODELS_DIR, f"{model_id}.glb")
        
        # Skip if already downloaded
        if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
            print(f"  Already exists ({os.path.getsize(filepath)/1024:.1f} KB)")
            success_count += 1
            continue
        
        if download_file(model_info["url"], filepath):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"Downloads complete: {success_count}/{len(MODELS)} models")
    print(f"Models saved to: {MODELS_DIR}")
    print("="*60 + "\n")
    
    # List downloaded files
    print("Downloaded files:")
    total_size = 0
    for f in sorted(os.listdir(MODELS_DIR)):
        if f.endswith('.glb'):
            fpath = os.path.join(MODELS_DIR, f)
            size = os.path.getsize(fpath)
            total_size += size
            print(f"  ✓ {f} ({size/1024:.1f} KB)")
    
    print(f"\nTotal size: {total_size/1024/1024:.2f} MB")
    print("\nNext step: Run index.html to see the realistic organs!")

if __name__ == "__main__":
    main()
