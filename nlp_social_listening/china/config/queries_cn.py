"""
Chinese search queries — ported from reference brief (nlp_social_listening_2.md):
  SET A1–A6 → Xiaohongshu, SET B → Weibo, SET E → Douyin.

Mapped to the SAME six group names the sibling English pipeline uses
(flavor / morning / pain / yogurt / occasion / competitor) so that
`query_group`-based analysis code runs unchanged. A1 (general) folds into `flavor`.
"""

# ── XIAOHONGSHU (小红书) — SET A, by group ──────────────────────────
XHS_FLAVOR = [           # A1 general + A2 flavor discovery
    "蛋白质饮料推荐", "高蛋白饮品 好喝", "蛋白奶昔 口味", "蛋白质饮料 测评",
    "蛋白饮品 哪个好", "乳清蛋白饮料 推荐",
    "蛋白质饮料 口味推荐", "抹茶 蛋白饮料", "椰子 蛋白饮料", "芒果 蛋白饮料",
    "草莓 蛋白饮料", "蛋白饮品 水果味", "荔枝 蛋白饮品", "桃子 蛋白饮品",
    "红豆 蛋白饮品", "芋头 蛋白饮品", "巧克力 蛋白饮品", "香草 蛋白饮品",
    "燕麦 蛋白饮品", "蛋白质饮料 好喝的味道",
]

XHS_YOGURT = [           # A3 yogurt drink flavor discovery
    "酸奶饮料 口味推荐", "喝的酸奶 什么味道好", "高蛋白酸奶饮品 好喝",
    "乳酸菌饮料 口味", "酸奶饮品 测评", "蛋白酸奶饮料 哪个好",
    "酸奶饮料 早餐", "喝的酸奶 蛋白", "安慕希 口味 推荐", "简醇 酸奶 口味",
    "益力多 评测", "喝的酸奶 新口味", "抹茶酸奶 好喝吗", "椰子酸奶饮品", "芒果酸奶饮品",
]

XHS_PAIN = [             # A4 pain points / sensory rejection
    "蛋白质饮料 难喝", "蛋白奶昔 腥味", "蛋白饮品 甜腻", "蛋白质饮料 口感差",
    "代餐饮料 缺点", "蛋白质饮料 后味", "蛋白饮料 不好喝", "蛋白粉 腥味怎么办",
    "蛋白质饮料 太甜", "蛋白饮品 粉感",
]

XHS_MORNING = [          # A5 morning / occasion
    "早餐 蛋白饮品", "上班路上 代餐", "早上喝什么好", "健康早餐 饮料",
    "忙碌早晨 营养", "便携早餐 饮品", "没时间吃早饭", "早晨代替早餐 饮料",
    "上班前 喝什么", "早餐饮品推荐",
]

XHS_COMPETITOR = [       # A6 competitive products
    "安慕希 高蛋白 测评", "简醇 蛋白 口味", "Fairlife 体验", "肌肉牛奶 测评",
    "雅培 营养素 口感", "佳倍有方 蛋白", "Ensure 蛋白奶昔", "蛋白饮料 哪个牌子好",
    "康师傅 蛋白饮料", "中国 高蛋白饮料 推荐",
]

# occasion group: pull the workout/meal-replacement cuts out of the general pool
XHS_OCCASION = [
    "健身后 蛋白饮料", "运动后 蛋白补充", "代餐 蛋白质 减脂", "蛋白质 加餐",
    "蛋白饮品 下午茶", "训练后 蛋白饮料",
]

XHS_GROUPS = {
    "flavor":     XHS_FLAVOR,
    "yogurt":     XHS_YOGURT,
    "pain":       XHS_PAIN,
    "morning":    XHS_MORNING,
    "occasion":   XHS_OCCASION,
    "competitor": XHS_COMPETITOR,
}

# ── WEIBO (微博) — SET B (topics + hashtags) ────────────────────────
WEIBO_TOPICS = [
    "蛋白质饮料 推荐", "高蛋白饮品 口感", "代餐奶昔 测评", "蛋白质 早餐",
    "健身饮料 味道", "乳清蛋白 饮料", "蛋白饮料 测评", "功能饮料 蛋白",
    "蛋白质 早晨", "蛋白饮品 新品",
]
WEIBO_HASHTAGS = [       # Weibo search format: #keyword#
    "#高蛋白饮食#", "#代餐减肥#", "#健身饮食#", "#蛋白质补充#", "#早餐代餐#",
    "#减脂餐#", "#运动营养#", "#健康饮料推荐#", "#蛋白质饮料#", "#高蛋白早餐#",
]

