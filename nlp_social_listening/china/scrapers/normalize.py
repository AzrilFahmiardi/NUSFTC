"""
Normalization adapter — maps each platform's native fields to the unified RAW schema
(superset of the Twitter raw schema + `platform` + `url`), so the China enriched CSV
is mergeable with twitter_enriched.csv downstream.

Privacy (brief §10): author names are MD5-hashed here and never stored raw.

Each platform's native field map is best-effort and confirmed during the Phase-1
smoke test (Apify/MediaCrawler item shapes vary); this is the ONLY place to edit when
a source's schema changes.
"""

import hashlib
import logging
from datetime import datetime, timezone

import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.queries_cn import group_for_keyword

logger = logging.getLogger(__name__)

# Canonical RAW columns (Twitter names kept so analysis code reads `tweet_id` etc.).
RAW_COLUMNS = [
    "tweet_id", "text", "created_at", "user_name", "user_screen_name",
    "user_followers", "favorite_count", "retweet_count", "reply_count",
    "language", "query", "query_group", "scraped_at", "platform", "url",
]


def _hash(name) -> str:
    if name is None:
        return ""
    return hashlib.md5(str(name).encode("utf-8")).hexdigest()


def _first(d: dict, *keys, default=None):
    """Return the first present, non-null value among keys (supports dotted paths)."""
    for k in keys:
        cur = d
        ok = True
        for part in k.split("."):
            if isinstance(cur, dict) and part in cur and cur[part] is not None:
                cur = cur[part]
            else:
                ok = False
                break
        if ok and cur not in (None, ""):
            return cur
    return default


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _blank_row(platform: str, keyword: str) -> dict:
    return {
        "tweet_id": "", "text": "", "created_at": "", "user_name": "",
        "user_screen_name": "", "user_followers": pd.NA, "favorite_count": 0,
        "retweet_count": 0, "reply_count": 0, "language": "",
        "query": keyword, "query_group": group_for_keyword(keyword),
        "scraped_at": _now(), "platform": platform, "url": "",
    }


def _normalize_records(records: list[dict], platform: str, field_map) -> pd.DataFrame:
    """Generic normalizer: field_map(record) -> dict of native values."""
    rows = []
    for rec in records:
        kw = rec.get("keyword_source") or rec.get("query") or ""
        row = _blank_row(platform, kw)
        mapped = field_map(rec)
        row.update({k: v for k, v in mapped.items() if v is not None})
        row["user_screen_name"] = _hash(mapped.get("_author"))
        row["user_name"] = ""                       # never stored
        row["query_group"] = group_for_keyword(kw)
        rows.append(row)
    df = pd.DataFrame(rows, columns=RAW_COLUMNS)
    logger.info("Normalized %d %s records", len(df), platform)
    return df


# ── Per-platform field maps ─────────────────────────────────────────
def _xhs_apify(rec: dict) -> dict:
    return {
        "tweet_id": "xhs_" + str(_first(rec, "id", "noteId", "note_id", default="")),
        "text": _first(rec, "desc", "title", "content", "text", default=""),
        "created_at": _first(rec, "time", "createTime", "publishTime", "date", default=""),
        "_author": _first(rec, "author.nickname", "nickname", "user.nickname", "author", default=""),
        "user_followers": _first(rec, "author.fans", "fans", default=None),
        "favorite_count": _first(rec, "likedCount", "liked_count", "likes", "interactInfo.likedCount", default=0),
        "reply_count": _first(rec, "commentsCount", "comment_count", "comments", default=0),
        "retweet_count": _first(rec, "sharedCount", "shareCount", "shares", default=0),
        "url": _first(rec, "url", "noteUrl", "link", default=""),
        "language": "zh",
    }


def _xhs_mediacrawler(rec: dict) -> dict:
    """MediaCrawler XHS CSV output. Posts have note_id; comments have comment_id."""
    is_comment = bool(_first(rec, "comment_id", default=""))
    if is_comment:
        id_val = "xhs_cmt_" + str(_first(rec, "comment_id", default=""))
        text = _first(rec, "content", default="")
        ts = _first(rec, "create_time", "time", default="")
        likes = _first(rec, "like_count", default=0)
        replies = _first(rec, "sub_comment_count", default=0)
    else:
        id_val = "xhs_" + str(_first(rec, "note_id", default=""))
        title = _first(rec, "title", default="")
        desc = _first(rec, "desc", default="")
        text = (title + "\n" + desc).strip() if title else desc
        ts = _first(rec, "time", default="")
        likes = _first(rec, "liked_count", default=0)
        replies = _first(rec, "comment_count", default=0)

    kw = _first(rec, "source_keyword", "keyword_source", default="")
    return {
        "tweet_id": id_val,
        "text": text,
        "created_at": ts,
        "_author": _first(rec, "nickname", "user_id", default=""),
        "user_followers": None,
        "favorite_count": likes,
        "reply_count": replies,
        "retweet_count": _first(rec, "share_count", default=0),
        "url": _first(rec, "note_url", "url", default=""),
        "query": kw,
        "language": "zh",
    }


