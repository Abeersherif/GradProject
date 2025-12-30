"""
MedTwin Asset Helper

This script helps you set up external 3D models for the visualization.
Since I cannot browse the web to verify current direct download links,
this script provides curated search links and instructions.
"""

import os
import webbrowser
import sys

ASSET_DIR = "assets"

def open_url(url):
    webbrowser.open(url)

def print_header():
    print("="*60)
    print("   MEDTWIN 3D ASSET MANAGER")
    print("="*60)

def ensure_dir():
    if not os.path.exists(ASSET_DIR):
        os.makedirs(ASSET_DIR)
        print(f"✓ Created '{ASSET_DIR}' directory")
    else:
        print(f"✓ Directory '{ASSET_DIR}' exists")

def main():
    print_header()
    ensure_dir()
    
    print("\nThe visualization uses high-quality procedural models by default.")
    print("To use custom models (GLB/GLTF), download them and place them")
    print(f"in the '{ASSET_DIR}' folder with these exact names:")
    print("\n  1. heart.glb")
    print("  2. kidneys.glb")
    print("  3. pancreas.glb")
    print("  4. eyes.glb")
    
    print("\nWould you like to open recommended free asset links? (y/n)")
    choice = input("> ").lower()
    
    if choice == 'y':
        print("\nOpening links in browser...")
        # Search links for free CC0/Royalty Free models
        print("1. Sketchfab (Heart)...")
        open_url("https://sketchfab.com/search?q=realistic+human+heart&features=downloadable&licenses=322a749bcfa841b19d44540d7706324d&type=models")
        
        print("2. Sketchfab (Kidneys)...")
        open_url("https://sketchfab.com/search?q=human+kidneys&features=downloadable&licenses=322a749bcfa841b19d44540d7706324d&type=models")
        
        print("3. Sketchfab (Pancreas)...")
        open_url("https://sketchfab.com/search?q=pancreas+anatomy&features=downloadable&licenses=322a749bcfa841b19d44540d7706324d&type=models")
        
        print("\nINSTRUCTIONS:")
        print("1. Download a model (GLTF/GLB format prefered)")
        print(f"2. Rename it (e.g., 'heart.glb')")
        print(f"3. Move it to: {os.path.abspath(ASSET_DIR)}")
        print("4. Refresh the visualization page")

if __name__ == "__main__":
    main()
