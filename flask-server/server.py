from flask import Flask, jsonify,send_file
from flask_cors import CORS
import matplotlib
matplotlib.use('Agg')
import subprocess
import re
import threading
import time
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.animation import FuncAnimation
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

class APTracker():
    def __init__(self):
        self.APs = []

    def fetch_APs(self):
        while True:
            try:
                # Run the nmcli command to fetch Wi-Fi access points
                result = subprocess.run("nmcli dev wifi", shell=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
                # Decode the output
                out = result.stdout.decode("utf-8", errors="ignore")
                l1 = out.split("\n")

                if len(l1) > 1:
                    propslength = dict()
                    props = l1[0]
                    m = re.findall("(IN-USE *)(BSSID *)(SSID *)(MODE *)(CHAN *)(RATE *)(SIGNAL *)(BARS *)(SECURITY *)",
                                   props, re.DOTALL)

                    if m:
                        for prop in m[0]:
                            propslength[prop.strip()] = len(prop)

                        self.APs = []  # Clear previous results
                        for ap in l1[1:]:
                            if ap:
                                AP = dict()
                                for prop, length in propslength.items():
                                    AP[prop] = ap[:length].strip()
                                    ap = ap[length:]
                                self.APs.append(AP)

                    else:
                        print("No matches found in the properties header.")  # Debug info

                else:
                    print("No access points found.")  # Debug info

            except Exception as e:
                print(f"Error fetching APs: {e}")  # Handle and log exceptions
            time.sleep(1)  # Wait for 1 second before fetching again

apt = APTracker()
def background_fetch():
    apt.fetch_APs()

threading.Thread(target=background_fetch, daemon=True).start()
def current_wifi_signal():
    # Run the iwconfig command to get Wi-Fi details
    result1 = subprocess.run("iwconfig", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out1 = result1.stdout.decode("utf-8", errors="ignore")

    # Extract ESSID from iwconfig output
    m1 = re.findall(r'ESSID:"(.*?)"', out1, re.DOTALL)
    if len(m1) == 1:
        ESSID = m1[0]

        # Run nmcli to get signal strength of the connected Wi-Fi
        result2 = subprocess.run("nmcli dev wifi | grep '*'", shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
        out2 = result2.stdout.decode("utf-8", errors="ignore")

        # Extract BSSID, Mode, Channel, Rate, Signal, and Security
        m2 = re.findall(
            r'\* *(\S+) *{} *(\S+) *(\d+) *([\d.]+ [a-zA-Z/]+) *(\d+) *[^ ]* *(.*)'.format(re.escape(ESSID)), out2)
        if m2:
            bssid, mode, channel, rate, signal_power, security = m2[0]
            security = security.strip()
            return int(signal_power), ESSID

    # If not connected to any Wi-Fi network
    return 0, 'Not connected to any access point'

x_vals = []
y_vals = []

@app.route('/wifi-signal-graph')
def wifi_signal_graph():
    signal, ESSID = current_wifi_signal()
    x_vals.append(datetime.now())
    y_vals.append(signal)

    # Create the plot
    plt.figure()
    plt.plot(x_vals[-20:], y_vals[-20:], marker='o')
    plt.xlabel('Time')
    plt.ylabel('Signal Strength')
    plt.title(ESSID)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to a BytesIO object and return it as an image
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    plt.close()

    return send_file(img_bytes, mimetype='image/png')
@app.route("/PickYourWifi")
def PickYourWifi():
    return jsonify(apt.APs)

if __name__ == "__main__":
    app.run(debug=True)  # Corrected line
