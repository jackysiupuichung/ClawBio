"""
Tests for check_interactions.py — the CYP450 shared-enzyme drug-drug
interaction step of the ConvertRX workflow.

Covers loading the bundled cyp450_drug_roles.csv, collision detection across
2 and 3 drugs, role-based risk interpretation, and (critically) that the
default CSV path resolves regardless of the current working directory.
"""

import importlib.util
import os
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = SKILL_DIR / "check_interactions.py"
CSV_PATH = SKILL_DIR / "cyp450_drug_roles.csv"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_interactions", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ci = _load_module()


def test_default_csv_path_resolves_from_any_cwd(tmp_path, monkeypatch):
    """DEFAULT_CSV_PATH must point at the bundled CSV no matter where the
    process is launched from — not a CWD-relative string."""
    monkeypatch.chdir(tmp_path)
    lookup = ci.load_roles(ci.DEFAULT_CSV_PATH)
    assert lookup, "default CSV path failed to load roles from a foreign CWD"


def test_load_roles_keys_are_lowercased():
    lookup = ci.load_roles(str(CSV_PATH))
    assert "warfarin" in lookup
    # each entry is (enzyme, role, original_name)
    enzymes = {e for e, _r, _n in lookup["warfarin"]}
    assert "1A2" in enzymes


def test_two_drug_substrate_inhibitor_collision():
    lookup = ci.load_roles(str(CSV_PATH))
    collisions, unmatched, isolated = ci.find_collisions(["warfarin", "amiodarone"], lookup)
    assert "1A2" in collisions
    roles = collisions["1A2"]
    assert any("warfarin" == n.lower() for n in roles.get("substrate", []))
    assert any("amiodarone" == n.lower() for n in roles.get("inhibitor", []))
    assert not unmatched


def test_unmatched_drug_is_reported():
    lookup = ci.load_roles(str(CSV_PATH))
    _collisions, unmatched, _isolated = ci.find_collisions(
        ["warfarin", "notarealdrugxyz"], lookup
    )
    assert "notarealdrugxyz" in unmatched


def test_describe_risk_substrate_plus_inhibitor():
    roles = {"substrate": ["drugA"], "inhibitor": ["drugB"]}
    msg = ci.describe_risk(roles)
    assert "raise" in msg.lower() and "substrate" in msg.lower()


def test_describe_risk_substrate_plus_inducer():
    roles = {"substrate": ["drugA"], "inducer": ["drugB"]}
    msg = ci.describe_risk(roles)
    assert "lower" in msg.lower()
