# 🩺 MedTwin Visualization Guide: Using Custom Models

The MedTwin 3D engine now supports **Physically Based Rendering (PBR)** and High-Fidelity models. By default, it generates realistic organic shapes using code, but you can import professional medical 3D models.

## 📁 Where to put models
Place your `.glb` or `.gltf` files in the `assets/` folder.

## 🏷️ Naming Convention
The system automatically looks for these specific filenames:

| Organ | Required Filename |
|-------|-------------------|
| ❤️ Heart | `heart.glb` |
| 🫘 Kidneys | `kidneys.glb` |
| 🥞 Pancreas | `pancreas.glb` |
| 👁️ Eyes | `eyes.glb` |

## 🌟 Visual Features (Unity-like Graphics)

### 1. PBR Materials ("The Wet Look")
The engine overrides the material of any imported model to simulate biological tissue:
- **Subsurface Scattering**: Simulates light entering the skin/tissue.
- **Clearcoat**: Adds a wet, glossy layer on top.
- **Roughness/Metalness**: Tuned for organic fleshy appearance.

### 2. Cinematic Post-Processing
- **Bloom**: Organs "glow" slightly, creating a sci-fi medical interface look.
- **Tone Mapping**: ACES Filmic mapping for realistic light handling.
- **Anti-aliasing**: Sharp edges.

### 3. Smart Fallback
If you don't have a `heart.glb` file, the system automatically generates a realistic high-poly procedural heart so the visualization never breaks.

## 📥 Recommended Resources for Free Models
- **Sketchfab**: Search for "Human Anatomy" (Filter by: Downloadable)
- **TurboSquid**: Filter by "Free" and "glTF"
- **OpenAnatomy**: Open source medical models
