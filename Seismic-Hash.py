import requests
import numpy as np
import matplotlib.pyplot as plt
import hashlib  # <--- NEW: Required for the upgrade
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.signal.cross_correlation import correlate
import warnings

# Suppress internal Obspy warnings for a cleaner console
warnings.filterwarnings("ignore")

# ==========================================
# MODULE 1: THE GEO-GRABBER (Discovery Mode)
# ==========================================
def get_my_coordinates():
    """
    Finds user location via IP to pick the nearest sensors.
    """
    try:
        response = requests.get('http://ip-api.com/json/', timeout=3)
        data = response.json()
        if data['status'] == 'success':
            print(f"📍 Detected: {data['city']}, {data['regionName']} ({data['lat']}, {data['lon']})")
            return data['lat'], data['lon']
    except:
        pass
    print("📍 Location fail. Defaulting to Southeast US.")
    return 34.0, -84.0 

def find_active_stations(client, lat, lon):
    """
    Returns a LIST of the top nearby High-Res stations.
    We scan multiple networks (US, IU, GS, etc) to find the best hardware.
    """
    print("📡 Scanning for High-Res (BHZ) Candidates...")
    candidates = []
    try:
        # Search radius: 8 degrees (~800km) to ensure we find *something*
        inventory = client.get_stations(
            network="US,IU,GS,TA,N4,CI,CO", 
            latitude=lat, longitude=lon, maxradius=8.0, 
            level="station", channel="BHZ", matchtimeseries=True
        )
        
        # Flatten the inventory into a simple list of codes
        for network in inventory:
            for station in network:
                candidates.append((network.code, station.code))
        
        print(f"   >> Found {len(candidates)} potential nodes nearby.")
        return candidates
    except Exception as e:
        print(f"   >> Scan Error: {e}")
        return [("US", "GOGA"), ("IU", "CCM")] # Backup defaults

# ==========================================
# MODULE 2: THE DATA ENGINE (Robust)
# ==========================================
def get_seismic_data(client, network, station, start_time, duration):
    """
    Fetches data and applies physics filters to isolate the 'Ocean Hum'.
    """
    try:
        # Request High-Resolution (BHZ) data
        st = client.get_waveforms(
            network=network, station=station, location="*", channel="BHZ", 
            starttime=start_time, endtime=start_time + duration
        )
        trace = st[0]
        
        # Physics Processing
        trace.detrend("linear") # Remove temperature drift
        trace.taper(0.05)       # Soften edges
        
        # Filter: Target the "Secondary Microseism" (0.1 Hz - 0.8 Hz)
        # This is the most consistent global signal caused by ocean waves.
        trace.filter("bandpass", freqmin=0.1, freqmax=0.8)
        
        return trace
    except Exception:
        # Return None so the loop knows to try the next station
        return None

# ==========================================
# MODULE 3: THE HASHER (The Upgrade)
# ==========================================
def generate_robust_key(correlation_wave):
    """
    UPGRADE: Instead of raw bit-slicing, we Hash the physical wave data.
    This creates a cryptographically uniform 256-bit key from the Earth signal.
    """
    # 1. Take the center 1000 points of the wave (The strongest lock)
    center = np.argmax(np.abs(correlation_wave))
    
    # Safety bounds to prevent crashing if the array is short
    start = max(0, center - 500)
    end = min(len(correlation_wave), center + 500)
    segment = correlation_wave[start:end]
    
    # 2. Convert the Float values to a Byte String
    # This captures the exact 'shape' of the wave as raw data bytes.
    # Because floats are very precise, even a microscopic difference 
    # in the wave shape results in totally different bytes.
    wave_bytes = segment.tobytes()
    
    # 3. SHA-256 Hash
    # This 'whitens' the data, turning the slow wave into a scrambled, uniform key.
    # No more repeating FFFF or 0000.
    sha_signature = hashlib.sha256(wave_bytes).hexdigest()
    
    return sha_signature.upper()

# ==========================================
# MAIN EXECUTION
# ==========================================
def run_litho_key():
    print("\n--- TECTONIC LITHOGRAPHY v5.1 (Hasher Upgrade) ---")
    client = Client("IRIS")
    
    lat, lon = get_my_coordinates()
    
    # 1. Get List of Candidates
    candidate_list = find_active_stations(client, lat, lon)
    
    # Reference Node: ANMO (Albuquerque) is the US gold standard
    net_ref, sta_ref = "IU", "ANMO"
    
    # Time Window: 20 minutes ago (to ensure data buffer is full)
    t0 = UTCDateTime.now() - 1200 
    duration = 600
    
    # 2. Station Hopper Loop
    tr_local = None
    active_station_name = ""
    
    print(f"\n⬇️ Attempting to acquire Local Stream...")
    for net, sta in candidate_list:
        print(f"   >> Pinging {net}.{sta}...", end="\r")
        tr_local = get_seismic_data(client, net, sta, t0, duration)
        
        if tr_local:
            print(f"   >> SUCCESS: Connected to {net}.{sta}      ")
            active_station_name = f"{net}.{sta}"
            break # We found a live one!
        else:
            print(f"   >> FAIL: {net}.{sta} (Offline)            ")
            
    if not tr_local:
        print("\n❌ CRITICAL: All local stations failed. Try again later.")
        return

    # 3. Get Reference Stream
    print(f"⬇️ Acquiring Reference Stream ({sta_ref})...")
    tr_ref = get_seismic_data(client, net_ref, sta_ref, t0, duration)
    
    if tr_local and tr_ref:
        print("✅ Streams Locked. Calculating Entanglement...")
        
        # Normalize Data for plotting clarity
        d1 = tr_local.data / np.max(np.abs(tr_local.data))
        d2 = tr_ref.data / np.max(np.abs(tr_ref.data))
        
        # --- THE MATH FIX ---
        # Calculate Cross-Correlation
        cc = correlate(d1, d2, 1000)
        
        # Extract Score (Max absolute value of the correlation array)
        # This tells us how well the shapes match, regardless of shift.
        score = np.max(np.abs(cc))
        
        # Generate Key (USING NEW HASHER FUNCTION)
        key = generate_robust_key(cc)
        
        print("\n" + "="*40)
        print(f"🌎 PLANETARY SYNC SCORE: {score:.4f}")
        if score > 0.1:
            print(">> STATUS: STRONG TECTONIC LOCK")
        else:
            print(">> STATUS: WEAK LOCK (Local noise high)")
        print("="*40)
        print(f"🔑 LITHOSPHERE KEY (SHA-256):\n{key}")
        print("="*40)

        # Plot
        fig, ax = plt.subplots(3, 1, figsize=(10, 8))
        ax[0].plot(tr_local.times(), d1, 'k', lw=0.5)
        ax[0].set_title(f"User Node: {active_station_name}")
        ax[0].set_ylabel("Velocity")
        
        ax[1].plot(tr_ref.times(), d2, 'r', lw=0.5)
        ax[1].set_title(f"Master Node: {sta_ref}")
        ax[1].set_ylabel("Velocity")
        
        ax[2].plot(cc, 'g', lw=1.5)
        ax[2].set_title(f"Key Waveform (Score: {score:.2f})")
        ax[2].set_ylabel("Agreement")
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    run_litho_key()