# MorphoCloud Issues Word Map

A word cloud visualization of keywords extracted from all GitHub issues in the [MorphoCloud/MorphoCloudInstances](https://github.com/MorphoCloud/MorphoCloudInstances) repository.

## Overview

This project analyzes 456 GitHub issues (both open and closed) from the MorphoCloud repository to identify and visualize the most frequently mentioned keywords in the issue descriptions.

## Results

![Word Map](wordmap.png)

### Top 10 Keywords

1. **slicermorph** (98) - Primary software platform
2. **scans** (84) - CT/imaging data
3. **segmentation** (64) - Image segmentation
4. **student** (63) - User demographic
5. **morphometrics** (59) - Analysis technique
6. **course** (53) - Educational context
7. **models** (51) - 3D models
8. **microct** (46) - Micro-CT imaging
9. **slicer** (40) - 3D Slicer software
10. **specimens** (36) - Biological specimens

## Data Processing

### Filtering Rules

**Banned Words:**
- Platform/infrastructure terms: morphocloud, university, instance, create, created, workshop, participant, github, issue
- Personal references: attending, orcid, individual names
- Geographic locations: countries, states, cities

**Word Unification:**
- segment/segments/segmenting → segmentation
- morphometric → morphometrics

### Statistics

- Total issues processed: 456
- Issues with descriptions: 441
- Unique keywords identified: 1,422

## Files

- `wordmap_generator.py` - Python script to generate the word map
- `wordmap.png` - Generated visualization
- `keyword_frequencies.csv` - Complete keyword frequency data
- `README.md` - This file

## Usage

### Requirements

```bash
pip install wordcloud matplotlib
```

### Run

```bash
# Fetch issues from GitHub
gh issue list --repo MorphoCloud/MorphoCloudInstances --state all --limit 1000 --json number,title,body > all_issues.json

# Generate word map
python wordmap_generator.py
```

The script will:
1. Parse the `all_issues.json` file
2. Extract keywords from issue descriptions
3. Apply filtering and unification rules
4. Generate `wordmap.png` and `keyword_frequencies.csv`

## Color Palette

Uses `twilight_shifted` colormap for good readability with varied blues, purples, pinks, and teals.

## License

MIT

## Date

Generated: January 15, 2026
