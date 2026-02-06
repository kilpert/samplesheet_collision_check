import argparse
import csv
import os
import sys
import pandas as pd

def parse_samplesheet(filepath):
    """Parses an Illumina SampleSheet.csv into a dictionary."""
    sections = {}
    current_section = None
    section_content = []

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines
            if not line:
                continue

            # Check for section headers (e.g., [Header], [Data])
            if line.startswith('[') and ']' in line:
                # If we were processing a section, save it
                if current_section:
                    sections[current_section] = process_section(current_section, section_content)
                
                # Start new section
                # Handle potential trailing commas like "[Header],"
                raw_section = line.split(',')[0]
                current_section = raw_section.strip('[]')
                section_content = []
            else:
                section_content.append(line)

    # Process the last section
    if current_section:
        sections[current_section] = process_section(current_section, section_content)

    return sections

def process_section(section_name, lines):
    """Processes lines of a section based on its name."""
    # Heuristic: Sections ending in 'Data' are usually CSV tables.
    # Others are usually Key-Value pairs.
    if section_name.endswith('Data'):
        return process_data_section(lines)
    else:
        return process_kv_section(lines)

def process_data_section(lines):
    """Parses a list of strings as a CSV table."""
    if not lines:
        return []
    
    # csv.DictReader expects an iterable of lines
    reader = csv.DictReader(lines)
    return list(reader)

def process_kv_section(lines):
    """Parses a list of strings as Key-Value pairs."""
    data = {}
    for line in lines:
        # Split on the first comma only
        parts = line.split(',', 1)
        key = parts[0].strip()
        value = parts[1].strip() if len(parts) > 1 else ""
        data[key] = value
    return data

def detect_collision(df):
    """
    Detects Sample_ID collisions, if the same Index + Index2 combination
    is used for multiple Sample_ID on the same Lane.
    """
    if df.empty:
        return df

    # Check for required columns
    if 'Index' not in df.columns or 'Sample_ID' not in df.columns:
        return pd.DataFrame()

    # Determine grouping columns based on availability
    group_cols = ['Index']
    if 'Lane' in df.columns:
        group_cols.append('Lane')
    if 'Index2' in df.columns:
        group_cols.append('Index2')

    # Identify collisions: groups with >1 unique Sample_ID
    collision_mask = df.groupby(group_cols)['Sample_ID'].transform('nunique') > 1
    return df[collision_mask]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for Sample_ID collisions in Illumina SampleSheet.")
    parser.add_argument("csv_path", help="Path to the SampleSheet.csv file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    csv_path = args.csv_path

    try:
        data = parse_samplesheet(csv_path)

    except Exception as e:
        data = None
        print(f"Error: {e}")

    df = pd.DataFrame(data.get("BCLConvert_Data", []))
    if args.verbose:
        print("{:#^100}".format(" BCLConvert_Data "))
        print(df)

    ## Write a function detect_collision(df) that detects Sample_ID collisions, if the same Index + Index2 combination is used for multiple Sample_ID on the same Lane.
    df_collision = detect_collision(df)

    if not df_collision.empty:
        print("{:#^100}".format(" Collisions "))
        print(df_collision)
        sys.exit(f"Error: {len(df_collision)} sample collisions detected!")
    elif args.verbose:
        print("{:#^100}".format(" Collisions "))
        print("No collisions detected.")
    