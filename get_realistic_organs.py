"""
Get Photorealistic Organs Script (v3 - Body Avatar)
===================================================

This script opens the BEST search pages for models.
Since specific model links can expire, this sends you to the search results
where you can pick the best FREE model you like.

INSTRUCTIONS:
1. The script will open 5 tabs (Body, Heart, Kidney, Pancreas, Eye).
2. On each page, look for models with the "Download" icon.
3. Download the "gltf" or "glb" format.
4. Rename and move to 'assets' folder as before.
"""

import webbrowser
import time

def open_robust_links():
    print("="*60)
    print("   OPENING ROBUST MODEL SEARCHES")
    print("="*60)
    
    base_url = "https://sketchfab.com/search?features=downloadable&type=models&q="

    print("\n1. Searching for: Human Body (Male/Female)...")
    # Search for a base mesh that we can make transparent
    webbrowser.open(base_url + "human+body+base+mesh")
    time.sleep(1)
    
    print("2. Searching for: Realistic Human Heart...")
    webbrowser.open(base_url + "human+heart+realistic")
    time.sleep(1)

    print("3. Searching for: Human Kidney...")
    webbrowser.open(base_url + "human+kidney+anatomy")
    time.sleep(1)

    print("4. Searching for: Pancreas...")
    webbrowser.open(base_url + "human+pancreas")
    time.sleep(1)

    print("5. Searching for: Human Eye...")
    webbrowser.open(base_url + "realistic+human+eye")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("1. Click on a model you like.")
    print("2. Click 'Download 3D Model' -> 'GLB'.")
    print("3. Rename files -> 'body.glb', 'heart.glb', etc.")
    print("4. Move to -> d:/Year 4 semster 1/GRAD PROJECT/medtwin/assets/")
    print("5. Refresh your index.html page.")
    print("="*60)

if __name__ == "__main__":
    open_robust_links()
