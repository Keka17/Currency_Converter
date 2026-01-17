from fastapi import APIRouter, Depends, Query
from typing import Annotated, List

from app.exceptions.tokens import InvalidTokenTypeException
from app.jwt_auth.security import decode_jwt_token
from app.utils.codes_names import get_codes_names
from app.utils.actual_rates import get_actual_rates_data
from app.exceptions.currency import InvalidCurrencyCodeException
from app.schemas.currency import Converter


router = APIRouter(prefix="/currency", tags=["Currency"])


@router.get("/list")
async def get_currencies_list(payload: dict = Depends(decode_jwt_token)) -> dict:
    """
    Retrieves a list of available currenices.
    Only accessible with a valid Access Token in the Authorization header.
    """
    if payload.get("token_type") != "access":
        raise InvalidTokenTypeException(expected_type="access")

    full_names_map = get_codes_names()

    return {
        "message": "Available currencies for conversion",
        "currencies": full_names_map,
    }


@router.get("/actual_rates")
async def get_actual_rates(payload: dict = Depends(decode_jwt_token)):
    """
    Returns current exchange rates relative to the USD.
    Only accessible with a valid Access Token in the Authorization header
    """
    if payload.get("token_type") != "access":
        raise InvalidTokenTypeException(expected_type="access")

    rates_data = get_actual_rates_data()
    return {
        "message": "Actual currencies rates. Base currency: 💵 USD (1 USD = value [Currency])",
        "rates": rates_data,
    }


@router.get("/actual_rate")
async def get_actual_rate(
    codes: Annotated[List[str] | None, Query()] = None,
    payload: dict = Depends(decode_jwt_token),
):
    """
    Returns the current exchange rate of the specified currency/ies relative to the USD.
    Request parameter: list of currency/ies code/s.
    Only accessible with a valid Access Token in the Authorization header.
    """
    if payload.get("token_type") != "access":
        raise InvalidTokenTypeException(expected_type="access")

    rates_data = get_actual_rates_data()

    codes_list = list(rates_data.keys())

    invalid_codes = []
    for code in codes:
        if code not in codes_list:
            invalid_codes.append(code)

    if invalid_codes:
        raise InvalidCurrencyCodeException(invalid_codes=invalid_codes)

    specified_rates = {c: rates_data[c] for c in codes if c in rates_data}

    return {
        "message": f"Current {codes} to dollar exchange rate",
        "rate": specified_rates,
    }


@router.post("/converter")
async def currency_converter(
    data: Converter, payload: dict = Depends(decode_jwt_token)
):
    """
    Converts one currency to another.
    Parameters:
    code_1: name of the currency to find out the price of;
    code_2: name of the currency to find out the price of
    the first currency in;
    k: amount of the first currency.
    """

    if payload.get("token_type") != "access":
        raise InvalidTokenTypeException(expected_type="access")

    rates_data = get_actual_rates_data()

    codes_list = list(rates_data.keys())

    # lowercase letters proccessing
    code_1 = data.code_1.upper()
    code_2 = data.code_2.upper()

    k = data.k

    if code_1 not in codes_list or code_2 not in codes_list:
        raise InvalidCurrencyCodeException()

    x = rates_data[code_1]
    y = rates_data[code_2]

    ratio = y / x

    return {"message": f"{k} {code_1} - {round(k * ratio, 3):,} {code_2}"}
