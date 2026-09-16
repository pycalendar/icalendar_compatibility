Notes for Developers
====================

Repository: `pycalendar/icalendar_compatibility <https://github.com/pycalendar/icalendar_compatibility>`_

Setup
-----

Use ``git``, ``make`` and ``uv`` to setup the repository for development.

.. code-block:: shell

    git clone https://github.com/pycalendar/icalendar_compatibility.git
    cd icalendar_compatibility
    make init

This installs ``pre-commit`` and the ``uv`` virtual environment.

Testing
-------

Runs ``tox``/``pytest`` to run all the tests.

.. code-block:: shell

    make test

Formatting
----------

Formats the code with ``black``.

.. code-block:: shell

    make format

Documentation
-------------

Build the documentation and edit it while it reloads:

.. code-block:: shell

    make livehtml

Test building the documentation:

.. code-block:: shell

    make html
    make linkcheck

New Release
-----------

To create a new release:

1. Edit the :file:`changes.rst` file.
2. Commit the changes::

      git add docs/changes.rst
      git commit -m"log changes"

3. Create a new tag and push it::

      git push
      git tag v0.0.2
      git push origin v0.0.2
