import json
import re
from pathlib import Path


REPO_ROOT = Path("/root/country")
SOURCE_ROOT = Path("/tmp/chinese-poetry")
OUTPUT_PATH = REPO_ROOT / "chinese-famous-quotes" / "data" / "quotes.zh-CN.json"


THEME_RULES = [
    ("学习", ["学", "知", "读", "书", "师", "教", "问", "习"]),
    ("成长", ["志", "行", "修", "省", "德", "善", "成"]),
    ("坚持", ["坚", "恒", "毅", "忍", "不舍", "百折", "磨"]),
    ("时间", ["日", "月", "年", "春", "秋", "晨", "夜", "时", "光阴"]),
    ("山水", ["山", "江", "湖", "海", "月", "风", "云", "雨", "雪"]),
    ("情绪", ["愁", "悲", "欢", "乐", "喜", "怒", "忧", "思"]),
    ("人生", ["人", "生", "世", "身", "心", "命"]),
    ("友情", ["友", "朋", "相知", "知己"]),
    ("志向", ["志", "远", "天下", "凌云", "丈夫"]),
    ("家国", ["国", "天下", "苍生", "社稷", "百姓"]),
    ("处世", ["君子", "小人", "礼", "仁", "义", "信", "和"]),
    ("自然", ["花", "草", "木", "鸟", "春", "秋", "霜", "露"]),
]

TONE_RULES = [
    ("激励", ["志", "行", "当", "须", "莫", "不", "丈夫", "凌云", "千里"]),
    ("平静", ["清", "静", "淡", "闲", "月", "风", "云", "水"]),
    ("哲思", ["道", "理", "知", "心", "生", "世", "无", "有"]),
    ("警醒", ["忧", "危", "慎", "惧", "戒", "省"]),
    ("温和", ["春", "花", "雨", "友", "乐"]),
]

USAGE_RULES = [
    ("学习激励", ["学习", "成长", "志向"]),
    ("晨间提醒", ["时间", "成长"]),
    ("情绪安抚", ["情绪", "平静", "自然"]),
    ("任务执行", ["坚持", "激励", "成长"]),
    ("关系表达", ["友情", "处世"]),
    ("审美文案", ["山水", "自然", "平静"]),
]


def normalize_text(text: str) -> str:
    text = str(text).strip()
    text = re.sub(r"\s+", "", text)
    text = text.replace("「", "“").replace("」", "”")
    text = text.replace("『", "“").replace("』", "”")
    text = text.replace("《", "《").replace("》", "》")
    text = re.sub(r"[()（）\[\]【】]", "", text)
    return text


def text_length(text: str) -> int:
    return len(re.sub(r"[，。！？；：“”《》、】【…·\s]", "", text))


def dedupe_key(text: str) -> str:
    return re.sub(r"[，。！？；：“”《》、】【…·\s]", "", normalize_text(text))


def is_good_quote(text: str) -> bool:
    if not text:
        return False
    if any(x in text for x in ["http", "作者", "注", "其一", "其二", "并序", "之一"]):
        return False
    clean_len = text_length(text)
    if clean_len < 6 or clean_len > 30:
        return False
    if len(re.findall(r"[A-Za-z0-9]", text)) > 0:
        return False
    if re.search(r"['\",`]", text):
        return False
    if text.count("“") != text.count("”"):
        return False
    if text.count("，") > 3:
        return False
    return True


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"[。！？；]", normalize_text(text))
    return [p.strip("，、 “ ”") for p in parts if p.strip("，、 “ ”")]


def strip_speech_prefix(text: str) -> str:
    text = normalize_text(text)
    prefixes = [
        r"^[\u4e00-\u9fff]{1,8}[问對对答言]曰[:：，]?",
        r"^[\u4e00-\u9fff]{1,8}曰[:：，]?",
        r"^[\u4e00-\u9fff]{1,8}问[:：，]?",
        r"^子曰[:：，]?",
        r"^曰[:：，]?",
    ]
    for pattern in prefixes:
        text = re.sub(pattern, "", text)
    return text.strip("，、 ")


