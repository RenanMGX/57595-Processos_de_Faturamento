class LoginError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class UrlError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class CobrancaError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)