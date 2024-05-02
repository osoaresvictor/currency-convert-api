class InvalidCurrencyException(Exception):
    """Exception raised for errors in currency like invalid code or invalid value.

    Attributes:
    currency_code -- input currency code which caused the error
    currency_rate -- input currency rate which caused the error
    message -- explanation of the error
    """

    def __init__(
            self,
            currency_code: str,
            currency_rate: float | None = None,
            message="Currency code {code} is not valid"
    ):
        self.code = currency_code
        self.rate = currency_rate
        self.message = message.format(code=currency_code)
        super().__init__(self.message)
