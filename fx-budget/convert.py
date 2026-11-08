"""Пересчитываем сумму по справочному курсу ЦБ на выбранную дату."""
import argparse
import xml.etree.ElementTree as ET
from datetime import date
import requests

URL = "https://www.cbr.ru/scripts/XML_daily.asp"


def rates_for(day):
    response = requests.get(URL, params={"date_req": day.strftime("%d/%m/%Y")}, timeout=20)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    rates = {"RUB": 1.0}
    for item in root.findall("Valute"):
        code = item.findtext("CharCode")
        nominal = float(item.findtext("Nominal").replace(",", "."))
        value = float(item.findtext("Value").replace(",", "."))
        rates[code] = value / nominal  # В XML сумма дана за nominal единиц валюты.
    return rates


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--date", required=True, help="YYYY-MM-DD")
    p.add_argument("--base", required=True, help="ISO currency code, e.g. USD")
    p.add_argument("--amount", required=True, type=float)
    p.add_argument("--target", required=True, help="ISO currency code, e.g. RUB")
    args = p.parse_args()
    day = date.fromisoformat(args.date)
    rates = rates_for(day)
    base, target = args.base.upper(), args.target.upper()
    if base not in rates or target not in rates:
        raise SystemExit(f"Currency not found for {day}; available codes: {', '.join(sorted(rates))}")
    result = args.amount * rates[base] / rates[target]
    print(f"{args.amount:.2f} {base} = {result:.2f} {target} (CBR reference rates, {day})")


if __name__ == "__main__":
    main()
