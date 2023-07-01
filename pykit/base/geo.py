"""
    GeoIP Address Data Extracting
"""

from pathlib import Path

from geoip2.database import Reader

from ..base.timer import utc_offset
from ..base.structure import Address


__all__ = (
    "geoip",
    "Address",
)


def geoip(ipaddr: str, file_geo: Path) -> Address:
    """maxmind geoip2 database connection for ip address parser"""
    res = Reader(str(file_geo)).city(ipaddr)
    country = res.country.iso_code
    state = res.subdivisions.most_specific.name
    city = res.city.name
    postal = res.postal.code
    time_zone = res.location.time_zone
    offset = utc_offset(time_zone) if time_zone else 0
    latitude = res.location.latitude
    longitude = res.location.longitude
    coordinate = (
        latitude or 0.0,
        longitude or 0.0,
    )
    return Address(
        ipaddr=ipaddr,
        country=country or "",
        state=state or "",
        city=city or "",
        postal=postal or "",
        coordinate=coordinate,
        time_zone=time_zone or "",
        street="",
        utc_offset=offset,
    )