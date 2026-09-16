Notes for Developers
====================

Repository: `pycalendar/icalendar_compatibility <https://github.com/pycalendar/icalendar_compatibility>`_

We use ``tox`` to run the tests.

.. code-block:: shell

    pip install tox
    tox

There are several environments to use.

.. code-block:: shell

    tox -e py312  # run Python 3.12
    tox -e ruff   # code quality
    tox -e black  # code formatting
    tox -e docs   # build the documentation to ./html
    tox -e build  # build the package in ./dist

New Release
-----------

To create a new release:

1. Edit the ``changes.rst`` file.
2. Commit the changes::

      git add docs/changes.rst
      git commit -m"log changes"

3. Create a new tag and push it::

      git push
      git tag v0.0.2
      git push origin v0.0.2
