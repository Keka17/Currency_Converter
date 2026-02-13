from fastapi import APIRouter, Depends, Query
from typing import Annotated, List

from app.utils.codes_names import get_codes_names
from app.utils.actual_rates import get_actual_rates_data
from app.exceptions.currency import (
    InvalidCurrencyCodeException,
    EmptyCurrencyCodeException,
)
from app.api.schemas.currency import Converter
from app.dependencies.dependencies import get_current_user
from app.database.models import User as UserModel


router = APIRouter(prefix="/currency", tags=["Currency"])


@router.get("/list")
async def get_currencies_list(
    current_user: UserModel = Depends(get_current_user),
) -> dict:
    """
    Retrieving a list of available currenices. \n
    Protected endpoint: a valid access token in the Authorization header required.
    """
    full_names_map = get_codes_names()
    del full_names_map["updated"]

    return {
        "message": "Available currencies for conversion",
        "currencies": full_names_map,
    }


@router.get("/actual_rates")
async def get_actual_rates(
        code: Annotated[List[str] | None, Query()] = None,
        current_user: UserModel = Depends(get_current_user)):
    """
    Retrieving current exchange rates against the US dollar. \n
    Query parameter: ISO currency code. \n
    Protected endpoint: a valid access token in the Authorization header required.
    """
    rates_data = get_actual_rates_data()

    if not code:
        return {
            "message": "Actual currencies rates. Base currency: 💵 USD (1 USD = value [Currency])",
            "rates": rates_data,
        }

    codes_list = list(rates_data.keys())

    invalid_codes = []
    for _ in code:
        if _ not in codes_list:
            invalid_codes.append(_)

    if invalid_codes:
        raise InvalidCurrencyCodeException(invalid_codes=invalid_codes)

    specified_rates = {c: rates_data[c] for c in code if c in rates_data}

    return {
        "message": f"Current {code} to USD exchange rate",
        "rate": specified_rates,
    }


@router.post("/converter")
async def currency_converter(
    data: Converter, current_user: UserModel = Depends(get_current_user)
):
    """
    Converting one currency to another. Parameters: \n
    **code_1**: name of the currency to find out the price of; \n
    **code_2**: name of the currency to find out the price of
    the first currency in; \n
    **k**: amount of the first currency.\n

    Protected endpoint: a valid access token in the Authorization header required.
    """

    rates_data = get_actual_rates_data()
    del rates_data["updated"]

    codes_list = list(rates_data.keys())

    # lowercase letters proccessing
    code_1 = data.code_1.upper()
    code_2 = data.code_2.upper()

    k = data.k
    invalid_codes = []
    codes = [code_1, code_2]

    for code in codes:
        if code not in codes_list:
            invalid_codes.append(code)

    if invalid_codes:
        raise InvalidCurrencyCodeException(invalid_codes=invalid_codes)

    x = rates_data[code_1]
    y = rates_data[code_2]

    ratio = y / x

    return {"message": f"{k} {code_1} - {round(k * ratio, 3):,} {code_2}"}
