import pandas as pd
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from analysis.aspect_analyzer import AspectAnalyzer
from analysis.keyword_extractor import KeywordExtractor

def main():
    df = pd.read_csv("data/processed/absa_data.csv")
    
    # Parse JSON strings back to objects
    import ast
    df["aspect_details"] = df["aspect_details"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    analyzer = AspectAnalyzer()
    matrix = analyzer.get_aspect_sentiment_matrix(df)
    pain = analyzer.get_pain_point_hierarchy(df)
    
    ext = KeywordExtractor()
    kw = ext.extract_complaint_keywords(df)

    print("=== DISTRIBUSI SENTIMEN KESELURUHAN ===")
    print(df["consensus_label"].value_counts(normalize=True) * 100)
    print("\n")

    print("=== MATRIKS SENTIMEN BERDASARKAN ASPEK (ASPECT-BASED) ===")
    print(matrix.to_string())
    print("\n")

    print("=== HIERARKI PAIN POINTS KONSUMEN (URUTAN PRIORITAS MASALAH) ===")
    print(pain.to_string())
    print("\n")

    print("=== TOP 10 KATA KUNCI KELUHAN (COMPLAINT KEYWORDS) ===")
    print(kw[["keyword", "complaint_ratio"]].head(10).to_string())

if __name__ == "__main__":
    main()
