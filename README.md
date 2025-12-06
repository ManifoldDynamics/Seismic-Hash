# Seismic Hash 🌎🔐

**True Random Number Generation (TRNG) via Tectonic Synchronization.**

> *The Earth is always moving. We use that movement to generate entropy.*

## Overview
**Seismic Hash** is a Python utility that generates high-entropy, military-grade cryptographic keys (SHA-256) by measuring the real-time background vibration of the Earth's crust (the "Global Hum").

Unlike pseudo-random number generators (PRNGs) that rely on algorithms, Seismic Hash relies on **physical reality**. It connects to seismic stations thousands of miles apart (e.g., Missouri vs. New Mexico) and waits for a "Tectonic Lock"—a moment where the continental plate moves in sync across a vast distance.

## Features
* **Station Hopper Protocol:** Autonomously scans the IRIS seismic network (US, IU, GS) to find live high-resolution sensors nearby.
* **Tectonic Lock Detection:** Compares your local vibration against a reference node (ANMO in Albuquerque) to verify the signal is global, not local noise.
* **SHA-256 Whitening:** Converts the raw analog waveform of the Earth's movement into a uniform, whitened 256-bit hash.

## How It Works
1.  **Geo-Location:** The script detects your IP to find the nearest seismic station.
2.  **Stream Acquisition:** It pulls live `BHZ` (Vertical High-Broadband) data from the last 20 minutes.
3.  **Correlation:** It calculates the cross-correlation coefficient between your local ground motion and the master reference node.
4.  **Hashing:** If a lock is established (Correlation > 0.1), the waveform shape is hashed to produce the key.

## Installation

1. Clone the repo:
   ```bash
   git clone [https://github.com/ManifoldDynamics/seismic-hash.git](https://github.com/ManifoldDynamics/seismic-hash.git)
   cd seismic-hash
2. Install dependencies:
   ```bash
   [pip install -r requirements.txt]
3. Run:
    ```bash
   python seismic_hash.py

## Example Output
```bash
    
🌎 PLANETARY SYNC SCORE: 0.2551
>> STATUS: STRONG TECTONIC LOCK
========================================
🔑 SEISMIC HASH (SHA-256):
123D4F717BBC25FEB0ECDCFE9BEF66CBAEA8D6D2DCD63558A351EDA471CE39AF      
========================================