def _weibo(rec: dict) -> dict:
    # Aliases cover both Apify actors: sian.agency (weiboId/attitudeCount/postedAt/
    # screenName/weiboPageUrl) and zhorex (postId/attitudesCount/createdAt/authorName/
    # postUrl), plus MediaCrawler snake_case fields.
    return {
        "tweet_id": "wb_" + str(_first(rec, "id", "mid", "_id", "weiboId", "postId", "bid", default="")),
        "text": _first(rec, "text", "content", "text_raw", "raw_text", default=""),
        "created_at": _first(rec, "postedAt", "createdAt", "created_at", "created", "publish_time", default=""),
        "_author": _first(rec, "screenName", "authorName", "user.screen_name", "screen_name",
                          "nick_name", "userId", "authorId", "author", default=""),
        "user_followers": _first(rec, "authorFollowers", "user.followers_count", "followers_count", default=None),
        "favorite_count": _first(rec, "attitudeCount", "attitudesCount", "attitudes_count",
                                 "likes_count", "like_count", default=0),
        "reply_count": _first(rec, "commentCount", "commentsCount", "comments_count", "comment_count", default=0),
        "retweet_count": _first(rec, "repostCount", "repostsCount", "reposts_count", "repost_count", default=0),
        "url": _first(rec, "weiboPageUrl", "postUrl", "url", "link", default=""),
        "language": "zh",
    }


def _douyin(rec: dict) -> dict:
    # Aliases cover the zen-studio actor (camelCase: text/createDate/authorMeta/
    # statistics.diggCount/shareUrl) plus MediaCrawler snake_case fields.
    return {
        "tweet_id": "dy_" + str(_first(rec, "aweme_id", "id", "awemeId", default="")),
        "text": _first(rec, "text", "desc", "title", "content", default=""),
        "created_at": _first(rec, "createDate", "create_time", "createTime", "time", default=""),
        "_author": _first(rec, "authorMeta.name", "authorMeta.nickName", "author.nickname",
                          "nickname", "author", default=""),
        "user_followers": _first(rec, "authorMeta.fans", "authorMeta.followerCount",
                                 "author.follower_count", "follower_count", default=None),
        "favorite_count": _first(rec, "statistics.diggCount", "diggCount", "statistics.digg_count",
                                 "digg_count", "likes", default=0),
        "reply_count": _first(rec, "statistics.commentCount", "commentCount",
                              "statistics.comment_count", "comment_count", default=0),
        "retweet_count": _first(rec, "statistics.shareCount", "shareCount",
                                "statistics.share_count", "share_count", default=0),
        "url": _first(rec, "shareUrl", "url", "share_url", default=""),
        "language": "zh",
    }


def _bilibili(rec: dict) -> dict:
    return {
        "tweet_id": "bili_" + str(_first(rec, "bvid", "aid", "id", default="")),
        "text": _first(rec, "title", "desc", "content", "message", default=""),
        "created_at": _first(rec, "pubdate", "ctime", "created", default=""),
        "_author": _first(rec, "owner.name", "author", "uname", default=""),
        "user_followers": _first(rec, "owner.fans", "fans", default=None),
        "favorite_count": _first(rec, "stat.like", "like", "likes", default=0),
        "reply_count": _first(rec, "stat.reply", "reply", "comments", default=0),
        "retweet_count": _first(rec, "stat.share", "share", default=0),
        "url": _first(rec, "url", "short_link", default=""),
        "language": "zh",
    }


def _zhihu(rec: dict) -> dict:
    return {
        "tweet_id": "zh_" + str(_first(rec, "id", "answer_id", default="")),
        "text": _first(rec, "content", "excerpt", "title", default=""),
        "created_at": _first(rec, "created_time", "updated_time", "created", default=""),
        "_author": _first(rec, "author.name", "author", default=""),
        "user_followers": _first(rec, "author.follower_count", default=None),
        "favorite_count": _first(rec, "voteup_count", "vote_count", default=0),
        "reply_count": _first(rec, "comment_count", default=0),
        "url": _first(rec, "url", default=""),
        "language": "zh",
    }


_FIELD_MAPS = {
    "xiaohongshu": _xhs_apify,          # Apify actor output
    "xiaohongshu_mc": _xhs_mediacrawler, # MediaCrawler CSV output
    "weibo": _weibo,
    "douyin": _douyin,
    "bilibili": _bilibili,
    "zhihu": _zhihu,
}


def normalize(records: list[dict], platform: str) -> pd.DataFrame:
    """Normalize a list of native records for `platform` into the RAW schema."""
    if platform not in _FIELD_MAPS:
        raise ValueError(f"Unknown platform '{platform}'. Known: {list(_FIELD_MAPS)}")
    return _normalize_records(records, platform, _FIELD_MAPS[platform])


def concat_all_raw(raw_dir: Path, out_path: Path) -> pd.DataFrame:
    """Concatenate every <platform>_raw.csv in raw_dir into china_all_raw.csv."""
    frames = []
    for csv in sorted(raw_dir.glob("*_raw.csv")):
        if csv.name == "china_all_raw.csv":
            continue
        frames.append(pd.read_csv(csv))
    if not frames:
        logger.warning("No per-platform raw CSVs found in %s", raw_dir)
        return pd.DataFrame(columns=RAW_COLUMNS)
    df = pd.concat(frames, ignore_index=True)
    df.to_csv(out_path, index=False)
    logger.info("Merged %d rows -> %s", len(df), out_path)
    return df
