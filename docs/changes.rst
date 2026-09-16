Versions and Changes
====================

v0.1.5
------

- Fix compatibility with icalendar 7 and ``vGeo`` by @nightcityblade. `Issue 5 <https://github.com/pycalendar/icalendar_compatibility/issues/5>`_.
- Update development documentation by @nightcityblade.

v0.1.4
------

- Add :func:`icalendar_compatibility.LocationSpec.for_geo_url` for ``geo:`` links.

v0.1.3
------

- Add :attr:`icalendar_compatibility.Location.geo` to access the geo location easily.

v0.1.2
------

- Improve documentation
- Add Google Maps example

v0.1.1
------

- Add :func:`icalendar_compatibility.LocationSpec.quote`
- Make sure location data is properly escaped when put into a URL.

v0.1.0
------

- :class:`icalendar_compatibility.Location` uses the URL in the location text

v0.0.3
------

- Update classifiers for PyPI

v0.0.2
------

- document development
- correct metadata for PyPI

v0.0.1
------

- create Documentation
- add :class:`icalendar_compatibility.Description`
- add :class:`icalendar_compatibility.Location`
