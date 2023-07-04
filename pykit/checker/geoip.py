#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""GeoIP Checker."""

from pathlib import Path
from dataclasses import dataclass

from geoip2.database import Reader

from ..base.timer import utc_offset
from ..base.schema import Address


@dataclass
class IP:
    """IP."""

    addr: str
    decimal: int
    hostname: str


@dataclass
class DNS:
    """DNS."""

    ip_addr: str
    ip_geo: str


@dataclass
class ASN:
    """ASN."""

    name: str
    org: str


@dataclass
class ISP:
    """ISP."""

    name: str



@dataclass
class Currency:
    """Currency."""
    
    name: str
    code: str
    symbol: str



@dataclass
class TimeZone:
    """Time Zone."""

    name: str
    offset: int

    current_time: str
    current_time_unix: int


@dataclass
class Continent:
    """Continent."""

    name: str
    code: str


@dataclass
class Country:
    """Country."""

    name: str
    code: str

    calling_code: str
    capital: str
    tld: str   # Top Level Domain


@dataclass
class Region:
    """Region."""

    name: str
    code: str


@dataclass
class City:
    """City."""

    name: str
    code: str


@dataclass
class Location:
    """Location Coordinate."""

    latitude: float
    longitude: float


@dataclass
class Privacy:
    """Privacy."""

    hosting: bool
    proxy: bool
    tor: bool
    relay: bool
    vpn: bool

    service: str


@dataclass
class Abuse:
    """Abuse."""

    name: str
    email: str
    country_code: str
    address: str


@dataclass
class GeoIPAddress:
    """Geo IP Address."""

    ip: IP

    continent: Continent
    country: Country

    region: Region
    city: City

    currency: Currency
    location: Location
    timezone: TimeZone
    asn: ASN
    isp: ISP
    dns: DNS

    privacy: Privacy

    zip_code: str


class GeoIPChecker:
    """Geo IP Address Checker."""


    def get_info(self, ip_addr: str) -> GeoIPAddress:
        """Get ip address information."""
        raise NotImplementedError


    @staticmethod
    def maxmind_geoip(ipaddr: str, file_geo: Path) -> Address:
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