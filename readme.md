# Keithley 2230G Instrument Automation

A comprehensive, full‑stack solution for remote control, configuration, and real‑time monitoring of the Keithley 2230G power supply. Harness the power of gRPC, FastAPI, and a modern web interface to streamline your laboratory workflows.

---

## Overview

This project delivers a robust pipeline for end‑to‑end instrument automation:

1. **gRPC Server**
   Wraps low‑level PyVISA commands to discover, connect, and command instruments programmatically.
2. **FastAPI Bridge**
   Exposes intuitive REST endpoints that sit atop gRPC, enabling easy integration with scripts, dashboards, or other services.
3. **Interactive Frontend**
   A React‑based web UI built with Chart.js for seamless device selection, channel tuning, output control, and live voltage plotting.

**Core Workflow**

* Scan and list VISA‑compatible resources
* Connect to your Keithley 2230G by address
* Configure channel voltage, current, and safety limits
* Toggle channel outputs ON/OFF
* View real‑time voltage data over a rolling 5‑minute window
* Clear and switch data streams when changing channels

---

## Key Features

* **Safe, Thread‑Aware VISA Access**
  All PyVISA calls are serialized via threading locks to avoid race conditions.
* **Background Monitoring**
  Dedicated thread captures voltage readings every second and retains a 5‑minute sliding window.
* **gRPC ↔ REST Integration**
  Flexible architecture lets you choose gRPC or HTTP for instrument control and data retrieval.
* **Dynamic Plotting**
  Interactive voltage charts that reset and redraw seamlessly when channels change.
* **Robust Error Handling**
  Clear messages and HTTP/gRPC status codes ensure visibility into failures.
* **Modular Codebase**
  Organized services, routes, and utilities for easy extension or reuse with other instruments.

---

## Tech Stack

* **Python 3.12** — FastAPI, grpcio, pyvisa
* **gRPC** — Protobuf definitions, synchronous and asynchronous service implementations
* **Frontend** — React, Axios, Chart.js
* **Concurrency** — Python threading for non‑blocking background tasks
* **Deployment** — Uvicorn server, optional Docker containerization

---

## Installation & Quickstart

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/instrument‑automation.git
   cd instrument‑automation
   ```

2. **Install dependencies & launch backend**

   ```bash
   python -m venv venv            # Create virtual environment
   source venv/bin/activate      # Activate (Linux/Mac)
   pip install -r requirements.txt
   python grpc_server.py         # Start gRPC on port 50051
   python -m main                # Start FastAPI on port 8000
   ```

3. **Launch the frontend**

   ```bash
   python -m main                   # React UI at http://localhost:3000
   ```

4. **Use the app**

   * Open `http://localhost:3000` (or `http://localhost:8000/docs` for API docs)
   * Browse devices, connect, configure channels, and watch live voltage curves.

---

## 🤝 Contributing

Feedback, improvements, and new feature ideas are welcome! Feel free to open an issue or submit a pull request.

---

## 📄 License

Distributed under the [MIT License](./LICENSE).

*Empower your bench‑top workflows with automated precision.*
