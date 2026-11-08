"""Fetch an hourly air-quality forecast and suggest lower-PM2.5 hours."""
import argparse
import csv
import requests

URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--hours", type=int, default=24)
    p.add_argument("--output", default="air_quality.csv")
    args = p.parse_args()
    hours = max(1, min(args.hours, 168))
    response = requests.get(URL, params={"latitude": args.lat, "longitude": args.lon,
        "hourly": "pm2_5,pm10,ozone", "forecast_days": 7, "timezone": "auto"}, timeout=25)
    response.raise_for_status()
    data = response.json().get("hourly", {})
    rows = [{"time": t, "pm2_5": pm25, "pm10": pm10, "ozone": ozone}
            for t, pm25, pm10, ozone in zip(data.get("time", [])[:hours],
                data.get("pm2_5", [])[:hours], data.get("pm10", [])[:hours], data.get("ozone", [])[:hours])]
    if not rows:
        raise SystemExit("No hourly forecast returned")
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["time", "pm2_5", "pm10", "ozone"])
        writer.writeheader(); writer.writerows(rows)
    ranked = sorted((r for r in rows if r["pm2_5"] is not None), key=lambda r: r["pm2_5"])
    print(f"Saved {len(rows)} hourly rows to {args.output}")
    print("Lowest forecast PM2.5 hours:")
    for row in ranked[:min(5, len(ranked))]:
        print(f"  {row['time']}: {row['pm2_5']} μg/m³ (PM10 {row['pm10']}, ozone {row['ozone']})")
    print("Source: Open-Meteo Air Quality API; forecast/model data, not a local sensor reading.")


if __name__ == "__main__":
    main()
