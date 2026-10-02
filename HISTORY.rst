=======
History
=======

Unreleased
----------

Results change for some settings; delete old caches with
``Launch.delete_previous_IO_builds()`` (new caches get new names anyway).

* Fixed: substitutions flagged in ``sk2``, ``sk3`` or ``sk4`` moved nothing;
  they now move the change made by ``kt2``, ``at1`` or ``at2``.
* Fixed: with ``sk1`` set, a substitution also moved the additive changes
  ``at1``/``at2`` of the same row.
* Fixed: ``make_secondary`` now also splits final demand between primary and
  secondary materials, so the supply-use tables stay balanced.
* Fixed: the info sheet in saved results named method 0 as MSC and method 1
  as TC; it now names them correctly.
* Fixed: the cached IO tables were reused across transformation methods. The
  cache name now includes the method and a version.
* Fixed: ``delete_previous_IO_builds`` only worked from the repository root.

0.1.0 (2018-05-11)
------------------

* First release on PyPI.
