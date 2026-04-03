import pycountry


def validate_numeric_country_code(value: int | None) -> int | None:
    if value is None:
        return value
    if not pycountry.countries.get(numeric=str(value).zfill(3)):
        raise ValueError(f"Invalid numeric country code: {value}")
    return value
