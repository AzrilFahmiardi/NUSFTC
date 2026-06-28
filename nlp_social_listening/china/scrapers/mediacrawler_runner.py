"""
MediaCrawler runner — thin subprocess wrapper around the self-hosted MediaCrawler CLI.

MediaCrawler (github.com/NanmiCoder/MediaCrawler) reads module-level vars from
`config/base_config.py`. We patch the needed vars in place (backup -> patch -> run ->
restore), then invoke `uv run main.py --platform <p> --lt qrcode --type search`, and
copy the resulting CSVs from MediaCrawler's own `data/<platform>/` into our interim dir.

Platforms via this self-hosted path (throwaway account): weibo, bilibili, zhihu, douyin.
Xiaohongshu goes through Apify instead (see apify_client_xhs.py).

NOTE: requires MediaCrawler cloned at config.settings.MEDIACRAWLER_DIR with its own
`uv` env, Chrome >= 144 for CDP login, and a logged-in throwaway account (QR scan).
License: MediaCrawler is research/learning-only — keep volumes modest.
"""

import logging
import shutil
import subprocess
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import MEDIACRAWLER_DIR, DATA_INTERIM

logger = logging.getLogger(__name__)

# platform name (ours) -> MediaCrawler --platform code
PLATFORM_CODE = {
    "weibo": "wb",
    "bilibili": "bili",
    "zhihu": "zhihu",
    "douyin": "dy",
    "xiaohongshu": "xhs",
    "kuaishou": "ks",
}

_CONFIG_REL = Path("config") / "base_config.py"


_OVERRIDE_BEGIN = "# === nlp_social_china override (auto-managed) ==="
_OVERRIDE_END = "# === end nlp_social_china override ==="


def _patch_config(mc_dir: Path, overrides: dict[str, str]) -> Path:
    """Append an override block at the END of base_config.py (module-level reassignment
    — the last assignment wins, so this safely overrides earlier multi-line definitions
    like CRAWLER_TYPE = ( ... ) without fragile in-place regex editing). Returns backup."""
    cfg = mc_dir / _CONFIG_REL
    backup = cfg.with_suffix(".py.bak")
    if not backup.exists():
        shutil.copy2(cfg, backup)
    # Always start from the pristine backup so overrides don't stack across runs.
    text = backup.read_text(encoding="utf-8")
    block = [_OVERRIDE_BEGIN]
    block += [f"{var} = {value}" for var, value in overrides.items()]
    block += [_OVERRIDE_END, ""]
    text = text.rstrip() + "\n\n" + "\n".join(block)
    cfg.write_text(text, encoding="utf-8")
    logger.info("Patched MediaCrawler config (appended override): %s", list(overrides))
    return backup


def _restore_config(mc_dir: Path):
    cfg = mc_dir / _CONFIG_REL
    backup = cfg.with_suffix(".py.bak")
    if backup.exists():
        shutil.copy2(backup, cfg)
        logger.info("Restored MediaCrawler base_config.py from backup")


def run_platform(
    platform: str,
    keywords: list[str],
    max_notes: int = 100,
    get_comments: bool = True,
    max_comments: int = 10,
    enable_cdp: bool = True,
    login_type: str = "qrcode",
    mc_dir: Path = MEDIACRAWLER_DIR,
    timeout: int = 3600,
) -> list[Path]:
    """Run one MediaCrawler search session for a platform across `keywords`.

    Returns paths of CSVs copied into DATA_INTERIM. Raises on non-zero exit.
    """
    if platform not in PLATFORM_CODE:
        raise ValueError(f"Unsupported platform '{platform}'. Known: {list(PLATFORM_CODE)}")
    mc_dir = Path(mc_dir)
    if not (mc_dir / "main.py").exists():
        raise FileNotFoundError(
            f"MediaCrawler not found at {mc_dir}. Clone it first (see README §Setup)."
        )

    code = PLATFORM_CODE[platform]
    kw_str = ",".join(keywords)
    overrides = {
        "PLATFORM": f'"{code}"',
        "XHS_INTERNATIONAL": "True",  # required: domestic endpoint blocked outside China
        "KEYWORDS": f'"{kw_str}"',
        "CRAWLER_TYPE": '"search"',
        "SAVE_DATA_OPTION": '"csv"',
        "LOGIN_TYPE": f'"{login_type}"',
        "ENABLE_GET_COMMENTS": str(get_comments),
        "ENABLE_GET_SUB_COMMENTS": "False",
        "CRAWLER_MAX_NOTES_COUNT": str(max_notes),
        "CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES": str(max_comments),
        "MAX_CONCURRENCY_NUM": "1",
        "ENABLE_CDP_MODE": str(enable_cdp),
        "START_PAGE": "1",
        "SAVE_LOGIN_STATE": "True",
    }

    _patch_config(mc_dir, overrides)
    try:
        cmd = ["uv", "run", "main.py", "--platform", code, "--lt", login_type, "--type", "search"]
        logger.info("Running MediaCrawler: %s (keywords=%d)", " ".join(cmd), len(keywords))
        proc = subprocess.run(cmd, cwd=str(mc_dir), timeout=timeout,
                              capture_output=True, text=True)
        if proc.returncode != 0:
            logger.error("MediaCrawler stderr:\n%s", proc.stderr[-4000:])
            raise RuntimeError(f"MediaCrawler exited {proc.returncode} for {platform}")
        logger.info("MediaCrawler stdout tail:\n%s", proc.stdout[-1500:])
    finally:
        _restore_config(mc_dir)

    return _collect_output(mc_dir, code, platform)


def _collect_output(mc_dir: Path, code: str, platform: str) -> list[Path]:
    """Copy MediaCrawler's CSV output for this platform into DATA_INTERIM."""
    src_dir = mc_dir / "data" / code
    copied = []
    if not src_dir.exists():
        logger.warning("No MediaCrawler output dir at %s", src_dir)
        return copied
    for csv in src_dir.glob("*.csv"):
        dest = DATA_INTERIM / f"{platform}_{csv.name}"
        shutil.copy2(csv, dest)
        copied.append(dest)
    logger.info("Collected %d CSV(s) for %s -> %s", len(copied), platform, DATA_INTERIM)
    return copied
