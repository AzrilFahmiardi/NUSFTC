"""
Bilingual entity dictionaries (Chinese + English) — ported from reference brief
(nlp_social_listening_2.md §6 step 3) and extended with APAC brands.

Substring matching against `clean_text` (original language preserved). Chinese has
no case; English values are lowercased to match the sibling extractor's `text.lower()`.

Drop-in compatible with `nlp social listening/nlp/entity_extractor.py`:
exposes FLAVOR_DICT, PAIN_DICT, OCCASION_DICT, FORMAT_DICT, BRAND_DICT, REGION_HINT_DICT.
"""

FLAVOR_DICT = {
    "matcha":        ["抹茶", "matcha", "green tea latte", "绿茶"],
    "coconut":       ["椰子", "椰奶", "椰", "coconut", "coconut milk"],
    "mango":         ["芒果", "mango"],
    "strawberry":    ["草莓", "strawberry"],
    "lychee":        ["荔枝", "lychee"],
    "peach":         ["桃子", "水蜜桃", "蜜桃", "peach", "white peach"],
    "taro":          ["芋头", "芋泥", "taro"],
    "red_bean":      ["红豆", "red bean", "azuki"],
    "chocolate":     ["巧克力", "可可", "chocolate", "choco", "cocoa"],
    "vanilla":       ["香草", "vanilla"],
    "coffee":        ["咖啡", "拿铁", "coffee", "latte", "mocha", "espresso"],
    "black_sesame":  ["黑芝麻", "芝麻", "black sesame", "sesame"],
    "osmanthus":     ["桂花", "osmanthus"],
    "jasmine":       ["茉莉", "茉莉花", "jasmine"],
    "milk_tea":      ["奶茶", "milk tea", "boba", "bubble tea"],
    "oat":           ["燕麦", "oat", "oatmeal"],
    "banana":        ["香蕉", "banana"],
    "passion_fruit": ["百香果", "passion fruit", "passionfruit"],
    "yuzu":          ["柚子", "yuzu"],
    "honey":         ["蜂蜜", "honey"],
    "caramel":       ["焦糖", "caramel"],
}

PAIN_DICT = {
    "chalky":      ["粉感", "粉末感", "粉粉的", "chalky", "chalk"],
    "too_sweet":   ["太甜", "过甜", "甜腻", "too sweet", "overly sweet", "sugar bomb"],
    "aftertaste":  ["后味", "余味", "回味差", "aftertaste", "lingering"],
    "artificial":  ["人工味", "化工感", "香精味", "artificial", "fake taste", "chemical taste"],
    "too_thick":   ["太稠", "太浓", "难以下咽", "too thick", "heavy", "thick texture"],
    "beany":       ["豆腥味", "植物蛋白味", "beany", "soy taste"],
    "metallic":    ["金属味", "铁腥", "metallic", "iron taste", "metal taste"],
    "grainy":      ["颗粒感", "不细腻", "grainy", "gritty", "powdery"],
    "bad_smell":   ["腥味", "难闻", "臭", "bad smell", "off smell", "smells bad"],
    "expensive":   ["贵", "价格高", "性价比低", "expensive", "pricey", "overpriced"],
    "not_filling": ["不饱", "不顶饱", "没饱腹感", "hungry after", "not filling"],
}

OCCASION_DICT = {
    "morning":          ["早上", "早餐", "早晨", "morning", "breakfast", "wake up"],
    "post_workout":     ["健身后", "运动后", "训练后", "post workout", "after gym", "recovery"],
    "meal_replacement": ["代餐", "不吃饭", "meal replacement", "skip meal", "instead of breakfast"],
    "snack":            ["零食", "加餐", "下午茶", "snack", "afternoon snack"],
    "commute":          ["上班路上", "通勤", "commute", "on the go", "on-the-go"],
    "work":             ["工作", "办公室", "上班", "office", "at work", "wfh"],
}

FORMAT_DICT = {
    "yogurt_drink":  ["酸奶饮料", "喝的酸奶", "乳酸菌饮料", "yogurt drink", "drinkable yogurt", "kefir"],
    "shake":         ["奶昔", "shake", "protein shake"],
    "RTD_liquid":    ["即饮", "瓶装", "rtd", "ready to drink", "ready-to-drink"],
    "powder":        ["蛋白粉", "粉", "protein powder", "powder mix"],
    "jelly":         ["果冻", "布丁", "jelly drink", "protein jelly", "pudding"],
}

BRAND_DICT = {
    # Western (kept from sibling project for cross-corpus comparability)
    "Fairlife":         ["fairlife"],
    "Premier Protein":  ["premier protein"],
    "Muscle Milk":      ["muscle milk", "肌肉牛奶"],
    "Oikos":            ["oikos"],
    "Ensure":           ["ensure", "雅培"],
    "Danone":           ["danone", "达能"],
    "Activia":          ["activia"],
    "Yakult":           ["yakult", "益力多", "养乐多"],
    # APAC / China
    "Yili Ambrosial":   ["yili", "ambrosial", "伊利", "安慕希"],
    "Jianchun":         ["简醇"],
    "Mengniu":          ["蒙牛", "mengniu"],
    "Master Kong":      ["master kong", "ksf", "kang shi fu", "康师傅"],
    "Wahaha":           ["娃哈哈", "wahaha"],
    "Nongfu":           ["农夫山泉", "nongfu"],
    "JoyBefit":         ["佳倍有方"],
}

# For region tagging — substrings searched in clean_text (lowercased for ASCII).
REGION_HINT_DICT = {
    "APAC": [
        "singapore", "malaysia", "philippines", "indonesia", "vietnam",
        "thailand", "japan", "korea", "taiwan", "hong kong", "china",
        "asia", "asian", "apac", "manila", "jakarta", "tokyo", "seoul",
        "shanghai", "beijing",
        # Chinese region tokens
        "中国", "上海", "北京", "广州", "深圳", "杭州", "成都", "香港", "台湾",
        "国内", "亚洲",
    ],
    "Global": [],  # fallback
}

# Words to inject into jieba so brand/flavor neologisms tokenize intact.
JIEBA_USERWORDS = [
    "安慕希", "简醇", "康师傅", "娃哈哈", "农夫山泉", "佳倍有方", "益力多", "养乐多",
    "高蛋白", "蛋白饮料", "蛋白奶昔", "酸奶饮料", "乳清蛋白", "代餐", "粉感",
    "后味", "豆腥味", "抹茶", "桂花", "茉莉", "百香果", "黑芝麻",
]
