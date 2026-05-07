import httpx
from datetime import date

_cache: dict = {"rates": {}, "date": None}


def get_rates() -> dict:
    today = date.today()

    if _cache["date"] == today and _cache["rates"]:
        return _cache["rates"]

    try:
        response = httpx.get(
            "https://api.nbrb.by/exrates/rates",
            params={"periodicity": 0},
            timeout=5.0
        )
        data = response.json()

        rates = {"BYR": 1.0, "BYN": 1.0}
        for item in data:
            currency = item["Cur_Abbreviation"]
            rate = item["Cur_OfficialRate"] / item["Cur_Scale"]
            rates[currency] = rate
            if currency == "RUB":
                rates["RUR"] = rate

        _cache["rates"] = rates
        _cache["date"] = today
        return rates

    except Exception as e:
        print(f"[CURRENCY] Ошибка загрузки курсов: {e}")
        return {
            "BYR": 1.0,
            "BYN": 1.0,
            "RUR": 0.034,
            "RUB": 0.034,
            "USD": 3.25,
            "EUR": 3.55,
            "KZT": 0.0067,
            "UAH": 0.078,
            "GEL": 1.18,
            "AMD": 0.0083,
            "UZS": 0.00025,
        }


def convert_to_byn(amount, currency: str):
    if amount is None or currency is None:
        return None
    rates = get_rates()
    rate = rates.get(currency, 1.0)
    return round(amount * rate)