"""Carvana poller stub — awaiting partner API credentials.

Implement fully once CARVANA_API_KEY is available from api-developer.carvana.com.
"""
import structlog

from app.config import settings
from scraper.base import BaseSource, RawListing

log = structlog.get_logger()


class CarvanaPoller(BaseSource):
    name = "carvana"

    async def fetch(self) -> list[RawListing]:
        if not settings.carvana_api_key:
            log.debug("carvana_key_missing", msg="Set CARVANA_API_KEY to enable Carvana listings")
            return []
        # TODO: implement when credentials are obtained
        log.warning("carvana_not_implemented")
        return []
