# samplesheet_collision_check

A Python utility to detect Sample_ID collisions in Illumina SampleSheets.

## Overview

This script parses an Illumina `SampleSheet.csv` file (specifically the `[BCLConvert_Data]` section) and checks for index collisions. A collision is defined as multiple `Sample_ID` entries sharing the same combination of `Index` (and `Index2` if present) on the same `Lane`.

## Usage

```bash
python samplesheet_collision_check.py [-v] <csv_path>
```

### Options

*   `csv_path`: Path to the SampleSheet.csv file.
*   `-v`, `--verbose`: Enable verbose output.

## Example

```bash
python samplesheet_collision_check.py example.with_collision.SampleSheet.csv
```
