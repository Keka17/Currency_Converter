import pycountry
import iso4217parse
from app.utils.actual_rates import get_actual_rates_data

CORRECT_NAMES = {
    "ANG": "Netherlands Antillean Guilder",
    "BCH": "Bitcoin Cash (cryptocurrency)",
    "BTC": "Bitcoin (cryptocurrency)",
    "BTG": "Bitcoin Gold",
    "DASH": "Dash (cryptocurrency)",
    "EOS": "Eos (cryptocurrency)",
    "ETH": "Ethereum (cryptocurrency)",
    "LTC": "Litecoin (cryptocurrency)",
    "XAF": "Central African CFA franc",
    "XAG": "Silver (one troy ounce)",
    "XAU": "Gold (one troy ounce)",
    "XCD": "East Caribbean dollar",
    "XLM": "Stellar Lumens (cryptocurrency)",
    "XOF": "West African CFA Franc",
    "XRP": "Ripple (cryptocurrency)",
}


def get_flag_from_currency(currency_code):
    """
    Returns flag emoji based on ISO 4217 code.
    """

    # Manual exceptions
    crypto = ["BCH", "BTC", "DASH", "EOS", "ETH", "LTC", "XLM", "XRP"]

    if currency_code == "EUR":
        return "🇪🇺"

    if currency_code in crypto:
        return "💻"

    country_code = currency_code[:2]  # Works for national currencies only (USD -> US)

    try:
        country = pycountry.countries.get(alpha_2=country_code)
        if country:
            return country.flag
        else:
            return "📂"
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

    return "Undefined"


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
