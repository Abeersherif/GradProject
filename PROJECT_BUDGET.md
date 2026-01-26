# MedTwin Project Budget (2025)

> **Exchange Rate:** 1 USD ≈ 50 EGP

---

## Budget Table

| # | Item | Type | Specifications | Cost (LE.) |
|---|------|------|----------------|------------|
| 1 | GPUs for AI Model Training | Hardware | High-performance GPUs for deep learning model training (Vast.ai RTX 4090, ~100 hrs) | **1,700** |
| 2 | Computing Infrastructure | Software | AI-VPC & RAID systems for simulation and testing (Railway Pro) | **1,000/year** |
| 3 | Storage (500 GB) | Software | Storage for medical data, simulations, and model results (NordLocker) | **1,800/year** |
| 4 | 3D Visualization Framework (BioDigital) | Software | Framework for 3D visualization of patient data (Business or Schools) | **3,000 - 5,000** |
| 5 | GeminiMed & DeepSeek APIs | Software | APIs for natural language processing and data analysis (~5M tokens/month) | **500 - 1,500/year** |
| 6 | High-performance Computing (12,000 CPU core hours) | Hardware | Required for simulations and patient data processing (Vast.ai) | **30,000** |
| 7 | Web Hosting (for API access and 3D model hosting) | Software | Hosting services for API and 3D visualization (Vercel/Railway) | **1,200 – 3,000/year** |

---

## Total Estimated Cost

| Category | Cost (LE.) |
|----------|-----------|
| GPU Training (one-time) | 1,700 |
| HPC Core Hours (one-time) | 30,000 |
| 3D Visualization (BioDigital) | 3,000 - 5,000 |
| Yearly Recurring (Infrastructure, Storage, APIs, Hosting) | 4,500 - 7,300 |
| **TOTAL Year 1** | **~39,200 - 44,000 LE** |

---

## Detailed Pricing Sources (2025)

### 1. GPU Cloud Pricing
| Provider | GPU | Price/Hour (USD) | Source |
|----------|-----|------------------|--------|
| Vast.ai | RTX 4090 | $0.34 | [vast.ai](https://vast.ai) |
| Vast.ai | RTX 3090 | $0.13 | [vast.ai](https://vast.ai) |
| RunPod | RTX 4090 | $0.34 | [runpod.io](https://runpod.io/gpu-instance/pricing) |
| RunPod | RTX 3090 Spot | $0.19 | [runpod.io](https://runpod.io/gpu-instance/pricing) |

### 2. Storage Pricing
| Provider | Storage | Price/Month (USD) | Source |
|----------|---------|-------------------|--------|
| NordLocker | 500GB | $2.99 | [nordlocker.com](https://nordlocker.com) |
| pCloud | 500GB | $4.99 | [pcloud.com](https://pcloud.com) |
| pCloud Lifetime | 500GB | $199 (one-time) | [pcloud.com](https://pcloud.com) |

### 3. API Pricing (Per Million Tokens)
| Provider | Model | Input | Output | Source |
|----------|-------|-------|--------|--------|
| DeepSeek | V3 (cache hit) | $0.07 | $0.42 | [platform.deepseek.com](https://platform.deepseek.com) |
| DeepSeek | V3 (cache miss) | $0.28 | $0.42 | [platform.deepseek.com](https://platform.deepseek.com) |
| DeepSeek | Reasoner | $0.56 | $1.68 | [cloudzero.com](https://cloudzero.com) |

### 4. Web Hosting
| Provider | Plan | Price/Month (USD) | Source |
|----------|------|-------------------|--------|
| Vercel | Hobby | Free | [vercel.com/pricing](https://vercel.com/pricing) |
| Vercel | Pro | $20/user | [vercel.com/pricing](https://vercel.com/pricing) |
| Railway | Hobby | $5 | [railway.com/pricing](https://railway.com/pricing) |
| Railway | Pro | $20 | [railway.com/pricing](https://railway.com/pricing) |

### 5. 3D Visualization
| Framework | License | Cost | Source |
|-----------|---------|------|--------|
| Three.js | MIT (Open Source) | FREE | [threejs.org](https://threejs.org) |
| Babylon.js | Apache 2.0 | FREE | [babylonjs.com](https://babylonjs.com) |
| Unity Pro | Commercial | $2,200/year | [unity.com/pricing](https://unity.com/pricing) |

---

## Cost-Saving Tips Applied

1. ✅ **Three.js instead of Unity** - Completely FREE and open-source
2. ✅ **Vast.ai for GPU** - Up to 80% cheaper than AWS/Azure
3. ✅ **DeepSeek API** - Much cheaper than Gemini/OpenAI
4. ✅ **NordLocker/pCloud** - Cheaper than AWS S3 for small projects
5. ✅ **Railway/Vercel Hobby tier** - $5-20/month vs $50+ for traditional VPS

---

*Last Updated: December 2025*
