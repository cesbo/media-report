#!/usr/bin/env python3

import sys
import json
import subprocess
from threading import Timer
from matplotlib import pyplot as plt

def run_ffprobe(filename):
    # Run ffprobe
    proc = subprocess.Popen(
        [
            "ffprobe",
            "-v", "quiet",
            "-show_frames",
            "-select_streams", "v",
            "-print_format", "json",
            filename,
        ],
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT
    )

    # Kill ffprobe if it runs for more than 30 seconds
    timer = Timer(30, proc.kill)
    try:
        timer.start()
        stdout = proc.communicate()
    finally:
        timer.cancel()

    return json.loads(stdout[0])

if __name__ == "__main__":
    # Print usage if no filename is given
    if len(sys.argv) < 2:
        print("Usage: analyze.py <filename>")
        sys.exit(1)
    # Get first argument
    filename = sys.argv[1]
    # Run ffprobe
    data = run_ffprobe(filename)

    # Get frames from data
    frames = data["frames"]
    pict_types = [item["pict_type"] for item in frames]
    pkt_sizes = [int(item["pkt_size"]) for item in frames]
    pkt_duration_times = [float(item["pkt_duration_time"]) for item in frames]
    chart_data = [round(pkt_size * 8 / pkt_duration_time / 1000, 2) for pkt_size, pkt_duration_time in zip(pkt_sizes, pkt_duration_times)]

    colors = {'I': 'red', 'P': 'green', 'B': 'blue'}

    handles = []
    for pict_type in set(pict_types):
        handle = plt.scatter([], [], color = colors[pict_type], label = pict_type)
        handles.append(handle)

    plt.figure(figsize = (16, 8))

    for i, (pict_type, y) in enumerate(zip(pict_types, chart_data)):
        if pict_type == 'I':
            plt.bar(i, y, color = colors[pict_type], width = 4)
        else:
            plt.scatter(i, y, color = colors[pict_type], s = 0.5)

    plt.grid(axis = 'y', linestyle = '-', linewidth = 0.5, color = 'gray', alpha = 0.5)
    plt.legend(handles = handles)
    plt.xlabel("Frame")
    plt.ylabel("Packet Bitrate (kbps)")
    plt.savefig('frames.png', dpi = 300)
