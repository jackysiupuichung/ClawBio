"""
Genotype test cases for ConvertRX (pharmacogenomics-kcl).

Each fixture in tests/fixtures/ is a synthetic 23andMe-format genotype file
crafted to exercise a specific metaboliser phenotype. These run the
pharmgx-reporter step of the ConvertRX workflow and assert the gene-level
diplotype + phenotype call so regressions in the calling chain are caught.

Synthetic data only — no real patient genotypes.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PHARMGX = REPO_ROOT / "skills" / "pharmgx-reporter" / "pharmgx_reporter.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

# (fixture filename, gene, expected diplotype, expected phenotype)
CASES = [
    ("cyp2c19_poor_metabolizer.txt",       "CYP2C19", "*2/*2",   "Poor Metabolizer"),
    ("cyp2c19_ultrarapid_metabolizer.txt", "CYP2C19", "*17/*17", "Ultrarapid Metabolizer"),
    ("cyp2d6_poor_metabolizer.txt",        "CYP2D6",  "*4/*4",   "Poor Metabolizer"),
    ("cyp2c9_poor_metabolizer.txt",        "CYP2C9",  "*3/*3",   "Poor Metabolizer"),
    ("cyp2d6_normal_metabolizer.txt",      "CYP2D6",  "*1/*1",   "Normal Metabolizer"),
]


@pytest.fixture(scope="module")
def profiles(tmp_path_factory):
    """Run pharmgx-reporter once per fixture; return {fixture: gene_profiles}."""
    out = {}
    for fixture, *_ in CASES:
        fpath = FIXTURES / fixture
        assert fpath.exists(), f"missing fixture: {fpath}"
        outdir = tmp_path_factory.mktemp(fixture.replace(".txt", ""))
        subprocess.run(
            [sys.executable, str(PHARMGX), "--input", str(fpath),
             "--no-enrich", "--output", str(outdir)],
            check=True, capture_output=True, text=True,
        )
        result = json.loads((outdir / "result.json").read_text())
        out[fixture] = result["data"]["gene_profiles"]
    return out


@pytest.mark.parametrize("fixture,gene,diplotype,phenotype", CASES)
def test_genotype_phenotype_call(profiles, fixture, gene, diplotype, phenotype):
    gp = profiles[fixture][gene]
    assert gp["diplotype"] == diplotype, (
        f"{fixture}: {gene} diplotype {gp['diplotype']!r} != {diplotype!r}"
    )
    assert gp["phenotype"] == phenotype, (
        f"{fixture}: {gene} phenotype {gp['phenotype']!r} != {phenotype!r}"
    )


def test_fixtures_are_valid_23andme_format():
    """Every fixture row is tab-separated rsid/chrom/pos/genotype."""
    for fixture in FIXTURES.glob("*.txt"):
        for line in fixture.read_text().splitlines():
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            assert len(parts) == 4, f"{fixture.name}: bad row {line!r}"
            assert parts[0].startswith("rs"), f"{fixture.name}: bad rsid {parts[0]!r}"
            assert set(parts[3].upper()) <= set("ACGT"), \
                f"{fixture.name}: bad genotype {parts[3]!r}"
