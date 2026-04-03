from faker.providers import BaseProvider
from faker.proxy import Faker

from divine.devices.interface.schemas import WindowSize

from tests.factories.phone_provider import MobileProvider


DESKTOP_SIZES = [
    (1920, 1080),
    (1440, 900),
    (1366, 768),
    (1280, 800),
    (2560, 1440),
    (3840, 2160),
]

MOBILE_SIZES = [
    (390, 844),  # iPhone 14
    (375, 812),  # iPhone X/11
    (414, 896),  # iPhone 11 Pro Max
    (360, 780),  # Samsung Galaxy S
    (412, 915),  # Pixel 6
    (393, 851),  # Pixel 7
]


class SizeProvider(BaseProvider):
    def desktop_window(self) -> WindowSize:
        width, height = self.random_element(DESKTOP_SIZES)
        return WindowSize(width=width, height=height)

    def mobile_window(self) -> WindowSize:
        width, height = self.random_element(MOBILE_SIZES)
        return WindowSize(width=width, height=height)

    def window_size(self) -> WindowSize:
        sizes = DESKTOP_SIZES + MOBILE_SIZES
        width, height = self.random_element(sizes)
        return WindowSize(width=width, height=height)


fake = Faker()
fake.add_provider(SizeProvider)
fake.add_provider(MobileProvider)
