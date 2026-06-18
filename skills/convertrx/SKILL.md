---
name: convertrx
description: XXX
license: MIT
metadata:
  version: 0.1.0
  author: KCL SGDP workshop group
  tags:
  - gwas
  - wgs
  openclaw:
    requires:
      bins:
      - python3
    always: false
    emoji: 📊
    homepage: https://github.com/ClawBio/ClawBio
    os:
    - darwin
    - linux
    install:
    - kind: conda
      package: plink2
      bins:
      - plink2
    - kind: conda
      package: regenie
      bins:
      - regenie
    trigger_keywords:
    - WGS
---

# 📊 GWAS Pipeline

You are **convertrx**, a specialised ClawBio agent for a pharmacogenomic profiling. Your role is to automate best-practice QC and prediction of their pharmacogenomic metaboliser status from genotype files to publication-ready results.

When a person takes a drug, the drug will be metabolised. This process is controlled by certain genes.

## Trigger

> **This is the most important section.** It determines whether the agent discovers
> and fires this skill. Be loud, explicit, and list every plausible phrasing.

**Fire this skill when the user says any of:**
- "exact phrase 1"
- "exact phrase 2"
- "keyword or synonym"
- "another way a user might ask for this"

**Do NOT fire when:**
- [Describe similar-sounding requests that should route elsewhere]
- [Edge case that belongs to a different skill]

**Design notes:** The trigger must be loud, not subtle. Models skip subdued
descriptions. Use exact phrases, domain-specific terms, and multiple synonyms.
If two skills sound similar, the trigger is where you disambiguate.

## Why This Exists

- **Without it**: Researchers must work manually, writing hundreds of lines of bash, managing dozens of parameters, and applying field-standard QC thresholds by hand
- **With it**: A single command runs the full analysis and prediction.

## Core Capabilities

1. **Run pharmgx-reporter**: Generate a personalised drug–gene interaction report from consumer genetic data
2. **Run clinpgx**: Look up gene-drug interactions, clinical annotations, CPIC guidelines, FDA drug labels, and allele definitions from the ClinPGx REST API (https://api.clinpgx.org/).
3. **Unified reporting**: Merge, deduplicate, and rank results across all sources using a tabular format

## Scope

**One skill, one task.** This skill does [specific task] and nothing else.
If your skill is trying to do two unrelated jobs, split it into two skills.

## Input Formats

| Format | Extension | Required Fields | Example |
|--------|-----------|-----------------|---------|
| 23andMe raw data | `.txt`, `.txt.gz` | rsid, chromosome, position, genotype | `demo_patient.txt` |
| AncestryDNA raw data | `.txt` | rsid, chromosome, position, allele1, allele2 | — |

## Workflow

1. **Run pharmgx-reporter**: Read raw genetic data, auto-detect format (23andMe vs AncestryDNA)
2. **Run clinpgx**: Look up gene-drug interactions, clinical annotations, CPIC guidelines, FDA drug labels, and allele definitions from the ClinPGx REST API.
3. **Report**: Generate `report.csv` with gene profile table, drug summary, and clinical alerts

## CLI Reference

```bash
# Standard usage
python skills/your-skill-name/your_skill.py \
  --input <input_file> --output <report_dir>

# Demo mode (synthetic data, no user files needed)
python skills/your-skill-name/your_skill.py --demo --output /tmp/demo

# Via ClawBio runner
python clawbio.py run <alias> --input <file> --output <dir>
python clawbio.py run <alias> --demo
```

## Demo

To verify the skill works:

```bash
python clawbio.py run <alias> --demo
```

Expected output: [Brief description of what the demo produces, e.g. "a 3-page report covering 12 genes and 51 drugs with a synthetic patient"]

## Algorithm / Methodology

Describe the core methodology so an AI agent can apply it even without the Python script:

1. **Step**: Detail
2. **Step**: Detail
3. **Step**: Detail

**Key thresholds / parameters**:
- Parameter 1: value (source: [database/paper])
- Parameter 2: value (source: [database/paper])

## Example Queries

- "Example query 1 that would route here"
- "Example query 2"
- "Example query 3"

## Example Output

> Show, do not just describe. Include an actual rendered sample of what the skill
> produces. If the output is a table, show the table. If it is a report, show the
> first section. This is far more effective than a format description alone.

```markdown
# [Skill Name] Report

**Input**: demo_data.ext (3 variants)
**Date**: 2026-04-05

| Column A | Column B | Result |
|----------|----------|--------|
| value1   | value2   | finding |
| value3   | value4   | finding |

## Summary
[One paragraph interpreting the results]

*ClawBio is a research tool. Not a medical device.*
```

## Output Structure

```
output_directory/
├── report.md              # Primary markdown report
├── result.json            # Machine-readable results
├── figures/
│   └── plot.png           # Visualisation(s)
├── tables/
│   └── results.csv        # Tabular data
└── reproducibility/
    ├── commands.sh         # Exact commands to reproduce
    └── environment.yml     # Conda/pip environment snapshot
```

<!-- This tree is the skill's output contract. TestOutputContract in tests/ runs
     the skill in --demo mode and asserts every file listed here is produced.
     If an artifact is only produced conditionally, add "(optional)" to its
     comment to exempt it, or remove it from this tree. Keep the list honest:
     do not document outputs the skill does not always write. -->

## Dependencies

**Required** (in `requirements.txt` or skill-level install):
- `package` >= version; purpose

**Optional**:
- `package`; purpose (graceful degradation without it)

## Gotchas

> This is the highest-signal section. Document every place where the model
> typically goes wrong, makes bad assumptions, or produces subtly incorrect output.
> Each gotcha should follow the pattern: "You will want to do X. Do not. Here is why."

- **Gotcha 1**: The model tends to [bad assumption]. Instead, [correct behaviour]. Why: [reason from testing].
- **Gotcha 2**: When [specific scenario], the model will [wrong action]. The correct approach is [right action].
- **Gotcha 3**: [Common failure mode discovered during stress testing]

**How to populate this section:** Run your skill 10 times with varied inputs. Every
time you have to correct or iterate on the output, write it down here. After
stress testing, this section should have at least 3 entries.

## Safety

- **Local-first**: No data upload without explicit consent
- **Disclaimer**: Every report includes the ClawBio medical disclaimer
- **Audit trail**: Log all operations to reproducibility bundle
- **No hallucinated science**: All parameters trace to cited databases

## Agent Boundary

The agent (LLM) dispatches and explains. The skill (Python) executes.
The agent must NOT override thresholds or invent associations.

## Integration with Bio Orchestrator

**Trigger conditions**: the orchestrator routes here when:
- [Keyword or file-type pattern 1]
- [Keyword or file-type pattern 2]

**Chaining partners**: this skill connects with:
- `[other-skill]`: [How they connect, e.g. "PharmGx output feeds into profile-report"]

> If your skill produces clean structured output (JSON, CSV, markdown with headers),
> it can chain. If it produces free-form prose, it cannot. Design for chaining.

## Maintenance

- **Review cadence**: Re-evaluate this skill monthly or when upstream databases update
- **Staleness signals**: [What would make this skill outdated, e.g. "new ClinVar release", "API endpoint change"]
- **Deprecation**: If the skill no longer serves users, archive it to `skills/_deprecated/` with a note explaining why

## Citations

- [Database/Paper 1](URL); what it provides
- [Database/Paper 2](URL); what it provides
