"""Public API surface: every ``__all__`` symbol must be importable."""

import importlib

import thanos_state_machine as tsm


def test_all_exports_are_importable():
    for name in tsm.__all__:
        assert hasattr(tsm, name), f"__all__ lists {name!r} but it is not defined"
        obj = getattr(tsm, name)
        if name == "__version__":
            assert isinstance(obj, str)


def test_version_matches_package_metadata():
    from importlib.metadata import version

    assert tsm.__version__ == version("thanos-state-machine")


def test_fresh_import_has_no_stale_exports():
    mod = importlib.reload(importlib.import_module("thanos_state_machine"))
    assert set(mod.__all__) == set(tsm.__all__)
