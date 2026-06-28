# KSF Consumer Intelligence — China (NLP Social Listening)

**Total posts analyzed:** 1649 across 3 platforms

## Methodology — volume & sentiment per platform

| platform    |   posts |   pct_positive |   pct_negative |   avg_sentiment |
|:------------|--------:|---------------:|---------------:|----------------:|
| douyin      |     171 |           79.5 |           12.3 |        0.576289 |
| weibo       |     601 |           80.4 |           10.6 |        0.6938   |
| xiaohongshu |     877 |           84.5 |            7.5 |        0.707356 |

## Q1 — Top flavors by net sentiment

| flavor        |   mentions |   pos_pct |   neg_pct |   net_score |
|:--------------|-----------:|----------:|----------:|------------:|
| passion_fruit |         22 |   95.4545 |   0       |     95.4545 |
| strawberry    |        109 |   94.4954 |   1.83486 |     92.6606 |
| yuzu          |         27 |   92.5926 |   0       |     92.5926 |
| lychee        |         49 |   91.8367 |   0       |     91.8367 |
| honey         |         24 |   91.6667 |   0       |     91.6667 |
| oat           |        177 |   92.6554 |   1.12994 |     91.5254 |
| mango         |         90 |   93.3333 |   3.33333 |     90      |
| jasmine       |         75 |   93.3333 |   4       |     89.3333 |

## Q3 — Top sensory pain points

| pain        |   mentions |   severity |   pain_score |
|:------------|-----------:|-----------:|-------------:|
| bad_smell   |         76 |         -0 |           -0 |
| expensive   |         74 |         -0 |           -0 |
| too_sweet   |         59 |         -0 |           -0 |
| chalky      |         19 |         -0 |           -0 |
| not_filling |         18 |         -0 |           -0 |
| artificial  |         12 |         -0 |           -0 |

## Q4 — Format appetite (net sentiment)

| formats      |   mentions |   net_score |
|:-------------|-----------:|------------:|
| powder       |        553 |     68.1736 |
| shake        |        164 |     89.0244 |
| RTD_liquid   |         57 |     94.7368 |
| yogurt_drink |         25 |     72      |
| jelly        |         16 |     87.5    |

## Q5 — Occasion distribution

| occasions        |   mentions |   net_score |
|:-----------------|-----------:|------------:|
| morning          |        293 |     83.6177 |
| snack            |        241 |     90.0415 |
| work             |        143 |     88.8112 |
| meal_replacement |        136 |     79.4118 |
| post_workout     |         96 |     91.6667 |
| commute          |         30 |     96.6667 |

## Q6 — Competitor sentiment

| brands         |   mentions |   pos_pct |   neg_pct |   net_score |
|:---------------|-----------:|----------:|----------:|------------:|
| Mengniu        |         44 |   81.8182 |   6.81818 |     75      |
| Jianchun       |         43 |   95.3488 |   0       |     95.3488 |
| Yili Ambrosial |         41 |   85.3659 |   0       |     85.3659 |
| Yakult         |         19 |   89.4737 |   5.26316 |     84.2105 |
| Ensure         |         12 |  100      |   0       |    100      |
| Master Kong    |          7 |  100      |   0       |    100      |
| Fairlife       |          5 |   80      |   0       |     80      |
| Wahaha         |          4 |   75      |   0       |     75      |
| Nongfu         |          2 |  100      |   0       |    100      |
| Oikos          |          1 |  100      |   0       |    100      |

## Consumer segments (K-means)

|   cluster |   size_pct | label                             | top_flavor   | top_pain    | top_occasion   |   avg_sentiment |
|----------:|-----------:|:----------------------------------|:-------------|:------------|:---------------|----------------:|
|         4 |       31.4 | Morning / Coffee / (expensive)    | coffee       | expensive   | morning        |           0.538 |
|         0 |       30.7 | Morning / Milk_Tea / (bad_smell)  | milk_tea     | bad_smell   | morning        |           0.857 |
|         2 |       15.4 | Snack / Oat / (not_filling)       | oat          | not_filling | snack          |           0.861 |
|         5 |       12.1 | Snack / Oat / (expensive)         | oat          | expensive   | snack          |           0.802 |
|         1 |        8.5 | Morning / Chocolate / (too_sweet) | chocolate    | too_sweet   | morning        |           0.265 |
|         3 |        1.9 | Morning / Coconut / (expensive)   | coconut      | expensive   | morning        |           0.243 |