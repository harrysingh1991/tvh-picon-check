from flask import Flask, render_template, send_from_directory, request
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Use environment variables if set, otherwise use defaults (local-friendly)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRP_FILE = os.getenv("SRP_FILE", os.path.join(BASE_DIR, "servicelist.txt"))
PICON_DIR = os.getenv("PICON_DIR", os.path.join(BASE_DIR, "picons"))
HTTP_PORT = int(os.getenv("HTTP_PORT", 9986))
ICON_AUTH_CODE = os.getenv("ICON_AUTH_CODE")

# Print initial configuration information
print(f"[INFO] Starting Picon Dashboard")
print(f"[INFO] Icon Auth Code: {ICON_AUTH_CODE}")

# Check if picon directory exists and is a directory
# If not, print a warning
# Prnts how many icons are found in the picon directory
if os.path.exists(PICON_DIR) and os.path.isdir(PICON_DIR):
    icon_files = [f for f in os.listdir(PICON_DIR) if f.lower().endswith('.png')]
    print(f"[INFO] Found {len(icon_files)} icon(s) in picon directory.")
else:
    print(f"[WARNING] Picon directory not found or is not a directory: {PICON_DIR}")

# Check if SRP file exists
if os.path.exists(SRP_FILE):
    print(f"[INFO] SRP file found: {SRP_FILE}")
else:
    print(f"[WARNING] SRP file not found: {SRP_FILE}")

# Function to parse the SRP file and extract channel information
def parse_srp_file():
    channels = []
    # Check if SRP file exists
    if not os.path.exists(SRP_FILE):
        print(f"[ERROR] SRP file not found during parse.")
        return channels
    # Attempt to read the SRP file
    try:
        with open(SRP_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Parse the line into components
                try:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) != 3:
                        continue

                    service_ref, channel_name, srp_line = parts
                    srp_part, matched_picon = srp_line.split("=")
                    matched_picon = matched_picon if matched_picon != "--------" else None

                    icon_filename = f"{service_ref}.png"
                    icon_path = os.path.join(PICON_DIR, icon_filename)
                    icon_exists = os.path.isfile(icon_path)

                    icon_url = f"/icons/{icon_filename}"
                    if ICON_AUTH_CODE:
                        icon_url += f"?auth={ICON_AUTH_CODE}"

                    channels.append({
                        "name": channel_name,
                        "service_ref": service_ref,
                        "srp": srp_part,
                        "matched": matched_picon,
                        "icon": icon_filename if icon_exists else None,
                        "icon_url": icon_url if icon_exists else None,
                        "status": "OK" if icon_exists else "Missing"
                    })

                except Exception as e:
                    print(f"[ERROR] Failed to parse line: {line}\n{e}")
                    continue

        print(f"[INFO] Parsed {len(channels)} channels from SRP file.")

    except Exception as e:
        print(f"[ERROR] Failed to open SRP file: {e}")

    return channels

# Route to serve the main dashboard page
@app.route("/")
def index():
    channels = parse_srp_file()
    return render_template("index.html", channels=channels)

# Route to serve individual icon files
@app.route("/icons/<filename>")
def icon_file(filename):
    return send_from_directory(PICON_DIR, filename)

# Route to serve the missing report
@app.route("/missing-report", methods=["GET", "POST"])
def missing_report():
    channels = parse_srp_file()
    excluded = []
    if request.method == "POST":
        data = request.get_json(silent=True)
        if data and "excluded" in data:
            excluded = set(data["excluded"])
    missing = [ch for ch in channels if ch["status"] == "Missing" and ch["service_ref"] not in excluded]

    print("Excluded service_refs:", excluded)  # Debugging line to print excluded service_refs

    report_lines = [
        f"{ch['srp']}={ch['matched'] if ch['matched'] else ch['name'].strip().lower().replace(' ', '').replace('+', 'plus')}"
        for ch in missing
    ]
    report = "\n".join(report_lines)

    return f"<pre>{report}</pre>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HTTP_PORT)