# group mapping for Weibo terms (best-effort; refined in normalize via KEYWORD_TO_GROUP).
# Pain + competitor weighted: XHS (种草 platform) already covers flavor/demand but buries
# complaints, so the Weibo budget concentrates on pain points and competitor sentiment —
# the signal these platforms add that XHS lacks. Flavor/morning/occasion kept light.
#
# IMPORTANT: Weibo full-text search is noisy — keywords MUST be compact whole phrases with
# NO SPACES (smoke test: "蛋白饮料难喝" → 5/5 on-topic; "蛋白饮品 太甜" with a space →
# off-topic diet posts; "高蛋白饮料难喝" too long → 0 results). A relevance filter in
# notebook 02 drops any residual rows that don't mention a protein/drink core term.
WEIBO_GROUPS = {
    "flavor":     ["蛋白饮料推荐", "高蛋白饮料",
                   # volume expansion — flavour territory (compact, no-space)
                   "抹茶蛋白饮料", "椰子蛋白饮料", "芒果蛋白饮料", "草莓蛋白饮料",
                   "巧克力蛋白饮料", "燕麦蛋白饮品", "蛋白奶昔好喝"],
    "morning":    ["蛋白质早餐", "早餐蛋白饮料"],
    "occasion":   ["健身蛋白饮料", "减脂蛋白饮料", "运动后蛋白补充"],
    "pain":       ["蛋白饮料难喝", "蛋白粉腥味", "蛋白粉难喝",
                   "蛋白奶昔难喝", "代餐难喝", "蛋白饮料太甜",
                   # more pain phrasings (texture/aftertaste/additives)
                   "蛋白粉颗粒感", "蛋白饮料齁甜", "蛋白粉沙感",
                   "蛋白饮料后味重", "蛋白饮料添加剂"],
    "yogurt":     ["高蛋白酸奶难喝", "高蛋白酸奶推荐", "酸奶饮料好喝"],
    "competitor": ["安慕希好喝吗", "简醇蛋白", "安慕希测评", "Fairlife",
                   # more competitor brands (Yili/Mengniu ecosystem + premium yogurt)
                   "蒙牛蛋白", "伊利蛋白饮料", "卡士酸奶", "北海牧场", "乐纯酸奶"],
}

# ── DOUYIN (抖音) — SET E (hashtags) ────────────────────────────────
DOUYIN_HASHTAGS = [
    "#蛋白质饮料", "#高蛋白饮品", "#代餐饮料测评", "#健身饮食", "#早餐代餐",
    "#蛋白奶昔", "#减脂饮食", "#功能性饮料", "#蛋白质早餐", "#高蛋白零食",
]
# Pain + competitor weighted (same rationale as Weibo). Douyin search strips the
# leading '#', so plain-text pain/competitor terms search fine alongside hashtags.
DOUYIN_GROUPS = {
    "flavor":     ["#蛋白质饮料", "#蛋白奶昔",
                   "抹茶蛋白饮料", "椰子蛋白饮料", "巧克力蛋白饮料"],
    "morning":    ["#早餐代餐"],
    "occasion":   ["#健身饮食", "#代餐饮料测评", "减脂蛋白饮料"],
    "pain":       ["蛋白饮料难喝", "蛋白粉腥味", "代餐难喝", "蛋白饮料太甜",
                   "蛋白粉颗粒感", "蛋白饮料齁甜"],
    "yogurt":     ["高蛋白酸奶难喝", "高蛋白酸奶推荐"],
    "competitor": ["安慕希", "简醇", "Fairlife", "蒙牛蛋白", "伊利蛋白"],
}

# ── BILIBILI / ZHIHU — reuse XHS keyword pool (long-form review search) ──
BILI_GROUPS = {
    "flavor":     ["高蛋白饮料 测评", "蛋白奶昔 推荐", "蛋白质饮料 好喝"],
    "pain":       ["蛋白粉 难喝", "蛋白饮料 腥味"],
    "competitor": ["安慕希 测评", "Fairlife 测评", "蛋白饮料 哪个好"],
    "morning":    [], "occasion": [], "yogurt": [],
}
ZHIHU_GROUPS = {
    "flavor":     ["高蛋白饮料 推荐", "好喝的蛋白饮料"],
    "pain":       ["蛋白饮料 为什么难喝", "蛋白粉 腥味"],
    "yogurt":     ["高蛋白酸奶 推荐"],
    "competitor": ["安慕希 简醇 对比"],
    "morning":    [], "occasion": [],
}

# ── Reverse map: keyword -> group (used by scrapers/normalize.py) ───
PLATFORM_GROUPS = {
    "xiaohongshu": XHS_GROUPS,
    "weibo":       WEIBO_GROUPS,
    "douyin":      DOUYIN_GROUPS,
    "bilibili":    BILI_GROUPS,
    "zhihu":       ZHIHU_GROUPS,
}

KEYWORD_TO_GROUP = {
    kw: group
    for groups in PLATFORM_GROUPS.values()
    for group, kws in groups.items()
    for kw in kws
}


def group_for_keyword(keyword: str, default: str = "flavor") -> str:
    """Best-effort group lookup for a keyword across all platforms."""
    return KEYWORD_TO_GROUP.get(keyword, default)
