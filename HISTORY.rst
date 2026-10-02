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
* Changed: building the IO tables and running scenarios is several times
  faster and uses less memory; results are unchanged. Scenarios reuse one
  factorization of the baseline. New dependency: ``scipy``.
* Changed: the helpers in ``Operations`` take vectors where they took
  diagonal matrices (``x`` instead of ``np.diag(x)``). Diagonal matrices still
  work but raise a ``DeprecationWarning``.
* Removed: ``Transform`` no longer returns the Leontief inverse ``L``, and its
  ``diag_*`` and ``inv_diag_*`` attributes are replaced by ``inv_q`` and
  ``inv_g``. ``Launch`` never used them.

0.1.0 (2018-05-11)
------------------

* First release on PyPI.
