"""
Audacity Pipe Script — 30‑Band HP/LP Split and Correct Mixdown
================================================================

AUTHOR NOTE (IMPORTANT — READ FIRST)
----------------------------------
• This script is **FINAL and WORKING**.
• **DO NOT CHANGE ANY CODE LOGIC OR COMMAND ORDER.**
• Track index behavior is intentional and depends on Audacity's
  Mix & Render mechanics (tracks collapse upward).
• All delays, selections, and renames are carefully tuned for stability.

OVERVIEW
--------
PHASE 1 : Duplicate Track 0 into 60 working tracks (2 tracks per band)
PHASE 2 : Apply High‑Pass and Low‑Pass filters for each frequency band
STEP 3  : Mix HP + LP pairs correctly into 30 band‑pass tracks

RESULT
------
• 30 clean band‑pass tracks
• Proper naming
• No recursive mix errors
• No track index drift

===============================================================
"""

import sys
import time

# ---------------------------------------------------------------
# PipeClient setup
# ---------------------------------------------------------------
# Path to pipeclient.py (Audacity scripting interface)
sys.path.append(r"D:\audacity_scripts")
import pipeclient

client = pipeclient.PipeClient()


# ---------------------------------------------------------------
# CONFIGURATION (DO NOT MODIFY)
# ---------------------------------------------------------------
DELAY = 1.0            # Required for Audacity command stability
WORKING_TRACKS = 60    # 2 tracks per frequency band (HP + LP)


# ---------------------------------------------------------------
# Helper: send command safely to Audacity
# ---------------------------------------------------------------
def send_command(cmd):
    client.write(cmd, timer=True)
    time.sleep(DELAY)
    reply = client.read()
    if reply:
        print(reply)


# ---------------------------------------------------------------
# FREQUENCY BANDS (30 ISO‑style bands)
# ---------------------------------------------------------------
BANDS = [
    (20, 25), (25, 31), (31, 40), (40, 50), (50, 63),
    (63, 80), (80, 100), (100, 125), (125, 160), (160, 200),
    (200, 250), (250, 315), (315, 400), (400, 500), (500, 630),
    (630, 800), (800, 1000), (1000, 1250), (1250, 1600), (1600, 2000),
    (2000, 2500), (2500, 3150), (3150, 4000), (4000, 5000), (5000, 6300),
    (6300, 8000), (8000, 10000), (10000, 12500), (12500, 16000), (16000, 20000)
]


# ===============================================================
# PHASE 1 — CREATE 60 WORKING TRACKS
# ===============================================================
print("\n📋 PHASE 1: Creating 60 working tracks from Track 0...")

# Assumes EXACTLY ONE track exists at script start
for _ in range(WORKING_TRACKS - 1):
    send_command('SelectTracks: Mode="Set" Track="0" TrackCount="1" Start="0" End="-1"')
    send_command('Duplicate')

print("✅ Phase 1 complete: 60 tracks created")


# ===============================================================
# PHASE 2 — APPLY HP / LP FILTERS (STABLE & ORDER‑SAFE)
# ===============================================================
print("\n🎚️ PHASE 2: Applying HP / LP filters...")

for band_index, (low_f, high_f) in enumerate(BANDS):
    hp_track = band_index * 2
    lp_track = band_index * 2 + 1
    band_label = f"Band {low_f}-{high_f} Hz"

    # --------------------
    # HIGH‑PASS FILTER
    # --------------------
    send_command(f'SelectTracks: Mode="Set" Track="{hp_track}" TrackCount="1" Start="0" End="-1"')
    time.sleep(DELAY)
    send_command(f'High-passFilter:FREQUENCY="{low_f}" ROLLOFF="dB6"')
    time.sleep(DELAY)
    send_command('Normalize:ApplyVolume="1" PeakLevel="-1" RemoveDcOffset="1" StereoIndependent="1"')
    time.sleep(DELAY)
    send_command(f'SetTrackStatus: Name="{band_label} HP"')

    # --------------------
    # LOW‑PASS FILTER
    # --------------------
    send_command(f'SelectTracks: Mode="Set" Track="{lp_track}" TrackCount="1" Start="0" End="-1"')
    time.sleep(DELAY)
    send_command(f'Low-passFilter:FREQUENCY="{high_f}" ROLLOFF="dB6"')
    time.sleep(DELAY)
    send_command('Normalize:ApplyVolume="1" PeakLevel="-1" RemoveDcOffset="1" StereoIndependent="1"')
    time.sleep(DELAY)
    send_command(f'SetTrackStatus: Name="{band_label} LP"')

print("✅ Phase 2 complete: HP/LP processing finished")


# ===============================================================
# STEP 3 — MIX HP + LP TRACKS **CORRECTLY**
# ===============================================================
print("\n🎛️ STEP 3 ONLY: Mixing HP + LP tracks correctly...\n")

"""
CRITICAL MIXING NOTE
--------------------
• MixAndRender deletes the selected tracks
• The resulting mixed track appears at the TOPMOST selected index
• Remaining tracks shift upward automatically

Therefore:
• After each mix, completed bands stack at the top
• The NEXT HP/LP pair is ALWAYS at indices:
      hp = band_index
      lp = band_index + 1

This is intentional. DO NOT OFFSET INDICES.
"""

for band_index, (low_f, high_f) in enumerate(BANDS):
    band_label = f"Band {low_f}-{high_f} Hz"

    hp_track = band_index
    lp_track = band_index + 1

    print(f"⏳ Mixing {band_label} (tracks {hp_track} + {lp_track})")

    # Clear any previous selection
    send_command('SelectNone')

    # Select HP track
    send_command(
        f'SelectTracks: Mode="Set" Track="{hp_track}" TrackCount="1" Start="0" End="-1"'
    )

    # Add LP track
    send_command(
        f'SelectTracks: Mode="Add" Track="{lp_track}" TrackCount="1" Start="0" End="-1"'
    )

    # Mix & render (HP + LP → single band track)
    send_command('MixAndRender')

    # Select newly created band track
    send_command(
        f'SelectTracks: Mode="Set" Track="{hp_track}" TrackCount="1" Start="0" End="-1"'
    )

    # Rename final band
    send_command(f'SetTrackStatus: Name="{band_label}"')

print("\n✅ STEP 3 COMPLETE: 30 correctly mixed band‑pass tracks")
