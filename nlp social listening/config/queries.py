"""
Twitter search queries — English-only, mapped to brief questions Q1–Q6.

Each group ~10–15 queries × ~200 tweets/query target.
After dedup + filters, target ~2,000–3,000 clean tweets.
"""

# Q1 — Flavor preferences
QUERIES_FLAVOR = [
    "matcha protein drink",
    "mango protein shake review",
    "coconut protein drink",
    "strawberry protein shake",
    "chocolate protein drink review",
    "vanilla protein shake taste",
    "taro protein drink",
    "lychee protein shake",
    "peach protein drink",
    "best flavor protein drink",
    "protein drink fruity flavor",
    "protein shake flavor ranking",
    "tropical protein drink",
    "milk tea protein drink",
    "oat protein drink",
]

# Q2 — Morning routine
QUERIES_MORNING = [
    "protein drink morning routine",
    "breakfast protein shake",
    "skip breakfast protein drink",
    "morning protein habit",
    "protein drink before work",
    "on the go breakfast protein",
    "protein shake instead of breakfast",
    "office protein drink",
    "busy morning protein",
    "protein drink commute",
    "wake up protein shake",
    "healthy morning protein",
]

# Q3 — Pain points / sensory rejection
QUERIES_PAIN = [
    "protein shake chalky",
    "protein drink too sweet",
    "protein shake aftertaste",
    "protein drink artificial taste",
    "protein shake too thick",
    "protein drink tastes bad",
    "worst protein shake",
    "protein drink metallic taste",
    "protein shake gritty",
    "protein drink weird smell",
    "protein shake disgusting",
    "protein drink hard to drink",
]

# Q4 — Yogurt drink format appetite
QUERIES_YOGURT_DRINK = [
    "drinkable yogurt protein",
    "protein yogurt drink",
    "high protein yogurt drink",
    "Oikos protein shake review",
    "Activia protein drink",
    "yogurt drink breakfast",
    "drinkable yogurt review",
    "yogurt protein RTD",
    "kefir protein drink",
    "yogurt drink high protein",
    "drinkable yogurt morning",
    "yogurt smoothie protein",
]

# Q5 — Other consumption occasions
QUERIES_OCCASION = [
    "post workout protein shake",
    "meal replacement protein drink",
    "afternoon protein snack",
    "protein drink after gym",
    "protein shake snack",
    "protein drink work from home",
    "protein shake on the go",
    "evening protein drink",
    "protein drink between meals",
    "protein shake recovery",
]

# Q6 — Competitor brand mentions
QUERIES_COMPETITOR = [
    "Fairlife protein shake review",
    "Premier Protein review",
    "Muscle Milk review",
    "Ensure protein drink review",
    "Oikos protein shake",
    "Yili Ambrosial protein",
    "Activia protein review",
    "Yakult protein",
    "Danone protein yogurt",
    "Master Kong protein",
    "protein drink brand comparison",
    "best protein drink brand",
]

QUERY_GROUPS = {
    "flavor":     QUERIES_FLAVOR,
    "morning":    QUERIES_MORNING,
    "pain":       QUERIES_PAIN,
    "yogurt":     QUERIES_YOGURT_DRINK,
    "occasion":   QUERIES_OCCASION,
    "competitor": QUERIES_COMPETITOR,
}

ALL_QUERIES = [q for group in QUERY_GROUPS.values() for q in group]
