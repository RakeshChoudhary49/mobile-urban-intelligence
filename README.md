# 🚌 AI-Powered Mobile Urban Intelligence Platform

> Transforming public transport buses into mobile urban sensing units using edge AI + centralized analytics.

**Problem Statement ID:** 26124
**Domain:** Smart Cities / Urban Mobility / Computer Vision
**SIH 2026 Internal Hackathon — Ranked 13th out of 150 teams (Top 9%)**

---

## 📖 Overview

Urban public transport buses traverse every major road daily and increasingly carry multiple cameras. This project turns them into **intelligent sensing platforms** that detect:

- 🕳️ **Road defects** — potholes, cracks, damaged surfaces
- 🚧 **Missing infrastructure** — dividers, zebra crossings, traffic signs
- 🚶 **Vulnerable pedestrians** — school zones, crossing risks
- 🚗 **Traffic incidents** — hit-and-run, rash driving (with ANPR)
- 🚦 **Congestion** — vehicle density, traffic bottlenecks

Data is processed **on the edge** (onboard the bus) and only lightweight metadata is sent to a **central command center** — achieving **99% bandwidth reduction** over raw video transmission.

## ✨ Key Features

### Onboard Edge AI
- **Multi-model inference:** YOLOv8 (general) + custom-trained pothole detector
- **Custom pothole model:** mAP@0.5 = **0.75**, Precision = **0.82**, Recall = **0.67**
- **Trained via transfer learning** on annotated Indian road dataset
- **Multi-class detection:** potholes, pedestrians, vehicles, missing infrastructure
- **ByteTrack** for deduplication across frames
- **Offline-first:** events buffer in SQLite when connectivity drops
- **Low bandwidth:** ~2 KB JSON/event vs ~50 MB video clip

### Central Command Center
- **REST API** (FastAPI) with OpenAPI/Swagger docs
- **WebSocket** live event streaming
- **8-page dashboard** (React + Vite + Leaflet):
  - Command Center (KPIs + live feed)
  - Live GIS Map (event markers, clusters)
  - Traffic Analytics (speed trends)
  - Road Conditions (hazard distribution)
  - Incidents (ANPR, dispatch actions)
  - Fleet Monitoring (real-time bus tracker)
  - Evidence Vault (frame snapshots)
  - Admin (simulator controls, diagnostics)
- **ANPR module** for hit-and-run incidents
- **Simulator** for scale testing & demo

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Edge AI** | Python, YOLOv8 (Ultralytics), OpenCV, ByteTrack, SQLite |
| **Backend** | FastAPI, SQLAlchemy, Pydantic, Uvicorn, WebSocket |
| **Frontend** | React, Vite, Leaflet, Recharts |
| **Database** | SQLite (PostGIS-ready for production) |
| **Deployment** | Docker, docker-compose |

---

## 📂 Project Structure


## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (3.12 recommended)
- Node.js 18+
- (Optional) CUDA-compatible GPU for faster inference

### 1. Clone & Setup

```bash
git clone https://github.com/<your-username>/mobile-urban-intelligence.git
cd mobile-urban-intelligence

# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Edge
cd ../edge
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install

2### Start the Central Server
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

3### Start the Dashboard
cd frontend
npm run dev


5## Run the Fleet (4 buses in parallel)
# Terminal 1
python run.py --video "data/bus_01.mp4" --bus-code BUS-101

# Terminal 2
python run.py --video "data/bus_02.mp4" --bus-code BUS-102

# Terminal 3
python run.py --video "data/bus_03.mp4" --bus-code BUS-103

# Terminal 4
python run.py --video "data/bus_04.mp4" --bus-code BUS-104
