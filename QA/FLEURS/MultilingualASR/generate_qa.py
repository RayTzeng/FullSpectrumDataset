#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate QA pairs for FLEURS Multilingual Speech Recognition.

Target field: `text` (native-script transcript). Auxiliary field: `lang`.

Template schema (template.jsonl), one JSON object per line:

    {"template_id": "masr_plain_direct_001",
     "question_template": "Transcribe this audio.",
     "answer_template": "text",
     "weight": 0.92}

Optional per-template fields:
    "guard": "cased"   -- only instantiate for entries whose transcript contains
                          cased characters. Required for text.upper()/lower()/
                          title() templates, since ~1/3 of the 102 FLEURS
                          languages are written in caseless scripts (Arabic,
                          Devanagari, Thai, Khmer, CJK, Ge'ez, ...) where the
                          requested transformation would be a silent no-op.

Question placeholders:
    {lang_display}     -- a sampled surface name for the entry's language:
                          the canonical English name (most of the time), an
                          English alternate (Farsi, Odia, Sepedi, ...), or the
                          endonym (Deutsch, 日本語, हिन्दी, ...).

Answer expressions supported by the safe evaluator:
    text
    text.upper() / text.lower() / text.title() / text.strip()
    format_language_cascade(lang, text)   -> "Language: X\\nTranscript: Y"
    format_language_inline(lang, text)    -> "X: Y"
    format_language_tagged(lang, text)    -> "[X] Y"
    string concatenation with +

Cascade answers always use the canonical English display name, never a sampled
alias: the model is being asked to identify the language, so the reference label
must be deterministic.

Output (JSONL.GZ), one object per line:
    {"question": ..., "answer": ..., "metadata": {...}}

Examples:
    python generate_qa.py \\
      --template-jsonl template.jsonl \\
      --metadata /home/tseng/FullSpectrumDataset/metadata/FLEURS/train.jsonl.gz \\
      --output train.jsonl.gz \\
      --samples-per-entry 4 --seed 42

    python generate_qa.py --template-jsonl template.jsonl \\
      --metadata .../dev.jsonl.gz --output dev.jsonl.gz \\
      --samples-per-entry 1 --seed 42
"""

from __future__ import annotations

import argparse
import ast
import gzip
import json
import random
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    from tqdm import tqdm
except ImportError:  # progress is optional
    def tqdm(it, **kwargs):
        return it


PLACEHOLDER_PATTERN = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

# --------------------------------------------------------------------------
# Language surface names
# --------------------------------------------------------------------------

"""Display names, English alternates and endonyms for the 102 FLEURS languages.

`display` is the canonical English name used in cascade answers and as the
high-probability alias in language-conditioned questions. It fixes the four
corpus strings that read awkwardly inline (Cantonese Chinese, Mandarin Chinese,
Northern-Sotho, Sorani-Kurdish).
"""

LANG_ALIASES = {
    "Afrikaans":         {"display": "Afrikaans",        "alt": [],                          "endonym": None},
    "Amharic":           {"display": "Amharic",          "alt": [],                          "endonym": "አማርኛ"},
    "Arabic":            {"display": "Arabic",           "alt": [],                          "endonym": "العربية"},
    "Armenian":          {"display": "Armenian",         "alt": [],                          "endonym": "Հայերեն"},
    "Assamese":          {"display": "Assamese",         "alt": [],                          "endonym": "অসমীয়া"},
    "Asturian":          {"display": "Asturian",         "alt": [],                          "endonym": "Asturianu"},
    "Azerbaijani":       {"display": "Azerbaijani",      "alt": ["Azeri"],                   "endonym": "Azərbaycan dili"},
    "Belarusian":        {"display": "Belarusian",       "alt": [],                          "endonym": "Беларуская"},
    "Bengali":           {"display": "Bengali",          "alt": ["Bangla"],                  "endonym": "বাংলা"},
    "Bosnian":           {"display": "Bosnian",          "alt": [],                          "endonym": "Bosanski"},
    "Bulgarian":         {"display": "Bulgarian",        "alt": [],                          "endonym": "Български"},
    "Burmese":           {"display": "Burmese",          "alt": ["Myanmar"],                 "endonym": "မြန်မာဘာသာ"},
    "Cantonese Chinese": {"display": "Cantonese",        "alt": ["Cantonese Chinese"],       "endonym": "粵語"},
    "Catalan":           {"display": "Catalan",          "alt": [],                          "endonym": "Català"},
    "Cebuano":           {"display": "Cebuano",          "alt": ["Bisaya"],                  "endonym": None},
    "Croatian":          {"display": "Croatian",         "alt": [],                          "endonym": "Hrvatski"},
    "Czech":             {"display": "Czech",            "alt": [],                          "endonym": "Čeština"},
    "Danish":            {"display": "Danish",           "alt": [],                          "endonym": "Dansk"},
    "Dutch":             {"display": "Dutch",            "alt": [],                          "endonym": "Nederlands"},
    "English":           {"display": "English",          "alt": [],                          "endonym": None},
    "Estonian":          {"display": "Estonian",         "alt": [],                          "endonym": "Eesti"},
    "Filipino":          {"display": "Filipino",         "alt": ["Tagalog"],                 "endonym": None},
    "Finnish":           {"display": "Finnish",          "alt": [],                          "endonym": "Suomi"},
    "French":            {"display": "French",           "alt": [],                          "endonym": "Français"},
    "Fula":              {"display": "Fula",             "alt": ["Fulani"],                  "endonym": "Fulfulde"},
    "Galician":          {"display": "Galician",         "alt": [],                          "endonym": "Galego"},
    "Ganda":             {"display": "Ganda",            "alt": ["Luganda"],                 "endonym": "Luganda"},
    "Georgian":          {"display": "Georgian",         "alt": [],                          "endonym": "ქართული"},
    "German":            {"display": "German",           "alt": [],                          "endonym": "Deutsch"},
    "Greek":             {"display": "Greek",            "alt": [],                          "endonym": "Ελληνικά"},
    "Gujarati":          {"display": "Gujarati",         "alt": [],                          "endonym": "ગુજરાતી"},
    "Hausa":             {"display": "Hausa",            "alt": [],                          "endonym": None},
    "Hebrew":            {"display": "Hebrew",           "alt": [],                          "endonym": "עברית"},
    "Hindi":             {"display": "Hindi",            "alt": [],                          "endonym": "हिन्दी"},
    "Hungarian":         {"display": "Hungarian",        "alt": [],                          "endonym": "Magyar"},
    "Icelandic":         {"display": "Icelandic",        "alt": [],                          "endonym": "Íslenska"},
    "Igbo":              {"display": "Igbo",             "alt": [],                          "endonym": "Asụsụ Igbo"},
    "Indonesian":        {"display": "Indonesian",       "alt": [],                          "endonym": "Bahasa Indonesia"},
    "Irish":             {"display": "Irish",            "alt": ["Irish Gaelic"],            "endonym": "Gaeilge"},
    "Italian":           {"display": "Italian",          "alt": [],                          "endonym": "Italiano"},
    "Japanese":          {"display": "Japanese",         "alt": [],                          "endonym": "日本語"},
    "Javanese":          {"display": "Javanese",         "alt": [],                          "endonym": "Basa Jawa"},
    "Kabuverdianu":      {"display": "Kabuverdianu",     "alt": ["Cape Verdean Creole"],     "endonym": "Kriolu"},
    "Kamba":             {"display": "Kamba",            "alt": [],                          "endonym": "Kikamba"},
    "Kannada":           {"display": "Kannada",          "alt": [],                          "endonym": "ಕನ್ನಡ"},
    "Kazakh":            {"display": "Kazakh",           "alt": [],                          "endonym": "Қазақша"},
    "Khmer":             {"display": "Khmer",            "alt": ["Cambodian"],               "endonym": "ភាសាខ្មែរ"},
    "Korean":            {"display": "Korean",           "alt": [],                          "endonym": "한국어"},
    "Kyrgyz":            {"display": "Kyrgyz",           "alt": [],                          "endonym": "Кыргызча"},
    "Lao":               {"display": "Lao",              "alt": [],                          "endonym": "ພາສາລາວ"},
    "Latvian":           {"display": "Latvian",          "alt": [],                          "endonym": "Latviešu"},
    "Lingala":           {"display": "Lingala",          "alt": [],                          "endonym": "Lingála"},
    "Lithuanian":        {"display": "Lithuanian",       "alt": [],                          "endonym": "Lietuvių"},
    "Luo":               {"display": "Luo",              "alt": [],                          "endonym": "Dholuo"},
    "Luxembourgish":     {"display": "Luxembourgish",    "alt": [],                          "endonym": "Lëtzebuergesch"},
    "Macedonian":        {"display": "Macedonian",       "alt": [],                          "endonym": "Македонски"},
    "Malay":             {"display": "Malay",            "alt": [],                          "endonym": "Bahasa Melayu"},
    "Malayalam":         {"display": "Malayalam",        "alt": [],                          "endonym": "മലയാളം"},
    "Maltese":           {"display": "Maltese",          "alt": [],                          "endonym": "Malti"},
    "Mandarin Chinese":  {"display": "Mandarin Chinese", "alt": ["Mandarin", "Chinese"],     "endonym": "普通话"},
    "Maori":             {"display": "Maori",            "alt": ["Māori"],                   "endonym": "Te Reo Māori"},
    "Marathi":           {"display": "Marathi",          "alt": [],                          "endonym": "मराठी"},
    "Mongolian":         {"display": "Mongolian",        "alt": [],                          "endonym": "Монгол"},
    "Nepali":            {"display": "Nepali",           "alt": [],                          "endonym": "नेपाली"},
    "Northern-Sotho":    {"display": "Northern Sotho",   "alt": ["Sepedi"],                  "endonym": "Sesotho sa Leboa"},
    "Norwegian":         {"display": "Norwegian",        "alt": [],                          "endonym": "Norsk"},
    "Nyanja":            {"display": "Nyanja",           "alt": ["Chichewa"],                "endonym": "Chinyanja"},
    "Occitan":           {"display": "Occitan",          "alt": [],                          "endonym": "Occitan"},
    "Oriya":             {"display": "Oriya",            "alt": ["Odia"],                    "endonym": "ଓଡ଼ିଆ"},
    "Oromo":             {"display": "Oromo",            "alt": [],                          "endonym": "Afaan Oromoo"},
    "Pashto":            {"display": "Pashto",           "alt": [],                          "endonym": "پښتو"},
    "Persian":           {"display": "Persian",          "alt": ["Farsi"],                   "endonym": "فارسی"},
    "Polish":            {"display": "Polish",           "alt": [],                          "endonym": "Polski"},
    "Portuguese":        {"display": "Portuguese",       "alt": [],                          "endonym": "Português"},
    "Punjabi":           {"display": "Punjabi",          "alt": ["Panjabi"],                 "endonym": "ਪੰਜਾਬੀ"},
    "Romanian":          {"display": "Romanian",         "alt": [],                          "endonym": "Română"},
    "Russian":           {"display": "Russian",          "alt": [],                          "endonym": "Русский"},
    "Serbian":           {"display": "Serbian",          "alt": [],                          "endonym": "Српски"},
    "Shona":             {"display": "Shona",            "alt": [],                          "endonym": "ChiShona"},
    "Sindhi":            {"display": "Sindhi",           "alt": [],                          "endonym": "سنڌي"},
    "Slovak":            {"display": "Slovak",           "alt": [],                          "endonym": "Slovenčina"},
    "Slovenian":         {"display": "Slovenian",        "alt": ["Slovene"],                 "endonym": "Slovenščina"},
    "Somali":            {"display": "Somali",           "alt": [],                          "endonym": "Soomaali"},
    "Sorani-Kurdish":    {"display": "Sorani Kurdish",   "alt": ["Central Kurdish", "Sorani"], "endonym": "کوردیی ناوەندی"},
    "Spanish":           {"display": "Spanish",          "alt": [],                          "endonym": "Español"},
    "Swahili":           {"display": "Swahili",          "alt": [],                          "endonym": "Kiswahili"},
    "Swedish":           {"display": "Swedish",          "alt": [],                          "endonym": "Svenska"},
    "Tajik":             {"display": "Tajik",            "alt": [],                          "endonym": "Тоҷикӣ"},
    "Tamil":             {"display": "Tamil",            "alt": [],                          "endonym": "தமிழ்"},
    "Telugu":            {"display": "Telugu",           "alt": [],                          "endonym": "తెలుగు"},
    "Thai":              {"display": "Thai",             "alt": [],                          "endonym": "ภาษาไทย"},
    "Turkish":           {"display": "Turkish",          "alt": [],                          "endonym": "Türkçe"},
    "Ukrainian":         {"display": "Ukrainian",        "alt": [],                          "endonym": "Українська"},
    "Umbundu":           {"display": "Umbundu",          "alt": [],                          "endonym": None},
    "Urdu":              {"display": "Urdu",             "alt": [],                          "endonym": "اردو"},
    "Uzbek":             {"display": "Uzbek",            "alt": [],                          "endonym": "Oʻzbekcha"},
    "Vietnamese":        {"display": "Vietnamese",       "alt": [],                          "endonym": "Tiếng Việt"},
    "Welsh":             {"display": "Welsh",            "alt": [],                          "endonym": "Cymraeg"},
    "Wolof":             {"display": "Wolof",            "alt": [],                          "endonym": None},
    "Xhosa":             {"display": "Xhosa",            "alt": [],                          "endonym": "isiXhosa"},
    "Yoruba":            {"display": "Yoruba",           "alt": [],                          "endonym": "Yorùbá"},
    "Zulu":              {"display": "Zulu",             "alt": [],                          "endonym": "isiZulu"},
}

def canonical_display(lang: str) -> str:
    """Canonical English name used in cascade answers."""
    entry = LANG_ALIASES.get(lang)
    if entry:
        return entry["display"]
    return lang.replace("-", " ")


def sample_lang_display(
    lang: str,
    rng: random.Random,
    alt_prob: float,
    endonym_prob: float,
) -> str:
    """Sample a surface name for `lang` used to fill {lang_display}."""
    entry = LANG_ALIASES.get(lang)
    if entry is None:
        return lang.replace("-", " ")

    choices: List[str] = [entry["display"]]
    weights: List[float] = [0.0]  # filled in below

    alts = list(entry.get("alt") or [])
    endonym = entry.get("endonym")

    p_alt = alt_prob if alts else 0.0
    p_end = endonym_prob if endonym else 0.0
    weights[0] = max(1e-9, 1.0 - p_alt - p_end)

    if alts:
        share = p_alt / len(alts)
        for a in alts:
            choices.append(a)
            weights.append(share)
    if endonym:
        choices.append(endonym)
        weights.append(p_end)

    return rng.choices(choices, weights=weights, k=1)[0]


# --------------------------------------------------------------------------
# Deterministic answer formatters
# --------------------------------------------------------------------------

def format_language_cascade(lang: str, text: str) -> str:
    """Two labeled lines. The default cascade shape."""
    return f"Language: {canonical_display(lang)}\nTranscript: {text}"


def format_language_inline(lang: str, text: str) -> str:
    """Single line: language name, colon, transcript."""
    return f"{canonical_display(lang)}: {text}"


def format_language_tagged(lang: str, text: str) -> str:
    """Transcript prefixed with a bracketed language tag."""
    return f"[{canonical_display(lang)}] {text}"


ANSWER_FUNCTIONS = {
    "format_language_cascade": format_language_cascade,
    "format_language_inline": format_language_inline,
    "format_language_tagged": format_language_tagged,
}

ALLOWED_STRING_METHODS = {"upper", "lower", "title", "strip"}


# --------------------------------------------------------------------------
# Safe evaluation of answer expressions
# --------------------------------------------------------------------------

class SafeEvaluator:
    """Evaluates the restricted expression subset used by answer_template."""

    def __init__(self, functions: Dict[str, Any], methods: Sequence[str]):
        self.functions = functions
        self.methods = set(methods)
        self._cache: Dict[str, ast.AST] = {}

    def eval(self, expr: str, env: Dict[str, Any]) -> str:
        expr = expr.strip()
        node = self._cache.get(expr)
        if node is None:
            try:
                node = ast.parse(expr, mode="eval").body
            except SyntaxError as e:
                raise ValueError(f"Invalid answer expression {expr!r}: {e}") from e
            self._cache[expr] = node
        return str(self._eval(node, env))

    def _eval(self, node: ast.AST, env: Dict[str, Any]) -> Any:
        if isinstance(node, ast.Name):
            if node.id not in env:
                raise ValueError(f"Unknown field in answer expression: {node.id}")
            return env[node.id]

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (str, int, float, bool)) or node.value is None:
                return node.value
            raise ValueError(f"Unsupported constant: {node.value!r}")

        if isinstance(node, ast.Call):
            if node.keywords:
                raise ValueError("Keyword arguments are not supported")
            if isinstance(node.func, ast.Name):
                fn = self.functions.get(node.func.id)
                if fn is None:
                    raise ValueError(f"Unsupported function: {node.func.id}")
                return fn(*[self._eval(a, env) for a in node.args])
            if isinstance(node.func, ast.Attribute):
                method = node.func.attr
                if method not in self.methods:
                    raise ValueError(f"Unsupported string method: {method}")
                if node.args:
                    raise ValueError(f"Arguments not supported for .{method}()")
                obj = self._eval(node.func.value, env)
                return getattr(str(obj), method)()
            raise ValueError("Unsupported call expression")

        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return str(self._eval(node.left, env)) + str(self._eval(node.right, env))

        raise ValueError(f"Unsupported answer expression node: {type(node).__name__}")


# --------------------------------------------------------------------------
# I/O
# --------------------------------------------------------------------------

def open_text(path: str, mode: str = "rt"):
    if path.endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def iter_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    """Stream a (optionally gzipped) JSONL file without loading it into memory."""
    with open_text(path, "rt") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON at {path}:{line_no}: {e}") from e


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    return list(iter_jsonl(path))


# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------

def load_templates(path: str) -> List[Dict[str, Any]]:
    raw = read_jsonl(path)
    if not raw:
        raise ValueError(f"No templates found in {path}")

    seen_ids: Dict[str, int] = {}
    templates: List[Dict[str, Any]] = []

    for i, t in enumerate(raw):
        question = t.get("question_template", t.get("question"))
        answer = t.get("answer_template", t.get("answer"))
        tid = t.get("template_id") or f"template_{i:04d}"

        if question is None:
            raise ValueError(f"Template #{i} ({tid}) has no question_template/question")
        if answer is None:
            raise ValueError(f"Template #{i} ({tid}) has no answer_template/answer")
        if tid in seen_ids:
            raise ValueError(
                f"Duplicate template_id {tid!r} at lines {seen_ids[tid] + 1} and {i + 1}"
            )
        seen_ids[tid] = i

        try:
            weight = float(t.get("weight", 1.0))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Template {tid} has non-numeric weight: {t.get('weight')!r}") from e
        if weight <= 0:
            raise ValueError(f"Template {tid} has non-positive weight: {weight}")

        placeholders = set(PLACEHOLDER_PATTERN.findall(question))
        unknown = placeholders - {"lang_display"}
        if unknown:
            raise ValueError(f"Template {tid} uses unsupported placeholder(s): {sorted(unknown)}")

        guard = t.get("guard")
        if guard not in (None, "cased"):
            raise ValueError(f"Template {tid} has unsupported guard: {guard!r}")

        templates.append({
            "template_id": tid,
            "question_template": question,
            "answer_template": answer,
            "weight": weight,
            "needs_lang": "lang_display" in placeholders,
            "guard": guard,
        })

    return templates


def has_cased_characters(text: str) -> bool:
    """True when the string contains at least one character with a case pairing."""
    return text.lower() != text.upper()


def sample_templates(
    pool: List[Dict[str, Any]],
    pool_weights: List[float],
    k: int,
    rng: random.Random,
    mode: str,
) -> List[Dict[str, Any]]:
    if mode == "cartesian":
        return pool
    if mode == "random_sample":
        return rng.choices(pool, k=k)
    return rng.choices(pool, weights=pool_weights, k=k)


# --------------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------------

def build_question(
    template: Dict[str, Any],
    entry: Dict[str, Any],
    rng: random.Random,
    alt_prob: float,
    endonym_prob: float,
) -> str:
    q = template["question_template"]
    if not template["needs_lang"]:
        return q
    display = sample_lang_display(entry["lang"], rng, alt_prob, endonym_prob)
    return q.replace("{lang_display}", display)


def slim_metadata(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": entry.get("id"),
        "path": entry.get("path"),
        "dataset": entry.get("dataset"),
        "lang": entry.get("lang"),
        "lang_group": entry.get("lang_group"),
        "duration": entry.get("duration"),
        "sampling_rate": entry.get("sampling_rate"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate FLEURS Multilingual ASR QA pairs from weighted templates.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--template-jsonl", "--template", dest="template_jsonl", required=True,
                        help="Path to template.jsonl")
    parser.add_argument("--metadata", required=True,
                        help="Path to the FLEURS metadata .jsonl or .jsonl.gz")
    parser.add_argument("--output", required=True, help="Output path (.jsonl.gz)")
    parser.add_argument("--samples-per-entry", "--num-templates-per-entry",
                        dest="samples_per_entry", type=int, default=1,
                        help="Templates instantiated per metadata entry")
    parser.add_argument("--mode", choices=["weighted_sample", "random_sample", "cartesian"],
                        default="weighted_sample",
                        help="weighted_sample honours template weights; cartesian emits every "
                             "template for every entry and ignores --samples-per-entry")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--alt-prob", type=float, default=0.12,
                        help="Probability of using an English alternate name for {lang_display}")
    parser.add_argument("--endonym-prob", type=float, default=0.15,
                        help="Probability of using the endonym for {lang_display}")
    parser.add_argument("--keep-metadata", action="store_true",
                        help="Keep the full metadata object instead of the slim projection")
    parser.add_argument("--lang-alias-json", default=None,
                        help="Optional JSON file overriding the built-in language alias table")
    parser.add_argument("--limit", type=int, default=None,
                        help="Process at most N metadata entries (for smoke tests)")
    parser.add_argument("--skip-errors", action="store_true",
                        help="Log and skip failing entries instead of aborting")
    args = parser.parse_args()

    if args.samples_per_entry <= 0:
        parser.error("--samples-per-entry must be positive")
    if not 0.0 <= args.alt_prob + args.endonym_prob < 1.0:
        parser.error("--alt-prob + --endonym-prob must be in [0, 1)")

    if args.lang_alias_json:
        with open(args.lang_alias_json, encoding="utf-8") as f:
            LANG_ALIASES.clear()
            LANG_ALIASES.update(json.load(f))

    rng = random.Random(args.seed)
    evaluator = SafeEvaluator(ANSWER_FUNCTIONS, ALLOWED_STRING_METHODS)
    templates = load_templates(args.template_jsonl)

    # Two pools: the full set, and the subset valid for caseless transcripts.
    pool_all = templates
    pool_uncased = [t for t in templates if t["guard"] != "cased"]
    w_all = [t["weight"] for t in pool_all]
    w_uncased = [t["weight"] for t in pool_uncased]
    n_guarded = len(pool_all) - len(pool_uncased)

    if not pool_uncased:
        raise ValueError("Every template is guarded; caseless entries would produce nothing.")

    total_entries = total_qa = skipped = guarded_skips = 0
    alias_uses: Dict[str, int] = {}

    with open_text(args.output, "wt") as fout:
        stream = iter_jsonl(args.metadata)
        for entry in tqdm(stream, desc=f"{args.metadata} -> {args.output}", unit=" entry"):
            if args.limit is not None and total_entries >= args.limit:
                break
            total_entries += 1
            try:
                text = entry["text"]
                lang = entry["lang"]
            except KeyError as e:
                if args.skip_errors:
                    skipped += 1
                    print(f"[WARN] entry #{total_entries} missing field {e}", file=sys.stderr)
                    continue
                raise ValueError(f"Entry #{total_entries} is missing required field {e}") from e

            if has_cased_characters(text):
                pool, weights = pool_all, w_all
            else:
                pool, weights = pool_uncased, w_uncased
                guarded_skips += 1

            try:
                chosen = sample_templates(
                    pool, weights, args.samples_per_entry, rng, args.mode
                )
                meta = entry if args.keep_metadata else slim_metadata(entry)
                for tmpl in chosen:
                    question = build_question(
                        tmpl, entry, rng, args.alt_prob, args.endonym_prob
                    )
                    answer = evaluator.eval(tmpl["answer_template"], entry)
                    fout.write(json.dumps(
                        {"question": question, "answer": answer, "metadata": meta},
                        ensure_ascii=False,
                    ) + "\n")
                    total_qa += 1
            except Exception as e:
                if args.skip_errors:
                    skipped += 1
                    print(f"[WARN] skipping entry #{total_entries}: {e}", file=sys.stderr)
                    continue
                raise

    print(f"Templates loaded      : {len(templates)} ({n_guarded} cased-guarded)", file=sys.stderr)
    print(f"Metadata entries      : {total_entries}", file=sys.stderr)
    print(f"  caseless transcripts : {guarded_skips} (guarded templates withheld)", file=sys.stderr)
    print(f"QA pairs written      : {total_qa} -> {args.output}", file=sys.stderr)
    if skipped:
        print(f"Entries skipped       : {skipped}", file=sys.stderr)


if __name__ == "__main__":
    main()
