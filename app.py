from flask import Flask, render_template, send_from_directory
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

SRP_FILE = os.getenv("SRP_FILE", "/data/servicelist.txt")
PICON_DIR = os.getenv("PICON_DIR", "/data/picons")
ICON_AUTH_CODE = os.getenv("ICON_AUTH_CODE")
HTTP_PORT = int(os.getenv("HTTP_PORT", "9986"))  # default to 9986 if not set

print(f"[INFO] Starting Picon Dashboard")
print(f"[INFO] Looking for SRP file at: {SRP_FILE}")
print(f"[INFO] Looking for Picon directory at: {PICON_DIR}")

if not os.path.exists(SRP_FILE):
    print(f"[WARNING] SRP file does not exist: {SRP_FILE}")
else:
    print(f"[OK] SRP file found.")

if not os.path.isdir(PICON_DIR):
    print(f"[WARNING] Picon directory does not exist or is not a directory: {PICON_DIR}")
else:
    print(f"[OK] Picon directory found.")
    icon_files = [f for f in os.listdir(PICON_DIR) if f.endswith(".png")]
    print(f"[INFO] Found {len(icon_files)} icon files in picon directory.")


def parse_srp_file():
    channels = []

    if not os.path.exists(SRP_FILE):
        print(f"[ERROR] SRP file not found during parse.")
        return channels

    try:
        with open(SRP_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

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


@app.route("/")
def index():
    channels = parse_srp_file()
    return render_template("index.html", channels=channels)


@app.route("/icons/<filename>")
def icon_file(filename):
    return send_from_directory(PICON_DIR, filename)


@app.route("/missing-report")
def missing_report():
    channels = parse_srp_file()
    missing = [ch for ch in channels if ch["status"] == "Missing"]

    report_lines = [
        f"{ch['srp']}={ch['matched'] if ch['matched'] else ch['name'].strip().lower().replace(' ', '').replace('+', 'plus')}"
        for ch in missing
    ]
    report = "\n".join(report_lines)

    return f"<pre>{report}</pre>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HTTP_PORT)
