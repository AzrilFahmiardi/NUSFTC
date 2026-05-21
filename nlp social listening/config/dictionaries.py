"""
Entity dictionaries — English-only, derived from KSF brief section 6 step 3.
Lowercased substring matching against tweet text.
"""

FLAVOR_DICT = {
    "matcha":        ["matcha", "green tea latte"],
    "coconut":       ["coconut", "coconut milk"],
    "mango":         ["mango"],
    "strawberry":    ["strawberry"],
    "lychee":        ["lychee"],
    "peach":         ["peach", "white peach"],
    "taro":          ["taro"],
    "red_bean":      ["red bean", "azuki"],
    "chocolate":     ["chocolate", "choco", "cocoa"],
    "vanilla":       ["vanilla"],
    "coffee":        ["coffee", "latte", "mocha", "espresso"],
    "black_sesame":  ["black sesame", "sesame"],
    "osmanthus":     ["osmanthus"],
    "jasmine":       ["jasmine"],
    "milk_tea":      ["milk tea", "boba", "bubble tea"],
    "oat":           ["oat", "oatmeal"],
    "banana":        ["banana"],
    "passion_fruit": ["passion fruit", "passionfruit"],
    "yuzu":          ["yuzu"],
    "honey":         ["honey"],
    "caramel":       ["caramel"],
}

PAIN_DICT = {
    "chalky":      ["chalky", "chalk"],
    "too_sweet":   ["too sweet", "overly sweet", "way too sweet", "sugar bomb"],
    "aftertaste":  ["aftertaste", "lingering", "weird taste after"],
    "artificial":  ["artificial", "fake taste", "plastic taste", "chemical taste"],
    "too_thick":   ["too thick", "heavy", "thick texture"],
    "beany":       ["beany", "soy taste", "plant protein taste"],
    "metallic":    ["metallic", "iron taste", "metal taste"],
    "grainy":      ["grainy", "gritty", "powdery"],
    "bad_smell":   ["bad smell", "off smell", "stinks", "smells bad"],
    "expensive":   ["expensive", "pricey", "too expensive", "overpriced"],
    "not_filling": ["hungry after", "not filling", "still hungry"],
}

OCCASION_DICT = {
    "morning":          ["morning", "breakfast", "wake up", "before work", "am routine"],
    "post_workout":     ["post workout", "after gym", "after workout", "post-gym", "recovery"],
    "meal_replacement": ["meal replacement", "skip meal", "instead of breakfast", "instead of lunch"],
    "snack":            ["snack", "afternoon snack", "midafternoon"],
    "commute":          ["commute", "on the go", "on-the-go", "in the car"],
    "work":             ["office", "at work", "work from home", "wfh", "desk"],
}

FORMAT_DICT = {
    "yogurt_drink":  ["yogurt drink", "drinkable yogurt", "yogurt smoothie", "kefir"],
    "shake":         ["shake", "protein shake"],
    "RTD_liquid":    ["rtd", "ready to drink", "bottled protein", "ready-to-drink"],
    "powder":        ["protein powder", "powder mix"],
    "jelly":         ["jelly drink", "protein jelly", "pudding"],
}

BRAND_DICT = {
    "Fairlife":         ["fairlife"],
    "Premier Protein":  ["premier protein"],
    "Muscle Milk":      ["muscle milk"],
    "Oikos":            ["oikos"],
    "Ensure":           ["ensure"],
    "Danone":           ["danone"],
    "Yili Ambrosial":   ["yili", "ambrosial"],
    "Activia":          ["activia"],
    "Yakult":           ["yakult"],
    "Master Kong":      ["master kong", "ksf", "kang shi fu"],
    "Core Power":       ["core power"],
    "Owyn":             ["owyn"],
    "Orgain":           ["orgain"],
}

# For Q2 APAC tagging — substrings searched in tweet text (lowercased)
REGION_HINT_DICT = {
    "APAC": [
        "singapore", "malaysia", "philippines", "indonesia", "vietnam",
        "thailand", "japan", "korea", "taiwan", "hong kong", "china",
        "asia", "asian", "sea ", "apac", "manila", "jakarta", "kuala lumpur",
        " kl ", "bangkok", "tokyo", "seoul", "shanghai", "beijing",
        "ho chi minh", "saigon",
    ],
    "Global": [],  # fallback if no APAC hint
}