def extract_inner_quotes(text: str) -> list[str]:
    text = normalize_text(text)
    parts = re.findall(r"“([^”]{4,60})”", text)
    results = []
    for part in parts:
        part = strip_speech_prefix(part)
        if is_good_quote(part):
            results.append(part)
        for sentence in split_sentences(part):
            sentence = strip_speech_prefix(sentence)
            if is_good_quote(sentence):
                results.append(sentence)
    return results


def infer_themes(text: str) -> list[str]:
    themes = []
    for theme, keywords in THEME_RULES:
        if any(keyword in text for keyword in keywords):
            themes.append(theme)
    if not themes:
        themes.append("哲思")
    return themes[:3]


def infer_tone(text: str) -> str:
    for tone, keywords in TONE_RULES:
        if any(keyword in text for keyword in keywords):
            return tone
    return "哲思"


def infer_usage(themes: list[str], tone: str) -> list[str]:
    usage = []
    theme_set = set(themes + [tone])
    for item, needs in USAGE_RULES:
        if any(need in theme_set for need in needs):
            usage.append(item)
    if not usage:
        usage.append("每日金句")
    return usage[:3]


def quote_entry(idx: int, quote: str, author: str, source: str, era: str) -> dict:
    themes = infer_themes(quote)
    tone = infer_tone(quote)
    usage = infer_usage(themes, tone)
    return {
        "id": f"cq_{idx:05d}",
        "quote": quote,
        "author": author,
        "source": source,
        "era": era,
        "themes": themes,
        "tone": tone,
        "usage": usage,
    }


def add_candidate(candidates: list[dict], seen: set[str], quote: str, author: str, source: str, era: str):
    quote = strip_speech_prefix(quote).strip("，、")
    if not is_good_quote(quote):
        return
    key = dedupe_key(quote)
    if key in seen:
        return
    seen.add(key)
    candidates.append({"quote": quote, "author": author, "source": source, "era": era})


def add_from_paragraphs(candidates: list[dict], seen: set[str], paragraphs: list[str], author: str, source: str, era: str):
    for para in paragraphs:
        para = normalize_text(para)
        for inner in extract_inner_quotes(para):
            add_candidate(candidates, seen, inner, author, source, era)
        if is_good_quote(para):
            add_candidate(candidates, seen, para, author, source, era)
        for sentence in split_sentences(para):
            sentence = strip_speech_prefix(sentence)
            if is_good_quote(sentence):
                add_candidate(candidates, seen, sentence, author, source, era)


def add_from_lines(candidates: list[dict], seen: set[str], lines: list[str], author: str, source: str, era: str):
    norm_lines = [normalize_text(x) for x in lines if normalize_text(x)]
    for line in norm_lines:
        if is_good_quote(line):
            add_candidate(candidates, seen, line, author, source, era)
    for i in range(len(norm_lines) - 1):
        merged = f"{norm_lines[i]}，{norm_lines[i + 1]}"
        if is_good_quote(merged):
            add_candidate(candidates, seen, merged, author, source, era)


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def process_classics(candidates: list[dict], seen: set[str]):
    classics = [
        ("论语/lunyu.json", "孔子及弟子", "《论语》", "春秋"),
        ("四书五经/mengzi.json", "孟子", "《孟子》", "战国"),
        ("四书五经/daxue.json", "曾子学派", "《大学》", "先秦"),
        ("四书五经/zhongyong.json", "子思", "《中庸》", "战国"),
        ("诗经/shijing.json", "佚名", "《诗经》", "先秦"),
        ("楚辞/chuci.json", "屈原等", "《楚辞》", "先秦"),
        ("幽梦影/youmengying.json", "张潮", "《幽梦影》", "清"),
        ("曹操诗集/caocao.json", "曹操", "《曹操诗集》", "东汉末"),
        ("纳兰性德/纳兰性德诗集.json", "纳兰性德", "《纳兰性德诗集》", "清"),
    ]
    for rel, author, source, era in classics:
        data = load_json(SOURCE_ROOT / rel)
        for item in data:
            if isinstance(item, dict):
                if "paragraphs" in item and isinstance(item["paragraphs"], list):
                    actual_author = item.get("author", author)
                    actual_source = item.get("title") or item.get("chapter") or source
                    add_from_paragraphs(candidates, seen, item["paragraphs"], actual_author, actual_source, era)
                elif "content" in item:
                    add_from_paragraphs(candidates, seen, [item["content"]], author, source, era)


