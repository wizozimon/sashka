"""Собираем открытые вакансии HeadHunter в CSV."""
import argparse
import csv
import os
import requests

API = "https://api.hh.ru/vacancies"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", default="стажер аналитик")
    parser.add_argument("--area", default="1", help="HH area ID; 1 is Moscow")
    parser.add_argument("--pages", type=int, default=2)
    parser.add_argument("--output", default="vacancies.csv")
    args = parser.parse_args()
    agent = os.getenv("HH_USER_AGENT", "StudentRadar/1.0 student@example.com")
    session = requests.Session()
    session.headers.update({"User-Agent": agent})
    records = []
    for page in range(max(1, min(args.pages, 20))):
        response = session.get(API, params={"text": args.text, "area": args.area,
                                            "page": page, "per_page": 50,
                                            "order_by": "publication_time"}, timeout=25)
        response.raise_for_status()
        payload = response.json()
        for v in payload.get("items", []):
            salary = v.get("salary") or {}
            records.append({"id": v.get("id"), "name": v.get("name"),
                "employer": (v.get("employer") or {}).get("name"),
                "area": (v.get("area") or {}).get("name"),
                "published_at": v.get("published_at"),
                "salary_from": salary.get("from"), "salary_to": salary.get("to"),
                "currency": salary.get("currency"), "gross": salary.get("gross"),
                "url": v.get("alternate_url")})
        if page + 1 >= payload.get("pages", 0):
            break
    fields = ["id", "name", "employer", "area", "published_at", "salary_from", "salary_to", "currency", "gross", "url"]
    with open(args.output, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(records)
    paid = [r for r in records if r["salary_from"] is not None or r["salary_to"] is not None]
    print(f"Saved {len(records)} vacancies ({len(paid)} with salary information) to {args.output}")
    print("Salary fields are optional and may use different currencies; normalize before comparing.")


if __name__ == "__main__":
    main()
