#!/usr/bin/env python3
"""
check_interactions.py

Takes a list of drugs and checks them against cyp450_drug_roles.csv to find
shared-enzyme collisions, including cases involving more than two drugs at once.

Usage:
    python3 check_interactions.py drug1 drug2 drug3 ...
    python3 check_interactions.py --csv path/to/cyp450_drug_roles.csv drug1 drug2
    python3 check_interactions.py --interactive

The CSV is expected to have columns: enzyme, drug, role
where role is one of: substrate, inhibitor, inducer
"""

import argparse
import csv
import sys
from collections import defaultdict


DEFAULT_CSV_PATH = "cyp450_drug_roles.csv"


def load_roles(csv_path):
    """
    Load the CSV into a lookup: drug_name_lowercase -> list of (enzyme, role).
    Keeps the original-case drug name too, since display should look natural.
    """
    lookup = defaultdict(list)
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            drug = row["drug"].strip()
            enzyme = row["enzyme"].strip()
            role = row["role"].strip().lower()
            lookup[drug.lower()].append((enzyme, role, drug))
    return lookup


def find_collisions(drug_list, lookup):
    """
    For the given drugs, find every enzyme where two or more of them show up
    (in any combination of substrate / inhibitor / inducer).

    Returns:
        collisions: dict enzyme -> dict role -> list of original-case drug names
        unmatched: list of input drugs not found in the CSV at all
        matched_but_isolated: list of (drug, enzyme, role) tuples for drugs that
            ARE in the dataset but don't share an enzyme with anything else input
    """
    enzyme_buckets = defaultdict(lambda: defaultdict(list))
    unmatched = []
    drug_to_enzymes = defaultdict(set)

    for drug in drug_list:
        key = drug.strip().lower()
        entries = lookup.get(key)
        if not entries:
            unmatched.append(drug)
            continue
        for enzyme, role, original_name in entries:
            enzyme_buckets[enzyme][role].append(original_name)
            drug_to_enzymes[drug].add(enzyme)

    # Only keep enzyme buckets where 2+ distinct input drugs are present
    collisions = {}
    for enzyme, roles in enzyme_buckets.items():
        distinct_drugs = set()
        for role, names in roles.items():
            distinct_drugs.update(n.lower() for n in names)
        if len(distinct_drugs) >= 2:
            collisions[enzyme] = roles

    # Drugs that matched the CSV but never landed in a collision enzyme
    collision_enzymes = set(collisions.keys())
    matched_but_isolated = []
    for drug in drug_list:
        key = drug.strip().lower()
        if key in lookup and not (drug_to_enzymes[drug] & collision_enzymes):
            matched_but_isolated.append(drug)

    return collisions, unmatched, matched_but_isolated


def describe_risk(roles):
    """
    Give a one-line plain-language read of what's happening in an enzyme bucket,
    based on which roles are present.
    """
    has_substrate = "substrate" in roles
    has_inhibitor = "inhibitor" in roles
    has_inducer = "inducer" in roles

    if has_substrate and has_inhibitor and has_inducer:
        return "substrate levels are being pulled in opposite directions at once (inhibited and induced)"
    if has_substrate and has_inhibitor:
        return "inhibitor(s) may raise substrate drug levels, increasing exposure/toxicity risk"
    if has_substrate and has_inducer:
        return "inducer(s) may lower substrate drug levels, risking reduced effectiveness"
    if has_inhibitor and has_inducer:
        return "inhibitor(s) and inducer(s) are both acting on this enzyme, competing effects"
    if has_substrate and len(roles.get("substrate", [])) >= 2:
        return "multiple substrates compete for the same enzyme capacity"
    return "multiple drugs share this enzyme pathway"


def print_report(drug_list, collisions, unmatched, matched_but_isolated):
    print()
    print("Drugs checked:", ", ".join(drug_list))
    print("=" * 60)

    if not collisions:
        print("No shared-enzyme collisions found among these drugs.")
    else:
        print(f"Found {len(collisions)} enzyme(s) with overlapping drugs:\n")
        for enzyme, roles in sorted(collisions.items()):
            print(f"Enzyme: {enzyme}")
            for role in ("substrate", "inhibitor", "inducer"):
                if role in roles:
                    names = sorted(set(roles[role]))
                    print(f"   {role:10s}: {', '.join(names)}")
            n_drugs_here = len(set(n.lower() for r in roles.values() for n in r))
            print(f"   -> {n_drugs_here} of your drugs converge here: {describe_risk(roles)}")
            print()

    if matched_but_isolated:
        print("No shared enzyme with anything else on the list (checked, no collision):")
        print("   " + ", ".join(matched_but_isolated))
        print()

    if unmatched:
        print("Not found in the dataset (check spelling, or not covered by this table):")
        print("   " + ", ".join(unmatched))
        print()


def main():
    parser = argparse.ArgumentParser(description="Check a list of drugs for shared CYP450 enzyme interactions.")
    parser.add_argument("drugs", nargs="*", help="Drug names to check, space separated")
    parser.add_argument("--csv", default=DEFAULT_CSV_PATH, help="Path to cyp450_drug_roles.csv")
    parser.add_argument("--interactive", action="store_true", help="Prompt for drugs instead of using command-line args")
    args = parser.parse_args()

    try:
        lookup = load_roles(args.csv)
    except FileNotFoundError:
        print(f"Could not find CSV file at: {args.csv}")
        print("Pass its location with --csv path/to/cyp450_drug_roles.csv")
        sys.exit(1)

    if args.interactive or not args.drugs:
        raw = input("Enter drug names, separated by commas: ")
        drug_list = [d.strip() for d in raw.split(",") if d.strip()]
    else:
        drug_list = args.drugs

    if len(drug_list) < 2:
        print("Enter at least two drugs to check for interactions.")
        sys.exit(1)

    collisions, unmatched, matched_but_isolated = find_collisions(drug_list, lookup)
    print_report(drug_list, collisions, unmatched, matched_but_isolated)


if __name__ == "__main__":
    main()
