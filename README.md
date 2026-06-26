# MoBai AI and Consumer Data Pipeline

This repository contains the AI and data work behind MoBai, a high-protein RTD
yogurt-style drink developed for the KSF (Master Kong) Global Innovation Challenge
2026. The brief asks teams to leverage AI and consumer data to develop personalised
flavours for sustainable high-protein beverages. MoBai is positioned as a daily
morning beverage for urban working adults aged 25 to 38 in the Asia-Pacific region.

The work is organised as a chain that runs from consumer language to molecular
science: consumer signals tell us what people want and what currently fails them,
a molecular AI screen ranks flavour pairings that are compatible with those signals,
and a molecular off-note analysis informs how protein off-notes are suppressed.

## Repository structure

```
NUSFTC/
├── nlp_social_listening/   Consumer intelligence from social media (English)
├── flavor_pairing/         Molecular pairing-compatibility recommender (FlavorGraph)
├── flavor_masking/         Bitter-risk and off-note masking analysis (cheminformatics)
└── README.md               This file
```

## The three AI components

1. Consumer intelligence (`nlp_social_listening/`). Collects and analyses 5,021
   English-language tweets across six consumer-insight dimensions: flavour
   preferences, morning routine, sensory pain points, yogurt-drink format,
   consumption occasions, and competitor sentiment. Uses a dual-model sentiment
   consensus (VADER and TextBlob) and K-Means consumer segmentation.

2. Molecular pairing compatibility (`flavor_pairing/`). Uses pre-trained
   300-dimensional FlavorGraph embeddings (Park et al., 2021) to score how
   molecularly compatible a candidate flavour is with the flavours consumers
   already like, and to screen the full ingredient vocabulary for new candidates.
   This is a ranking and screening tool, not a liking predictor (see that folder's
   README for the explicit limitations).

3. Off-note and bitter-risk analysis (`flavor_masking/`). Uses Morgan
   (ECFP4-equivalent) molecular fingerprints and a Random Forest classifier to
   predict which constituent compounds are most likely to contribute a bitter
   off-note, which informs the masking strategy.

## How the components connect

The consumer intelligence layer produces a ranked flavour-sentiment signal. The
pairing-compatibility layer takes that signal, maps the preferred flavours into the
molecular embedding space, and ranks candidate pairings by their compatibility with
that space. The off-note analysis then characterises the compounds that need masking.
Together they move from a broad consumer signal to a small, human-testable shortlist
of flavour concepts.

## Environment

All Python work runs in a conda environment named `ml`:

```bash
conda activate ml
```

Each subfolder has its own README with run order, data files, and dependencies.

## Attribution

The molecular fingerprint and bitter-risk analysis in `flavor_masking/` is based on
work by the MoBai team member who maintains the cheminformatics codebase
(github.com/Narscode/mobai-flavorgraph). The FlavorGraph embeddings and graph are
from Park et al., 2021 (FlavorGraph: a large-scale food-chemical graph).
