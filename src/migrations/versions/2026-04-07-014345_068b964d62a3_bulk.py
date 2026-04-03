"""bulk add templates

Revision ID: 068b964d62a3
Revises: 8dc22fe720ed
Creation Date: 2026-04-06 00:51:45.323259
"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "068b964d62a3"
down_revision: Union[str, Sequence[str], None] = "8dc22fe720ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_DESKTOP = 1
_MOBILE = 2

_table = sa.table(
    "device_templates",
    sa.column("name", sa.String),
    sa.column("device_type", sa.SmallInteger),
    sa.column("width", sa.SmallInteger),
    sa.column("height", sa.SmallInteger),
    sa.column("user_agent", sa.String),
)
users_table = sa.table(
    "users",
    sa.column("email", sa.String),
    sa.column("first_name", sa.String),
    sa.column("last_name", sa.String),
    sa.column("password", sa.String),
)


def upgrade() -> None:
    op.bulk_insert(
        users_table,
        [
            {
                "email": "user@example.com",
                "first_name": "User",
                "last_name": "Sample",
                "password": "$argon2id$v=19$m=65536,t=3,p=4$A2CsdU6J8d67t9ZaC2EMoQ$SFBsGgDTKTK4j4VhzEVp0b4TRV00a1pjfrSrnByp1Ec",  # admin
            },
        ],
    )
    op.bulk_insert(
        _table,
        [
            # --- Mobile ---
            {
                "name": "Xiaomi Poco X5 Pro",
                "device_type": _MOBILE,
                "width": 393,
                "height": 852,
                "user_agent": "Mozilla/5.0 (Linux; Android 13; 2201116PG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.99 Mobile Safari/537.36",
            },
            {
                "name": "Samsung Galaxy S23",
                "device_type": _MOBILE,
                "width": 360,
                "height": 780,
                "user_agent": "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.99 Mobile Safari/537.36",
            },
            {
                "name": "iPhone 15",
                "device_type": _MOBILE,
                "width": 393,
                "height": 852,
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            },
            # --- Desktop 1080p ---
            {
                "name": "Firefox 1080p",
                "device_type": _DESKTOP,
                "width": 1920,
                "height": 1080,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            },
            {
                "name": "Brave 1080p",
                "device_type": _DESKTOP,
                "width": 1920,
                "height": 1080,
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36",
            },
            {
                "name": "Chromium 1080p",
                "device_type": _DESKTOP,
                "width": 1920,
                "height": 1080,
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chromium/123.0.6312.86 Chrome/123.0.6312.86 Safari/537.36",
            },
            {
                "name": "Chrome 1080p",
                "device_type": _DESKTOP,
                "width": 1920,
                "height": 1080,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36",
            },
            {
                "name": "Edge 1080p",
                "device_type": _DESKTOP,
                "width": 1920,
                "height": 1080,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36 Edg/123.0.2420.65",
            },
            {
                "name": "IE 1080p",
                "device_type": _DESKTOP,
                "width": 1920,
                "height": 1080,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            },
            # --- Desktop 1440p ---
            {
                "name": "Firefox 1440p",
                "device_type": _DESKTOP,
                "width": 2560,
                "height": 1440,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            },
            {
                "name": "Brave 1440p",
                "device_type": _DESKTOP,
                "width": 2560,
                "height": 1440,
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36",
            },
            {
                "name": "Chromium 1440p",
                "device_type": _DESKTOP,
                "width": 2560,
                "height": 1440,
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chromium/123.0.6312.86 Chrome/123.0.6312.86 Safari/537.36",
            },
            {
                "name": "Chrome 1440p",
                "device_type": _DESKTOP,
                "width": 2560,
                "height": 1440,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36",
            },
            {
                "name": "Edge 1440p",
                "device_type": _DESKTOP,
                "width": 2560,
                "height": 1440,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36 Edg/123.0.2420.65",
            },
            {
                "name": "IE 1440p",
                "device_type": _DESKTOP,
                "width": 2560,
                "height": 1440,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            },
            # --- Desktop 4K ---
            {
                "name": "Firefox 4K",
                "device_type": _DESKTOP,
                "width": 3840,
                "height": 2160,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            },
            {
                "name": "Brave 4K",
                "device_type": _DESKTOP,
                "width": 3840,
                "height": 2160,
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36",
            },
            {
                "name": "Chromium 4K",
                "device_type": _DESKTOP,
                "width": 3840,
                "height": 2160,
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chromium/123.0.6312.86 Chrome/123.0.6312.86 Safari/537.36",
            },
            {
                "name": "Chrome 4K",
                "device_type": _DESKTOP,
                "width": 3840,
                "height": 2160,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36",
            },
            {
                "name": "Edge 4K",
                "device_type": _DESKTOP,
                "width": 3840,
                "height": 2160,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36 Edg/123.0.2420.65",
            },
            {
                "name": "IE 4K",
                "device_type": _DESKTOP,
                "width": 3840,
                "height": 2160,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            },
        ],
    )


def downgrade() -> None:
    pass  # seed data is not worth reversing
