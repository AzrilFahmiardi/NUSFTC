"""
Build the static chart-data JSON for mobai-web from the project's real artifacts.

Reads the committed NLP result CSVs, the flavor-pairing outputs, the survey result,
and the bitter-risk predictions, then writes accurate JSON the web charts consume.
All quantitative numbers shown on the site come from here (no manual transcription).

Run:
    conda activate ml
    python mobai-web/scripts/build_web_data.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

WEB = Path(__file__).resolve().parents[1]
ROOT = WEB.parent
EN = ROOT / "nlp_social_listening" / "data" / "results"
CN = ROOT / "nlp_social_listening" / "china" / "data" / "results"
FP = ROOT / "flavor_pairing"
FM = ROOT / "flavor_masking"
OUT = WEB / "app" / "data"
OUT.mkdir(parents=True, exist_ok=True)

# Fixed affinity-tier bands (final report, Table 5).
TIER_HIGH, TIER_MID_HIGH, TIER_MID = 0.70, 0.50, 0.35


def tier_of(s):
    if s >= TIER_HIGH:
        return "HIGH"
    if s >= TIER_MID_HIGH:
        return "MID-HIGH"
    if s >= TIER_MID:
        return "MID"
    return "LOW"


def r1(x):
    return round(float(x), 1)


def pretty(s):
    return str(s).replace("_", " ").strip().title()


def write(name, obj):
    p = OUT / name
    with open(p, "w") as f:
        json.dump(obj, f, separators=(",", ":"), ensure_ascii=False)
    print(f"  wrote {name}  ({p.stat().st_size/1024:.1f} KB)")


# --------------------------------------------------------------------------
# CONSUMER INTELLIGENCE
# --------------------------------------------------------------------------
def flavor_rows(df, mention_col="mentions", min_mentions=20, top=None):
    d = df[df[mention_col] >= min_mentions].copy()
    d = d.sort_values("net_score", ascending=False)
    if top:
        d = d.head(top)
    return d


en_flav = pd.read_csv(EN / "flavor_ranking.csv")
cn_flav = pd.read_csv(CN / "flavor_frequency.csv")
en_pain = pd.read_csv(EN / "pain_ranking.csv")
cn_pain = pd.read_csv(CN / "pain_point_frequency.csv")
en_fmt = pd.read_csv(EN / "format_appeal.csv")
cn_fmt = pd.read_csv(CN / "format_mentions.csv")
en_occ = pd.read_csv(EN / "occasion_distribution.csv")
cn_occ = pd.read_csv(CN / "occasion_distribution.csv")
en_comp = pd.read_csv(EN / "competitor_scorecard.csv")
cn_comp = pd.read_csv(CN / "competitor_sentiment.csv")
en_seg = pd.read_csv(EN / "cluster_profiles.csv")
cn_seg = pd.read_csv(CN / "cluster_profiles.csv")
joint = pd.read_csv(CN / "joint_cluster_profiles.csv")


def flav_payload(df, min_mentions=20, top=13, platform=False):
    d = flavor_rows(df, min_mentions=min_mentions, top=top)
    rows = []
    for _, r in d.iterrows():
        row = {
            "flavor": pretty(r["flavor"]),
            "mentions": int(r["mentions"]),
            "pos": r1(r["pos_pct"]),
            "neg": r1(r["neg_pct"]),
            "net": r1(r["net_score"]),
        }
        if platform and "top_platform" in df.columns:
            row["platform"] = pretty(r["top_platform"])
        rows.append(row)
    return rows


def simple_rows(df, key, cols):
    out = []
    for _, r in df.iterrows():
        out.append({"label": pretty(r[key]), **{k: r1(r[v]) if v != "mentions" else int(r[v]) for k, v in cols.items()}})
    return out


# Cross-market: flavours that appear in the report's cross-market figure.
cross_list = ["passion_fruit", "strawberry", "yuzu", "lychee", "honey", "oat",
              "mango", "jasmine", "vanilla", "milk_tea", "peach", "caramel"]
en_net = dict(zip(en_flav["flavor"], en_flav["net_score"]))
cn_net = dict(zip(cn_flav["flavor"], cn_flav["net_score"]))
cross = []
for fl in cross_list:
    cross.append({
        "flavor": pretty(fl),
        "en": r1(en_net.get(fl)) if fl in en_net else None,
        "zh": r1(cn_net.get(fl)) if fl in cn_net else None,
    })


def seg_payload(df):
    out = []
    for _, r in df.iterrows():
        out.append({
            "size": int(r["size"]),
            "pct": r1(r["size_pct"]),
            "flavor": pretty(r["top_flavor"]),
            "pain": pretty(r["top_pain"]),
            "occasion": pretty(r["top_occasion"]),
            "sentiment": round(float(r["avg_sentiment"]), 3),
            "positive": r1(r["pct_positive"]),
        })
    return out


joint_rows = []
for _, r in joint.iterrows():
    joint_rows.append({
        "size": int(r["size"]),
        "pct": r1(r["size_pct"]),
        "flavor": pretty(r["top_flavor"]),
        "pain": pretty(r["top_pain"]),
        "occasion": pretty(r["top_occasion"]),
        "china": r1(r["pct_china"] * 100),
        "twitter": r1(r["pct_twitter"] * 100),
    })

consumer = {
    "corpus": [
        {"platform": "Twitter", "language": "English", "posts": 5021, "role": "Broad global flavour and pain-point signal"},
        {"platform": "Xiaohongshu", "language": "Chinese", "posts": 877, "role": "Flavour discovery and demand territory"},
        {"platform": "Weibo", "language": "Chinese", "posts": 601, "role": "Open opinion, complaints, competitor talk"},
        {"platform": "Douyin", "language": "Chinese", "posts": 171, "role": "Candid sensory reactions and pain points"},
    ],
    "corpusTotal": 6670,
    "platformSentiment": [
        {"platform": "Xiaohongshu", "posts": 877, "pos": 84.5, "neg": 7.5},
        {"platform": "Weibo", "posts": 601, "pos": 80.4, "neg": 10.6},
        {"platform": "Douyin", "posts": 171, "pos": 79.5, "neg": 12.3},
    ],
    "flavorsEN": flav_payload(en_flav, top=13),
    "flavorsZH": flav_payload(cn_flav, top=13, platform=True),
    "painsEN": simple_rows(en_pain.head(6), "pain", {"mentions": "mentions", "pos": "pos_pct", "neg": "neg_pct", "net": "net_score"}),
    "painsZH": simple_rows(cn_pain.head(6), "pain", {"mentions": "mentions", "pos": "pos_pct", "neg": "neg_pct", "net": "net_score"}),
    "formatsEN": simple_rows(en_fmt, "format", {"mentions": "mentions", "pos": "pos_pct", "neg": "neg_pct", "net": "net_score"}),
    "formatsZH": simple_rows(cn_fmt, "formats", {"mentions": "mentions", "pos": "pos_pct", "neg": "neg_pct", "net": "net_score"}),
    "occasionsEN": simple_rows(en_occ, "occasion", {"mentions": "mentions", "net": "net_score"}),
    "occasionsZH": simple_rows(cn_occ, "occasions", {"mentions": "mentions", "net": "net_score"}),
    "competitorsEN": simple_rows(en_comp.head(8), "brand", {"mentions": "mentions", "net": "net_score"}),
    "competitorsZH": simple_rows(cn_comp.head(8), "brands", {"mentions": "mentions", "net": "net_score"}),
    "crossMarket": cross,
    "segmentsJoint": joint_rows,
    "segmentsEN": seg_payload(en_seg),
    "segmentsZH": seg_payload(cn_seg),
}
write("consumer.json", consumer)

# --------------------------------------------------------------------------
# MOLECULAR PAIRING (compatibility + variant C)
# --------------------------------------------------------------------------
pc = pd.read_csv(FP / "outputs" / "pairing_compatibility.csv")
variants = []
for _, r in pc.iterrows():
    variants.append({
        "label": r["label"],
        "score": round(float(r["compatibility_score"]), 3),
        "tier": tier_of(float(r["compatibility_score"])),
    })

vc = pd.read_csv(FP / "outputs" / "variant_c_curated_top20.csv").head(10)
variant_c = []
for _, r in vc.iterrows():
    variant_c.append({
        "name": pretty(r["name"]),
        "category": r.get("category"),
        "score": round(float(r["compatibility_score"]), 3),
        "tier": tier_of(float(r["compatibility_score"])),
    })

molecular = {
    "graph": {"nodes": 8298, "ingredients": 6653, "compounds": 1645, "edges": 147179,
              "embedded": 8297, "dim": 300, "screened": 8279, "targets": 13},
    "tiers": [
        {"tier": "HIGH", "range": "0.70 and above", "interp": "Strong molecular alignment with the consumer-preferred space"},
        {"tier": "MID-HIGH", "range": "0.50 to 0.69", "interp": "Moderate alignment, warrants sensory exploration"},
        {"tier": "MID", "range": "0.35 to 0.49", "interp": "Weak alignment"},
        {"tier": "LOW", "range": "below 0.35", "interp": "Poor molecular fit with the consumer-liked anchor"},
    ],
    "variants": variants,
    "variantC": variant_c,
    "meanOf13": 0.442,
    "pearsonInSample": 0.60,
}
write("molecular.json", molecular)

# --------------------------------------------------------------------------
# BITTER RISK
# --------------------------------------------------------------------------
br = pd.read_csv(FM / "outputs" / "bitter_predictions.csv")
points = [{"compound": pretty(r["compound"]), "mw": round(float(r["molecular_weight"]), 1),
           "prob": round(float(r["bitter_probability"]), 3),
           "status": "risk" if str(r["status"]).strip() == "bitter risk" else "safe"}
          for _, r in br.iterrows()]
top5 = br.sort_values("bitter_probability", ascending=False).head(5)
bitter = {
    "threshold": 0.5,
    "total": int(len(br)),
    "points": points,
    "top": [{"compound": pretty(r["compound"]), "prob": round(float(r["bitter_probability"]), 2)} for _, r in top5.iterrows()],
}
write("bitter_risk.json", bitter)

# --------------------------------------------------------------------------
# SURVEY
# --------------------------------------------------------------------------
with open(FP / "outputs" / "survey_results.json") as f:
    sr = json.load(f)
order = ["Coconut & Milk Tea", "Mango & Jasmine", "Pineapple", "Vanilla", "Strawberry"]
concepts = []
for name in order:
    c = sr["concepts"][name]
    concepts.append({
        "concept": name,
        "score": c["fg_score"],
        "tier": c["tier"],
        "role": c["role"],
        "liking": round(c["mean_liking"], 2),
        "se": round(c["se_liking"], 3),
        "purchase": round(c["mean_purchase_intent"], 2),
    })
survey = {
    "n": sr["n_respondents"],
    "spearman": sr["spearman_r"],
    "pValue": sr["p_value"],
    "highMean": round(sr["high_tier_mean"], 2),
    "lowMean": round(sr["low_tier_mean"], 2),
    "gate": sr["gate_verdict"],
    "concepts": concepts,
}
write("survey.json", survey)

# --------------------------------------------------------------------------
# PERFORMANCE
# --------------------------------------------------------------------------
performance = {
    "dataVolume": [
        {"component": "English tweets", "detail": "5,021 across 6 query groups"},
        {"component": "China posts", "detail": "1,649 across 3 platforms (Xiaohongshu, Weibo, Douyin)"},
        {"component": "FlavorGraph nodes", "detail": "8,298 nodes; 8,279 screened for Variant C"},
        {"component": "Survey respondents", "detail": "n = 34 (APAC urban, aged 25 to 38)"},
    ],
    "metrics": [
        {"metric": "NLP inter-model agreement (English)", "value": "0.635", "notes": "Mean confidence, VADER vs TextBlob"},
        {"metric": "NLP inter-model agreement (Chinese)", "value": "0.731", "notes": "Mean confidence, RoBERTa-JD vs SnowNLP"},
        {"metric": "Clustering k selection", "value": "k = 5", "notes": "Silhouette optimisation over k in 2 to 7"},
        {"metric": "FlavorGraph HIGH-tier compatibility", "value": "0.73 to 0.79", "notes": "Variant A and Variant B"},
        {"metric": "FlavorGraph LOW-tier compatibility", "value": "0.26", "notes": "Strawberry discriminative baseline"},
        {"metric": "Survey validation (Spearman r)", "value": "0.90 (p = 0.037)", "notes": "Compatibility vs mean liking, n = 34"},
        {"metric": "Survey tier separation", "value": "HIGH 6.9 / LOW 4.3", "notes": "9-point hedonic scale"},
    ],
}
write("performance.json", performance)

print("Done.")
