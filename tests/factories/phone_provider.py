from faker.providers import BaseProvider


MODELS = [
    "Samsung Galaxy S24",
    "Samsung Galaxy S23",
    "Samsung Galaxy A54",
    "Google Pixel 8",
    "Google Pixel 7a",
    "OnePlus 12",
    "OnePlus 11",
    "Xiaomi 14",
    "Xiaomi Poco X11 Pro",
    "iPhone 15",
    "iPhone 14",
    "iPhone 13",
]


class MobileProvider(BaseProvider):
    models = MODELS

    def mobile_model(self) -> str:
        return self.random_element(self.models)
