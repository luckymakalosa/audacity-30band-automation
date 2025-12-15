"""
Audacity Pipe Script — 30-Band HP+LP Band-Pass (Single Track)
===============================================================

AUTHOR NOTE
-----------
• This script applies HP and LP filters on the same track per band.
• Uses 30 tracks only (1 track per band).
• ROLLOFF is dB6 for all filters.
• Normalization is applied after HP and LP.
• SAFE for automation, but slightly less precise than 60-track MixAndRender method.
"""

import sys
import time

# ---------------------------------------------------------------
# PipeClient setup
# ---------------------------------------------------------------
sys.path.append(r"D:\audacity_scripts")
import pipeclient

client = pipeclient.PipeClient()

# ---------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------
DELAY = 1.0            # seconds
BANDS = [
    (20, 25), (25, 31), (31, 40), (40, 50), (50, 63),
    (63, 80), (80, 100), (100, 125), (125, 160), (160, 200),
    (200, 250), (250, 315), (315, 400), (400, 500), (500, 630),
    (630, 800), (800, 1000), (1000, 1250), (1250, 1600), (1600, 2000),
    (2000, 2500), (2500, 3150), (3150, 4000), (4000, 5000), (5000, 6300),
    (6300, 8000), (8000, 10000), (10000, 12500), (12500, 16000), (16000, 20000)
]

# ---------------------------------------------------------------
# Helper function
# ---------------------------------------------------------------
def send_command(cmd):
    client.write(cmd, timer=True)
    time.sleep(DELAY)
    reply = client.read()
    if reply:
        print(reply)

# ===============================================================
# PHASE 1 — CREATE 30 WORKING TRACKS
# ===============================================================
print("\n📋 PHASE 1: Creating 30 working tracks from Track 0...")

# Assumes exactly ONE track exists at start
for _ in range(len(BANDS) - 1):
    send_command('SelectTracks: Mode="Set" Track="0" TrackCount="1" Start="0" End="-1"')
    send_command('Duplicate')

print("✅ Phase 1 complete: 30 tracks created")

# ===============================================================
# PHASE 2 — APPLY HP + LP FILTERS ON EACH TRACK
# ===============================================================
print("\n🎚️ PHASE 2: Applying HP + LP filters on each track...")

for band_index, (low_f, high_f) in enumerate(BANDS):
    band_label = f"Band {low_f}-{high_f} Hz"

    # Select track
    send_command(f'SelectTracks: Mode="Set" Track="{band_index}" TrackCount="1" Start="0" End="-1"')

    # High-pass
    send_command(f'High-passFilter:FREQUENCY="{low_f}" ROLLOFF="dB6"')
    send_command('Normalize:ApplyVolume="1" PeakLevel="-1" RemoveDcOffset="1" StereoIndependent="1"')

    # Low-pass
    send_command(f'Low-passFilter:FREQUENCY="{high_f}" ROLLOFF="dB6"')
    send_command('Normalize:ApplyVolume="1" PeakLevel="-1" RemoveDcOffset="1" StereoIndependent="1"')

    # Rename track
    send_command(f'SetTrackStatus: Name="{band_label}"')

print("\n✅ Phase 2 complete: 30-band HP+LP processing finished")
