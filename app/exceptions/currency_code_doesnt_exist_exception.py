class CurrencyCodeDoesntExistException(Exception):
    """Raised when currency code does not exist

    Attributes:
        currency_code -- currency code that does not exist
        message -- explanation of the error
    """

    def __init__(self, currency_code, message="Currency {code} does not exist"):
        self.message = message.format(code=currency_code)
        self.currency_code = currency_code
        super().__init__(self.message)
