"""
Bitter-risk prediction for MoBai off-note analysis (Layer 4).

This is a BitterPredict-style classifier: each candidate compound is encoded as a
2048-bit Morgan (ECFP4-equivalent, radius 2) molecular fingerprint, and a Random
Forest trained on labelled bitter and non-bitter reference compounds predicts a
bitter-risk probability for every molecule in the MoBai flavour universe.

The predicted probability is used to anticipate which constituent compounds of a
flavour are most likely to contribute a bitter off-note, so that formulation and
masking can be targeted at them. It does not predict consumer liking.

Requirements:
    pip install rdkit scikit-learn numpy pandas matplotlib

Note:
    The committed outputs/bitter_predictions.csv and outputs/bitter_risk_scatter.png
    are the reference run. This script reproduces the same method; exact probabilities
    can vary marginally with the RDKit version used.

Attribution:
    The molecular reference data, the bitter/non-bitter training labels, and the
    fingerprint-plus-RandomForest method were authored by the MoBai team member who
    maintains the molecular cheminformatics work (github.com/Narscode/mobai-flavorgraph).
    This file is a trimmed, self-contained extract scoped to the bitter-risk analysis
    used by MoBai Layer 4.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

OUTPUT_DIR = Path(__file__).parent / "outputs"

# ---------------------------------------------------------------------------
# Molecular reference data: name -> (SMILES, molecular weight)
# ---------------------------------------------------------------------------
MOLECULES = {
    # Mango
    "ethyl butanoate": ("CCCC(=O)OCC", 116.16),
    "3-carene": ("CC1=CCC2C(C1)C2(C)C", 136.24),
    "alpha-terpinolene": ("CC1=CCC(=C(C)C)CC1", 136.24),
    "beta-myrcene": ("CC(=CCCC(=C)C=C)C", 136.24),
    "limonene": ("CC1=CCC(CC1)C(=C)C", 136.24),
    "gamma-terpinene": ("CC1=CCC(C=C1)C(C)C", 136.24),
    "isoamyl acetate": ("CC(C)CCOC(=O)C", 130.18),
    "4-hydroxy-2,5-dimethyl-3(2H)-furanone": ("CC1C(=O)C(=C(O1)C)O", 128.13),
    # Jasmine
    "benzyl acetate": ("CC(=O)OCC1=CC=CC=C1", 150.17),
    "linalool": ("CC(=CCCC(C)(C=C)O)C", 154.25),
    "benzyl benzoate": ("C1=CC=C(C=C1)COC(=O)C2=CC=CC=C2", 212.24),
    "methyl jasmonate": ("COC(=O)CC1C(CC=CCC)C(=O)CC1", 224.3),
    "indole": ("C1=CC=C2C(=C1)C=CN2", 117.15),
    "cis-jasmone": ("CC=CCC1=C(C(=O)CC1)C", 164.24),
    "alpha-farnesene": ("CC(=CCCC(=C)CCC=C(C)C)C", 204.35),
    # Coconut
    "delta-decalactone": ("CCCCCC1CCC(=O)O1", 170.25),
    "gamma-nonalactone": ("CCCCC1CCC(=O)O1", 156.22),
    "delta-octalactone": ("CCCC1CCC(=O)O1", 142.2),
    "methylheptanone": ("CC(C)CCC(=O)C", 114.19),
    # Milk tea
    "geraniol": ("CC(=CCCC(=CCO)C)C", 154.25),
    "pyrazine": ("C1=CN=CC=N1", 80.09),
    "2-methylpyrazine": ("CC1=CN=CC=N1", 94.11),
    "benzaldehyde": ("C1=CC=C(C=C1)C=O", 106.12),
    "phenylacetaldehyde": ("C1=CC=C(C=C1)CC=O", 120.15),
    "theaflavin": ("C1C(C(OC2=CC(=CC(=C12)O)O)C3=CC(=C4C(=C3)C(=O)C5=C(C(=C(C=C5)O)O)C6C(CC7=C(O6)C=C(C=C7O)O)O)O)O)O", 564.5),
    "catechin": ("C1C(C(OC2=CC(=CC(=C12)O)O)C3=CC(=C(C=C3)O)O)O", 290.27),
    "caffeine": ("CN1C=NC2=C1C(=O)N(C(=O)N2C)C", 194.19),
    # Yogurt base
    "acetaldehyde": ("CC=O", 44.05),
    "diacetyl": ("CC(=O)C(=O)C", 86.09),
    "acetoin": ("CC(C(=O)C)O", 88.11),
    "lactic acid": ("CC(C(=O)O)O", 90.08),
    "acetic acid": ("CC(=O)O", 60.05),
    "butyric acid": ("CCCC(=O)O", 88.11),
    "ethyl acetate": ("CCOC(=O)C", 88.11),
    # WPI off-notes
    "dimethyl sulfide": ("CSC", 62.13),
    "dimethyl disulfide": ("CSSC", 94.2),
    "hexanal": ("CCCCCC=O", 100.16),
    "nonanal": ("CCCCCCCCC=O", 142.24),
    "heptanal": ("CCCCCCC=O", 114.19),
    "octanoic acid": ("CCCCCCCC(=O)O", 144.21),
    "decanoic acid": ("CCCCCCCCCC(=O)O", 172.26),
    "dodecanoic acid": ("CCCCCCCCCCCC(=O)O", 200.32),
    "2-heptanone": ("CCCCCC(=O)C", 114.19),
    # Masking candidates
    "vanillin": ("COC1=C(C=CC(=C1)C=O)O", 152.15),
    "ethyl vanillin": ("CCOC1=C(C=CC(=C1)C=O)O", 166.17),
    "maltol": ("CC1=C(C(=O)C=CO1)O", 126.11),
    "citric acid": ("C(C(=O)O)C(CC(=O)O)(C(=O)O)O", 192.12),
    "malic acid": ("C(C(=O)O)C(C(=O)O)O", 134.09),
    "sodium chloride": ("[Na+].[Cl-]", 58.44),
    "zinc gluconate": ("C(C(C(C(C(CO)O)O)O)O)C(=O)[O-].C(C(C(C(C(CO)O)O)O)O)C(=O)[O-].[Zn+2]", 455.7),
    "cyclodextrin": ("C1C2C(C(C(O2)OC3C(C(C(O3)OC4C(C(C(O4)OC5C(C(C(O5)OC6C(C(C(O6)OC7C(C(C(O7)OC8C(C(C(O8)OC1)CO)O)O)CO)O)O)CO)O)O)CO)O)O)CO)O)O", 1135.0),
    # Bitter receptor amino acids
    "leucine": ("CC(C)CC(C(=O)O)N", 131.17),
    "isoleucine": ("CCC(C)C(C(=O)O)N", 131.17),
    "valine": ("CC(C)C(C(=O)O)N", 117.15),
    "phenylalanine": ("C1=CC=C(C=C1)CC(C(=O)O)N", 165.19),
    "tryptophan": ("C1=CC=C2C(=C1)C(=CN2)CC(C(=O)O)N", 204.23),
    "tyrosine": ("C1=CC(=CC=C1CC(C(=O)O)N)O", 181.19),
    # Bitter classifier reference positives / negatives
    "quinine": ("COC1=CC2=C(C=CN=C2C=C1)C(C3CC4CCN3CC4C=C)O", 324.4),
    "naringenin": ("C1C(OC2=CC(=CC(=C2C1=O)O)O)C3=CC=C(C=C3)O", 272.25),
    "limonin": ("CC1(C2CC3C4(C5CC6C7(C(C5(CC4C(=O)O2)O1)CC(=O)C7C8=COC(=O)O8)C)C)C", 470.5),
    "glucose": ("C(C1C(C(C(C(O1)O)O)O)O)O", 180.16),
    "sucrose": ("C(C1C(C(C(O1)OC2(C(C(C(O2)CO)O)O)CO)O)O)O", 342.3),
    # APAC exotic candidates
    "2-acetyl-1-pyrroline": ("CC(=O)C1=NCCC1", 111.14),
    "alpha-pinene": ("CC1=C2CC(C1(C)C)C2", 136.24),
    "beta-ionone": ("CC1=C(C(CCC1)(C)C)C=CC(=O)C", 192.3),
    "gamma-decalactone": ("CCCCCC1CCC(=O)O1", 170.25),
    "borneol": ("CC1(C2CCC1(C(C2)O)C)C", 154.25),
    "camphor": ("CC1(C2CCC1(C(=O)C2)C)C", 152.23),
    "alpha-terpineol": ("CC1=CCC(CC1)C(C)(C)O", 154.25),
    "ethyl hexanoate": ("CCCCCC(=O)OCC", 144.21),
    "phenylethyl alcohol": ("C1=CC=C(C=C1)CCO", 122.16),
    "citronellol": ("CC(CCC=C(C)C)CCO", 156.27),
    "citral": ("CC(=CCCC(=CC=O)C)C", 152.23),
    "gingerol": ("CCCCCC(CC(=O)CC1=CC(=C(C=C1)O)OC)O", 294.39),
    "turmerone": ("CC(=CC(=O)CC(C)C1=CC=C(C=C1)C)C", 218.33),
    "alpha-phellandrene": ("CC1=CCC(C=C1)C(C)C", 136.24),
    "caprylic acid": ("CCCCCCCC(=O)O", 144.21),
    "capric acid": ("CCCCCCCCCC(=O)O", 172.26),
    "lauric acid": ("CCCCCCCCCCCC(=O)O", 200.32),
}

# Reference training labels
BITTER_POSITIVES = ["leucine", "isoleucine", "valine", "tryptophan", "phenylalanine",
                    "caffeine", "quinine", "naringenin", "limonin"]
BITTER_NEGATIVES = ["glucose", "sucrose", "vanillin", "ethyl acetate", "linalool",
                    "benzyl acetate", "delta-decalactone", "maltol", "acetaldehyde"]


def morgan_fingerprint(smiles):
    """Return a 2048-bit Morgan fingerprint (radius 2) as a numpy array."""
    if not RDKIT_AVAILABLE:
        raise RuntimeError("RDKit is required. Install with: pip install rdkit")
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit could not parse SMILES: {smiles}")
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
    return np.array(list(fp))


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Build training set
    train_fps, train_labels = [], []
    for name in BITTER_POSITIVES:
        train_fps.append(morgan_fingerprint(MOLECULES[name][0]))
        train_labels.append(1)
    for name in BITTER_NEGATIVES:
        train_fps.append(morgan_fingerprint(MOLECULES[name][0]))
        train_labels.append(0)

    rf = RandomForestClassifier(n_estimators=500, random_state=42)
    rf.fit(train_fps, train_labels)

    # Predict over the full molecule universe
    records = []
    for name, (smiles, weight) in MOLECULES.items():
        prob = float(rf.predict_proba([morgan_fingerprint(smiles)])[0][1])
        status = "bitter risk" if prob > 0.5 else "safe"
        records.append([name, round(prob, 3), status, weight])

    df = pd.DataFrame(records, columns=["compound", "bitter_probability",
                                        "status", "molecular_weight"])
    df = df.sort_values("bitter_probability", ascending=False).reset_index(drop=True)
    out_csv = OUTPUT_DIR / "bitter_predictions_repro.csv"
    df.to_csv(out_csv, index=False)
    print(f"Wrote {out_csv} ({len(df)} compounds, "
          f"{(df.status == 'bitter risk').sum()} flagged bitter risk)")

    # Scatter: molecular weight vs bitter probability
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#c0392b" if s == "bitter risk" else "#27ae60" for s in df.status]
    ax.scatter(df.molecular_weight, df.bitter_probability, c=colors, s=40, alpha=0.8)
    ax.axhline(0.5, color="#888", linestyle="--", linewidth=0.8, label="risk threshold (0.5)")
    ax.set_xlabel("Molecular weight (g/mol)")
    ax.set_ylabel("Predicted bitter probability")
    ax.set_title("MoBai bitter-risk screen (Morgan fingerprint + Random Forest)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "bitter_risk_scatter_repro.png", dpi=150)
    print(f"Wrote {OUTPUT_DIR / 'bitter_risk_scatter_repro.png'}")


if __name__ == "__main__":
    main()
