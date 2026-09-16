# icalendar_compatibility
# Copyright (C) 2025  Nicco Kunzmann
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see
# <https://www.gnu.org/licenses/>.
"""Event location computation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

from icalendar import Event, vGeo, vText

GEO_MATCH = re.compile(r"^(?P<lat>[-+]?\d*\.?\d+)\s*,\s*(?P<lon>[-+]?\d*\.?\d+)$")

URL_REGEX = re.compile(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
)  # see https://stackoverflow.com/a/3809435/1320237


@dataclass
class LocationSpec:
    """Specification for event locations.

    Attributes:
        zoom : int
            Zoom level for geo_url and search_url
        geo_url : str
            A url template when the geo location is given.
            At least {lat} and {lon} are required.
        text_url : str
            A url template when the location is given as text.
            At leat {location} is required.

    Examples:

        >>> from icalendar_compatibility import LocationSpec
        >>> spec = LocationSpec.for_openstreetmap_org()

    """

    geo_url: str
    text_url: str
    zoom: int = 16

    @classmethod
    def for_openstreetmap_org(cls, **kw) -> LocationSpec:
        """Spec for https://openstreetmap.org"""
        return cls(
            geo_url="https://www.openstreetmap.org/#map={zoom}/{lat}/{lon}",
            text_url="https://www.openstreetmap.org/search?query={location}",
            **kw,
        )

    @classmethod
    def for_bing_com(cls, **kw) -> LocationSpec:
        """Spec for https://www.bing.com/maps"""
        return cls(
            geo_url="https://www.bing.com/maps?brdr=1&cp={lat}%7E{lon}&lvl={zoom}",
            text_url="https://www.bing.com/maps?q={location}&lvl={zoom}",
            **kw,
        )

    @classmethod
    def for_google_com(cls, **kw) -> LocationSpec:
        """Spec for https://www.google.com/maps"""
        return cls(
            geo_url="https://www.google.com/maps/@{lat},{lon},{zoom}z",
            text_url="https://www.google.com/maps/search/{location}",
            **kw,
        )

    @classmethod
    def for_google_co_uk(cls, **kw) -> LocationSpec:
        """Spec for https://www.google.co.uk/maps"""
        return cls(
            geo_url="https://www.google.co.uk/maps/@{lat},{lon},{zoom}z",
            text_url="https://www.google.co.uk/maps/search/{location}",
            **kw,
        )

    @classmethod
    def for_no_url(cls) -> LocationSpec:
        """Return a spec that creates empty URLs always."""
        return cls(geo_url="", text_url="")

    @classmethod
    def for_geo_url(cls) -> LocationSpec:
        """Spec for the geo:{lat},{lon} links.

        :rfc:`5870`::

            geo:48.2010,16.3695
        """
        return cls(geo_url="geo:{lat},{lon}", text_url="")

    def get_geo_url(self, *, lat: float, lon: float, zoom: Optional[int] = None) -> str:
        """Get the url for a geo location."""
        return self.geo_url.format(
            lat=lat, lon=lon, zoom=self.zoom if zoom is None else zoom
        )

    def get_text_url(self, location: str, zoom: Optional[int] = None) -> str:
        """Get the url for a text location."""
        return self.text_url.format(
            location=self.quote(location), zoom=self.zoom if zoom is None else zoom
        )

    @staticmethod
    def quote(string: str):
        """Quote a string to fit into any place in a URL.

        We also replace the . as .. has a special meaning.
        """
        return quote(string, safe="").replace(".", "%2e")


class Location:
    """The location of an event.

    Attributes:
        text : str
            The text of the location.
        url : str
            The url of the event location.
            This considers geo information, text and more.

    Examples:

        >>> from icalendar_compatibility import Location, LocationSpec
        >>> from icalendar import Event
        >>> event_string = '''
        ... BEGIN:VEVENT
        ... SUMMARY:Event in Mountain View with Geo link
        ... DTSTART:20250115T150000Z
        ... LOCATION:Mountain View, Santa Clara County, Kalifornien, Vereinigte Staaten von Amerika
        ... GEO:37.386013;-122.082932
        ... END:VEVENT
        ... '''
        >>> event = Event.from_ical(event_string)
        >>> location = Location(event, LocationSpec.for_bing_com())
        >>> print(location.text)
        Mountain View, Santa Clara County, Kalifornien, Vereinigte Staaten von Amerika
        >>> print(location.url)
        https://www.bing.com/maps?brdr=1&cp=37.386013%7E-122.082932&lvl=16


    """

    def __init__(self, event: Event, spec: Optional[LocationSpec] = None):
        """Create a new location adapter.

        Args:
            event : Event
                The event to adapt.
            spec : LocationSpec
                The specification to use.
                By default we use OpenStreetMap.
        """
        self._event = event
        self._spec = LocationSpec.for_openstreetmap_org() if spec is None else spec

    @property
    def raw_text(self) -> vText:
        r"""The raw event text of the location.

        :rfc:`5545`::

            LOCATION:Conference Room - F123\, Bldg. 002
        """
        return self._event.get("LOCATION", vText(""))

    @property
    def raw_altrep(self) -> str:
        r"""The alternative representation according to RFC5545.

        :rfc:`5545`::

            LOCATION;ALTREP="http://xyzcorp.com/conf-rooms/f123.vcf":
            Conference Room - F123\, Bldg. 002
        """
        return self.raw_text.params.get("ALTREP", "")

    @property
    def raw_geo(self) -> Optional[vGeo]:
        """The raw geo location.

        :rfc:`5545`::

            GEO:37.386013;-122.082932
        """
        geo = self._event.get("GEO")
        if isinstance(geo, vGeo):
            return geo
        match = GEO_MATCH.match(self.raw_text)
        if match:
            return vGeo((float(match.group("lat")), float(match.group("lon"))))
        return None

    @property
    def geo(self) -> Optional[vGeo]:
        """The geo location from latitude and longitude."""
        lat = self.lat
        lon = self.lon
        if lon is not None and lat is not None:
            return vGeo((lat, lon))
        return None

    @property
    def text(self) -> str:
        """The location text.

        Returns: str
            The text or an empty string if we have no location data.
        """
        return str(self.raw_text)

    @property
    def url(self) -> str:
        """The location url.

        Returns: str
            The url or an empty string if we have no location data.
        """
        if self.raw_altrep:
            return self.raw_altrep
        lon, lat = self.lon, self.lat
        if lon is None or lat is None:
            text = self.text
            if text == "":
                return ""
            for url in URL_REGEX.finditer(text):
                return url.group()
            return self._spec.get_text_url(location=self.text, zoom=self.zoom)
        return self._spec.get_geo_url(lat=lat, lon=lon, zoom=self.zoom)

    @property
    def lon(self) -> Optional[float]:
        """The longitude of the location.

        Returns: float
            The longitude or None if we have no location data.
        """
        return self.raw_geo.longitude if self.raw_geo else None

    @property
    def lat(self) -> Optional[float]:
        """The latitude of the location.

        Returns: float
            The longitude or None if we have no location data.
        """
        return self.raw_geo.latitude if self.raw_geo else None

    @property
    def zoom(self) -> int:
        """The zoom level of the location.

        Returns: int
            The zoom level of the location.
        """
        return self._spec.zoom

    @property
    def spec(self) -> LocationSpec:
        """The location spec we use."""
        return self._spec

    @spec.setter
    def spec(self, new_spec: LocationSpec):
        """Set the location spec."""
        self._spec = new_spec


__all__ = ["Location", "LocationSpec"]
