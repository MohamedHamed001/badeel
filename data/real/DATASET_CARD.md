# Badeel Real-Drug Demo Dataset

> **SYNTHETIC DATA. NOT FOR CLINICAL USE.** Every drug name, brand and clinical statement in this document is fictional and was generated for software evaluation. It does not describe any real medicine.

## What this is

A demonstration dataset of **real active ingredients** with **real Egyptian
brand names**. Ingredient-level clinical facts (contraindications, interactions,
ATC codes, narrow-therapeutic-index status) are standard reference pharmacology.
EGP prices are **illustrative** and stock status is assigned for demonstration.

This dataset powers the demo only. The graded evaluation and the 100% safety
result are measured on the separate synthetic dataset, whose ground truth is
true by construction.

## Not for clinical use

Simplified reference knowledge for a software demo, not a validated drug
database. Always verify against an authoritative source and clinical judgement.

## Contents

| File | Rows |
|---|---|
| `ingredients.csv` | 26 |
| `products.csv` | 63 |
| `aliases.csv` | 40 misspellings plus Arabic names |
| `interactions.csv` | 48 |
| `leaflets/*.md` | 26 documents |