def process_tang_poems(candidates: list[dict], seen: set[str]):
    for path in sorted((SOURCE_ROOT / "全唐诗").glob("poet.tang.*.json")):
        data = load_json(path)
        for item in data:
            add_from_lines(
                candidates,
                seen,
                item.get("paragraphs", []),
                item.get("author", "唐人"),
                item.get("title", "《全唐诗》"),
                "唐",
            )


def process_song_ci(candidates: list[dict], seen: set[str]):
    for path in sorted((SOURCE_ROOT / "宋词").glob("ci.song.*.json")):
        data = load_json(path)
        for item in data:
            source = item.get("rhythmic", "《宋词》")
            add_from_lines(candidates, seen, item.get("paragraphs", []), item.get("author", "宋人"), source, "宋")
    data = load_json(SOURCE_ROOT / "宋词" / "宋词三百首.json")
    for item in data:
        source = item.get("rhythmic", "《宋词三百首》")
        add_from_lines(candidates, seen, item.get("paragraphs", []), item.get("author", "宋人"), source, "宋")


def process_mengxue(candidates: list[dict], seen: set[str]):
    for path in sorted((SOURCE_ROOT / "蒙学").glob("*.json")):
        data = load_json(path)
        source = f"《{path.stem}》"
        author = "古籍"
        era = "古代"
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    if "paragraphs" in item:
                        add_from_paragraphs(candidates, seen, item.get("paragraphs", []), author, item.get("chapter", source), era)
                    elif "content" in item:
                        add_from_paragraphs(candidates, seen, [item["content"]], author, source, era)
                elif isinstance(item, str):
                    add_from_paragraphs(candidates, seen, [item], author, source, era)


def score(item: dict) -> tuple:
    q = item["quote"]
    length = text_length(q)
    punctuation_bonus = 2 if "，" in q else 0
    classics_bonus = 2 if item["era"] in {"春秋", "战国", "先秦"} else 0
    author_bonus = 1 if item["author"] not in {"佚名", "古籍", "唐人", "宋人"} else 0
    return (
        punctuation_bonus + classics_bonus + author_bonus,
        -abs(length - 12),
        -length,
        q,
    )


def author_cap(author: str) -> int:
    if author in {"佚名", "无名氏", "不詳", "不详", "古籍", "唐人", "宋人"}:
        return 500
    if author in {"孟子", "孔子及弟子", "屈原等"}:
        return 1200
    return 80


def main():
    candidates = []
    seen = set()

    process_classics(candidates, seen)
    process_mengxue(candidates, seen)
    process_tang_poems(candidates, seen)
    process_song_ci(candidates, seen)

    candidates.sort(key=score, reverse=True)
    selected = []
    author_counts = {}
    for item in candidates:
        limit = author_cap(item["author"])
        count = author_counts.get(item["author"], 0)
        if count >= limit:
            continue
        selected.append(item)
        author_counts[item["author"]] = count + 1
        if len(selected) == 10000:
            break
    output = [
        quote_entry(i + 1, item["quote"], item["author"], item["source"], item["era"])
        for i, item in enumerate(selected)
    ]
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"generated {len(output)} quotes to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
