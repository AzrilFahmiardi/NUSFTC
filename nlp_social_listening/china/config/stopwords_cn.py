"""
Chinese stopwords + sensory-preserve set for jieba-tokenized text.

CN_STOPWORDS: common function words / particles removed before clustering.
CN_SENSORY_PRESERVE: flavor/sensory/occasion tokens that must survive stopword
removal (mirrors the English SENSORY_PRESERVE in the sibling project).
"""

# Compact, high-frequency Chinese stopword set (particles, pronouns, conjunctions).
CN_STOPWORDS = {
    "的", "了", "和", "是", "在", "我", "有", "也", "就", "都", "而", "及", "与",
    "着", "或", "一个", "没有", "我们", "你们", "他们", "她", "他", "它", "这",
    "那", "这个", "那个", "这些", "那些", "啊", "吧", "呢", "吗", "哦", "嗯",
    "呀", "啦", "哈", "哈哈", "嘛", "哟", "之", "其", "以", "于", "对", "把",
    "被", "让", "向", "从", "到", "给", "为", "因为", "所以", "但是", "可是",
    "如果", "虽然", "然后", "还是", "还有", "就是", "不是", "可以", "这样",
    "那样", "怎么", "什么", "怎样", "现在", "已经", "真的", "感觉", "觉得",
    "一下", "一些", "比较", "非常", "特别", "有点", "挺", "很", "太", "更",
    "最", "好像", "应该", "可能", "大家", "自己", "时候", "东西", "一种",
    "这种", "那种", "今天", "昨天", "明天", "之后", "之前", "里面", "外面",
    "上面", "下面", "现在", "目前", "最近", "一直", "一定", "其实", "不过",
    "并且", "等等", "之类", "等", "啊啊", "哈喽", "大概", "差不多",
    # latin noise commonly mixed in
    "the", "a", "an", "is", "are", "and", "or", "of", "to", "in", "for",
}

# Sensory / product vocabulary preserved through stopword removal (zh + en).
CN_SENSORY_PRESERVE = {
    # taste / texture
    "甜", "苦", "酸", "咸", "鲜", "腻", "香", "浓", "稠", "稀",
    "粉感", "颗粒感", "细腻", "顺滑", "丝滑", "清爽", "醇厚", "口感",
    "后味", "余味", "回味", "腥味", "豆腥味", "金属味", "人工味", "香精味",
    # flavors
    "抹茶", "椰子", "椰奶", "芒果", "草莓", "荔枝", "桃子", "蜜桃", "芋头",
    "红豆", "巧克力", "可可", "香草", "咖啡", "拿铁", "黑芝麻", "芝麻",
    "桂花", "茉莉", "奶茶", "燕麦", "香蕉", "百香果", "柚子", "蜂蜜", "焦糖",
    # format / product
    "酸奶", "奶昔", "蛋白粉", "蛋白", "高蛋白", "乳清蛋白", "饮料", "饮品",
    "代餐", "果冻", "布丁", "即饮", "瓶装",
    # occasion
    "早餐", "早上", "早晨", "健身", "运动", "训练", "通勤", "上班", "加餐", "零食",
    # english sensory (for mixed rows)
    "sweet", "bitter", "creamy", "smooth", "chalky", "thick", "aftertaste",
    "matcha", "coconut", "mango", "protein", "yogurt",
}
