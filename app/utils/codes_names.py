import pycountry
import iso4217parse
from app.utils.actual_rates import get_actual_rates_data

CORRECT_NAMES = {
    "ADA": "Cardano (cryptocurrency)",
    "ANG": "Netherlands Antillean Guilder",
    "AVAX": "Avalanche (cryptocurrency)",
    "ARB": "Argentine Peso (offshore rate)",
    "BNB": "Binance Coin (cryptocurrency)",
    "BTC": "Bitcoin (cryptocurrency)",
    "BYR": "Belarusian Ruble (old)",
    "DAI": "DAI (stablecoin)",
    "DOT": "Polkadot (cryptocurrency)",
    "ETH": "Ethereum (cryptocurrency)",
    "LTC": "Litecoin (cryptocurrency)",
    "LTL": "Lithuanian Litas",
    "LVL": "Latvian Lats",
    "MATIC": "Polygon (cryptocurrency)",
    "MRO": "Mauritanian ouguiya (old)",
    "MRU": "Mauritanian ouguiya",
    "OP": "Optimism (cryptocurrency)",
    "SLE": "Sierra Leonean Leone",
    "SLL": "Sierra Leonean Leone (old)",
    "SOL": "Solana (cryptocurrency)",
    "STD": "Sao Tome and Principe Dobra (old)",
    "STN": "Sao Tome and Principe Dobra",
    "TRX": "TRON (cryptocurrency)",
    "USDC": "USD Coin (stablecoin)",
    "USDT": "Tether (stablecoin)",
    "VEF": "Venezuelan Bolivar (old)",
    "VES": "Venezuelan Bolivar",
    "XAF": "Central African CFA Franc",
    "XAG": "Silver (one troy ounce)",
    "XAU": "Gold (one troy ounce)",
    "XCD": "East Caribbean dollar",
    "XCG": "East Caribbean Guilder",
    "XDR": "Special drawing rights",
    "XOF": "West African CFA Franc",
    "XPD": "Palladium (one troy ounce)",
    "XPF": "CFP franc (franc Pacifique)",
    "XPT": "Platinum (one troy ounce)",
    "XRP": "Ripple (cryptocurrency)",
    "ZMK": "Zambian Kwacha (old)",
    "ZMW": "Zambian kwacha",
    "ZWG": "Zimbabwe Gold",
    "ZWL": "Zimbabwean dollar",
}


def get_flag_from_currency(currency_code):
    """
    Returns flag emoji based on ISO 4217 code.
    Crypto, stablecoins are not processed by the library
    """

    # Manual exceptions here
    crypto = [
        "ADA",
        "AVAX",
        "BNB",
        "BTC",
        "DOT",
        "ETH",
        "LTC",
        "MATIC",
        "OP",
        "SOL",
        "TRX",
        "XRP",
    ]
    stablecoin = ["DAI", "USDC", "USDT"]

    if currency_code == "EUR":
        return "🇪🇺"

    if currency_code in crypto:
        return "💻"

    if currency_code in stablecoin:
        return "💰"

    country_code = currency_code[:2]  # Works for national currencies only (USD -> US)

    try:
        country = pycountry.countries.get(alpha_2=country_code)
        if country:
            return country.flag
        else:
            return None
    except AttributeError:
        return None
    except Exception as e:
        print(f"Error getting flag for {currency_code}: {e}")
        return None


def get_currency_name(currency_code):
    """
    Returns the currency name (ISO 4217 standard).
    """
    result = iso4217parse.parse(currency_code)

    if result:
        return result[0].name


def get_codes_names() -> dict:
    """
    Returns a dictionary:
    - Keys are currency codes;
    - Values are currency names according to the ISO 4217 standard.
    """
    data = get_actual_rates_data()
    codes_list = list(data.keys())

    codes_flags = {x: get_flag_from_currency(x) for x in codes_list}
    codes_iso = [get_currency_name(code) for code in codes_list]

    full_names_map = {}

    for i, key in enumerate(codes_list):
        full_names_map[key] = f"{codes_flags[key]} {codes_iso[i]}"

    for code, name in CORRECT_NAMES.items():
        if code in full_names_map:
            emoji = full_names_map[code].split(" ")[0]
            if emoji == "None":
                full_names_map[code] = name
            else:
                full_names_map[code] = f"{emoji} {name}"

    return full_names_map
