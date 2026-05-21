"""
01 - Load FlavorGraph assets, scan node availability for MoBai-relevant ingredients.

Outputs:
- data/mobai_target_nodes.csv: curated mapping MoBai flavor -> FlavorGraph node + strategy
- Prints summary stats to stdout
"""
import pickle
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path("__file__" in globals() and __file__ or "notebooks/dummy.py").resolve().parents[1] if "__file__" in globals() else Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA = ROOT / "data"

# Load embeddings
with open(DATA / "flavorgraph_embeddings.pickle", "rb") as f:
    emb = pickle.load(f)
print(f"Loaded embeddings: {len(emb)} nodes, dim={next(iter(emb.values())).shape[0]}")

# Load node metadata
nodes = pd.read_csv(DATA / "nodes_191120.csv")
print(f"Loaded node list: {len(nodes)} rows, columns={list(nodes.columns)}")
print(f"Node types: {nodes['node_type'].value_counts().to_dict()}")
print(f"Hub status: {nodes['is_hub'].value_counts().to_dict()}")

# Build lookup: name -> node_id (note: node_id in CSV is int, in pickle is str)
nodes['node_id_str'] = nodes['node_id'].astype(str)
name_to_id = dict(zip(nodes['name'], nodes['node_id_str']))

# Search for MoBai-relevant flavors (from NLP Q1 + product spec)
mobai_search_terms = {
    # NLP Q1 chart flavors (13 total)
    "mango": ["mango", "fresh_mango", "dried_mango"],
    "vanilla": ["vanilla", "vanilla_extract", "vanilla_bean"],
    "caramel": ["caramel", "caramel_sauce"],
    "coconut": ["coconut", "coconut_milk", "coconut_cream", "coconut_water"],
    "chocolate": ["chocolate", "dark_chocolate", "milk_chocolate"],
    "milk_tea": ["milk_tea", "bubble_tea"],  # likely missing
    "oat": ["oat", "oats", "rolled_oats", "oatmeal"],
    "coffee": ["coffee", "brewed_coffee", "instant_coffee"],
    "banana": ["banana", "ripe_banana"],
    "matcha": ["matcha", "green_tea_powder"],
    "peach": ["peach", "fresh_peach", "canned_peach", "dried_peach"],
    "honey": ["honey"],
    "strawberry": ["strawberry", "fresh_strawberry"],
    # MoBai product spec
    "jasmine": ["jasmine", "jasmine_tea", "jasmine_flower"],
    "black_tea": ["black_tea", "brewed_black_tea"],
    "oolong": ["oolong", "oolong_tea"],
    "milk": ["milk", "whole_milk", "skim_milk", "low_fat_milk"],
    "yogurt": ["yogurt", "plain_yogurt", "greek_yogurt"],
    "tea": ["tea", "brewed_tea", "green_tea", "brewed_green_tea"],
    # Compound proxies for jasmine
    "benzyl_acetate": ["benzyl_acetate"],
    "linalool": ["linalool"],
    "methyl_jasmonate": ["methyl_jasmonate"],
    # Variant C candidates (per MoBai Section 4.1)
    "osmanthus": ["osmanthus"],
    "white_peach": ["white_peach"],
    "lychee": ["lychee", "lychee_fruit"],
    "passionfruit": ["passionfruit", "passion_fruit"],
}

results = []
for mobai_term, candidates in mobai_search_terms.items():
    found = []
    for c in candidates:
        # Exact match
        if c in name_to_id and name_to_id[c] in emb:
            found.append((c, name_to_id[c], "exact"))
        # Substring match
        else:
            matches = nodes[nodes['name'].str.contains(c, case=False, na=False)]
            for _, row in matches.head(5).iterrows():
                nid = str(row['node_id'])
                if nid in emb:
                    found.append((row['name'], nid, "substring"))
    results.append({
        "mobai_term": mobai_term,
        "matches": "; ".join([f"{n}({i})" for n, i, _ in found[:5]]) if found else "NONE",
        "count": len(found),
        "status": "FOUND" if found else "MISSING",
    })

results_df = pd.DataFrame(results)
print("\n=== MoBai Node Availability ===")
for _, row in results_df.iterrows():
    print(f"  [{row['status']:7s}] {row['mobai_term']:20s} ({row['count']} matches): {row['matches'][:120]}")

# Build canonical mapping: choose primary node per MoBai term
canonical_map = {
    # Direct hits (verified against actual node names)
    "mango":        ("fresh_mango", "direct"),
    "vanilla":      ("vanilla", "direct"),
    "caramel":      ("caramel", "direct"),
    "coconut":      ("coconut", "direct"),
    "chocolate":    ("chocolate", "direct"),
    "oat":          ("oat", "direct"),
    "coffee":       ("coffee", "direct"),
    "banana":       ("banana", "direct"),
    "matcha":       ("matcha_green_tea_powder", "direct"),
    "peach":        ("canned_peach", "direct"),
    "honey":        ("honey", "direct"),
    "strawberry":   ("strawberry", "direct"),
    "black_tea":    ("black_tea", "direct"),
    "milk":         ("milk", "direct"),
    "yogurt":       ("yogurt", "direct"),
    "jasmine":      ("jasmine_tea", "direct"),                    # FOUND in full data
    # Compound proxies
    "milk_tea":     ("black_tea+milk", "compound_proxy"),         # not a single node, average
    # Additional jasmine aromatic compounds (alternative for sensitivity check)
    "jasmine_compound_BA": ("Benzyl_Acetate", "compound_proxy"),  # primary jasmine ester
    "jasmine_compound_lin": ("Linalool", "compound_proxy"),
    "jasmine_compound_lactone": ("Jasmine_lactone", "compound_proxy"),
    # Variant C candidates (verified present)
    "white_peach":  ("white_peach", "variant_c"),
    "lychee":       ("lychee", "variant_c"),
    "passionfruit": ("passion_fruit", "variant_c"),
    # Confirmed missing
    "oolong":       (None, "missing"),
    "osmanthus":    (None, "missing"),
}

# Verify each canonical mapping exists
out_rows = []
for term, (target, strategy) in canonical_map.items():
    if target is None:
        out_rows.append({"mobai_term": term, "flavorgraph_node": "", "node_id": "", "strategy": strategy, "in_embeddings": False})
        continue
    if "+" in target:
        # Compound proxy - verify each part
        parts = target.split("+")
        all_present = all(name_to_id.get(p) in emb for p in parts)
        out_rows.append({
            "mobai_term": term, "flavorgraph_node": target, "node_id": "+".join(name_to_id.get(p, "?") for p in parts),
            "strategy": strategy, "in_embeddings": all_present,
        })
    else:
        nid = name_to_id.get(target)
        in_emb = nid in emb if nid else False
        out_rows.append({
            "mobai_term": term, "flavorgraph_node": target, "node_id": nid or "",
            "strategy": strategy, "in_embeddings": in_emb,
        })

target_df = pd.DataFrame(out_rows)
target_df.to_csv(DATA / "mobai_target_nodes.csv", index=False)
print(f"\n=== Saved canonical mapping ===")
print(target_df.to_string(index=False))
print(f"\nWritten to: {DATA / 'mobai_target_nodes.csv'}")
