# Flavor Masking: Bitter-Risk and Off-Note Analysis

This module supports MoBai's off-note masking strategy. High-protein beverages,
especially those using whey protein isolate, carry characteristic off-notes such as
bitterness, sulphury volatiles, and soapy fatty-acid notes. This module uses
molecular cheminformatics to anticipate which constituent compounds are most likely
to contribute a bitter off-note, so that formulation and masking can be targeted at
them.

## Bitter-risk prediction

Each candidate compound is encoded as a 2048-bit Morgan molecular fingerprint
(ECFP4-equivalent, radius 2). A Random Forest classifier is trained on labelled
bitter reference compounds (for example leucine, isoleucine, tryptophan, caffeine,
quinine) and non-bitter reference compounds (for example glucose, sucrose, vanillin,
maltol). The trained classifier then predicts a bitter-risk probability for every
compound in the MoBai flavour universe.

The prediction anticipates off-note risk at the compound level. It does not predict
consumer liking.

### Outputs

- `outputs/bitter_predictions.csv`     Per-compound bitter probability and risk status
- `outputs/bitter_risk_scatter.png`    Molecular weight versus bitter probability

The compounds flagged with the highest bitter risk are the branched-chain and
aromatic amino acids (tryptophan, leucine, isoleucine, valine, phenylalanine) and
known bitter references (quinine, limonin, naringenin, caffeine), which is consistent
with the food-science literature on protein bitterness. This points masking effort at
the right targets.

## Masking mechanisms

The bitter-risk screen informs which off-notes to prioritise. The masking itself is
delivered in the product through a combination of mechanisms drawn from the
food-science literature:

- Cyclic oligosaccharide encapsulation (for example beta-cyclodextrin) to physically
  trap volatile off-note compounds.
- Maillard-derived roasted and caramel notes that shift the flavour foreground.
- Mild acidification (citric and malic acid) to reduce bitter and astringent
  perception.
- Fermentation-derived dairy notes (for example from BB-12 cultures) that contribute
  freshness and mask chalky and metallic perceptions.
- Tea polyphenol interactions that complex with protein and moderate astringency.

## Reproducing the bitter-risk screen

```bash
pip install rdkit scikit-learn numpy pandas matplotlib
python bitter_risk.py
```

This writes `outputs/bitter_predictions_repro.csv` and a reproduction scatter plot.
The committed `outputs/bitter_predictions.csv` and `outputs/bitter_risk_scatter.png`
are the reference run. Exact probabilities can vary marginally with the RDKit version.

## Attribution

The molecular reference data, the bitter and non-bitter training labels, and the
fingerprint-plus-Random-Forest method were authored by the MoBai team member who
maintains the molecular cheminformatics codebase
(github.com/Narscode/mobai-flavorgraph). `bitter_risk.py` is a trimmed,
self-contained extract scoped to the bitter-risk analysis used here.
