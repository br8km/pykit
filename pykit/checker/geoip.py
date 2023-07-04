#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""GeoIP Checker."""


from dataclasses import dataclass


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
