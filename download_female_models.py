"""
Download both male and female 3D organ models from HuBMAP CCF Reference Library.
"""

import urllib.request
import os
import ssl

# Create models directory
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = "https://ccf-ontology.hubmapconsortium.org/objects/v1.2"

# Female models to download
FEMALE_MODELS = {
    "skin_female": {
        "name": "Body Skin (Female)",
        "url": f"{BASE_URL}/VH_F_Skin.glb"
    },
    "heart_female": {
        "name": "Human Heart (Female)",
        "url": f"{BASE_URL}/VH_F_Heart.glb"
    },
    "kidney_left_female": {
        "name": "Human Kidney Left (Female)", 
        "url": f"{BASE_URL}/VH_F_Kidney_L.glb"
    },
    "kidney_right_female": {
        "name": "Human Kidney Right (Female)",
        "url": f"{BASE_URL}/VH_F_Kidney_R.glb"
    },
    "pancreas_female": {
        "name": "Human Pancreas (Female)",
        "url": f"{BASE_URL}/VH_F_Pancreas.glb"
    }
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
    print("MedTwin - Downloading Female 3D Organ Models")
    print("Source: HuBMAP Human Reference Atlas (CC BY 4.0)")
    print("="*60 + "\n")
    
    success_count = 0
    
    for model_id, model_info in FEMALE_MODELS.items():
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
    print(f"Downloads complete: {success_count}/{len(FEMALE_MODELS)} models")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
