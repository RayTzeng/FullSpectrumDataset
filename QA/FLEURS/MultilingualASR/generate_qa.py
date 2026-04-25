#!/usr/bin/env python3
"""
Generate QA pairs for FLEURS Multilingual Speech Recognition.

Input:
  1. template.jsonl
     Each line should contain either:
       {"question_template": "...", "answer_template": "text", "weight": 0.9}
     or:
       {"question": "...", "answer": "text", "weight": 0.9}

  2. metadata.jsonl.gz
     Each line should contain at least:
       {
         "text": "...",
         "lang": "...",
         ...
       }

Output:
  output.jsonl.gz
     Each line:
       {
         "question": "...",
         "answer": "...",
         "metadata": {...}
       }

Example:
  python generate_qa.py \
    --template-jsonl template.jsonl \
    --metadata fleurs_train.jsonl.gz \
    --output qa_train.jsonl.gz \
    --samples-per-entry 1 \
    --seed 42
"""

import argparse
import ast
import gzip
import json
import random
import sys
from typing import Any, Dict, Iterable, List, Optional


def open_text(path: str, mode: str):
    """Open plain text or gzip text file based on suffix."""
    if path.endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    records = []
    with open_text(path, "rt") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON at {path}:{line_no}: {e}") from e
    return records


def iter_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    with open_text(path, "rt") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON at {path}:{line_no}: {e}") from e


def normalize_template(raw: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Normalize template schema to {question_template, answer_template, weight}."""
    question = raw.get("question_template", raw.get("question"))
    answer = raw.get("answer_template", raw.get("answer"))
    weight = raw.get("weight", 1.0)

    if question is None:
        raise ValueError(f"Template #{index} is missing question_template/question: {raw}")
    if answer is None:
        raise ValueError(f"Template #{index} is missing answer_template/answer: {raw}")

    try:
        weight = float(weight)
    except Exception as e:
        raise ValueError(f"Template #{index} has non-numeric weight: {weight}") from e

    if weight <= 0:
        raise ValueError(f"Template #{index} has non-positive weight: {weight}")

    return {
        "question_template": question,
        "answer_template": answer,
        "weight": weight,
        "raw": raw,
    }


def load_templates(path: str) -> List[Dict[str, Any]]:
    raw_templates = load_jsonl(path)
    templates = [normalize_template(t, i) for i, t in enumerate(raw_templates)]

    if not templates:
        raise ValueError(f"No templates found in {path}")

    return templates


def format_language_cascade(lang: str, text: str) -> str:
    """
    Deterministic answer format for language-ID + transcription templates.

    You can change this format if you want a different cascade output style,
    but keep it deterministic and aligned with your templates.
    """
    return f"Language: {lang}\nTranscript: {text}"


def safe_eval_answer_expr(expr: str, metadata: Dict[str, Any]) -> str:
    """
    Evaluate a restricted answer expression.

    Supported examples:
      text
      lang
      format_language_cascade(lang, text)
      text.strip()
      text.lower()
      text.upper()

    This intentionally avoids unrestricted eval.
    """
    expr = expr.strip()

    env = dict(metadata)
    env["format_language_cascade"] = format_language_cascade

    # Fast path: direct field reference
    if expr in metadata:
        return str(metadata[expr])

    # Parse and evaluate a restricted subset of Python expressions.
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Invalid answer expression: {expr}") from e

    return str(_eval_ast_node(tree.body, env))


def _eval_ast_node(node: ast.AST, env: Dict[str, Any]) -> Any:
    if isinstance(node, ast.Name):
        if node.id not in env:
            raise ValueError(f"Unknown name in answer expression: {node.id}")
        return env[node.id]

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (str, int, float, bool)) or node.value is None:
            return node.value
        raise ValueError(f"Unsupported constant in answer expression: {node.value!r}")

    if isinstance(node, ast.Call):
        # Function call: format_language_cascade(lang, text)
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name != "format_language_cascade":
                raise ValueError(f"Unsupported function call: {func_name}")
            func = env[func_name]
            args = [_eval_ast_node(arg, env) for arg in node.args]
            if node.keywords:
                raise ValueError("Keyword arguments are not supported in answer expressions")
            return func(*args)

        # Method call: text.strip(), text.lower(), text.upper()
        if isinstance(node.func, ast.Attribute):
            obj = _eval_ast_node(node.func.value, env)
            method = node.func.attr
            allowed_methods = {"strip", "lower", "upper", "title"}
            if method not in allowed_methods:
                raise ValueError(f"Unsupported string method: {method}")
            if node.args or node.keywords:
                raise ValueError(f"Arguments are not supported for string method: {method}")
            if not isinstance(obj, str):
                obj = str(obj)
            return getattr(obj, method)()

        raise ValueError("Unsupported call expression")

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _eval_ast_node(node.left, env)
        right = _eval_ast_node(node.right, env)
        return str(left) + str(right)

    if isinstance(node, ast.JoinedStr):
        # Supports f-string-like expressions if ever stored as parsed AST.
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(str(value.value))
            elif isinstance(value, ast.FormattedValue):
                parts.append(str(_eval_ast_node(value.value, env)))
            else:
                raise ValueError("Unsupported f-string component")
        return "".join(parts)

    raise ValueError(f"Unsupported answer expression node: {ast.dump(node)}")


def build_question(template: str, metadata: Dict[str, Any]) -> str:
    """
    Format question template using metadata fields.

    Common placeholders:
      {lang}
      {lang_display}
      any other metadata key, if present

    lang_display defaults to metadata["lang"].
    """
    fmt = dict(metadata)
    if "lang_display" not in fmt:
        fmt["lang_display"] = metadata.get("lang", "")

    try:
        return template.format(**fmt)
    except KeyError as e:
        missing = e.args[0]
        raise ValueError(
            f"Question template requires missing metadata field {{{missing}}}: {template}"
        ) from e


def sample_templates(
    templates: List[Dict[str, Any]],
    k: int,
    rng: random.Random,
    replace: bool,
) -> List[Dict[str, Any]]:
    if replace:
        weights = [t["weight"] for t in templates]
        return rng.choices(templates, weights=weights, k=k)

    if k > len(templates):
        raise ValueError(
            f"--samples-per-entry={k} exceeds number of templates={len(templates)} "
            "while --no-replacement is enabled."
        )

    # Weighted sampling without replacement.
    available = templates[:]
    selected = []
    for _ in range(k):
        weights = [t["weight"] for t in available]
        chosen = rng.choices(available, weights=weights, k=1)[0]
        selected.append(chosen)
        available.remove(chosen)
    return selected


def generate_qa_for_entry(
    metadata: Dict[str, Any],
    templates: List[Dict[str, Any]],
    samples_per_entry: int,
    rng: random.Random,
    replace: bool,
    keep_metadata: bool,
) -> List[Dict[str, Any]]:
    if "text" not in metadata:
        raise ValueError(f"Metadata entry is missing required field 'text': {metadata}")

    sampled = sample_templates(
        templates=templates,
        k=samples_per_entry,
        rng=rng,
        replace=replace,
    )

    qa_pairs = []
    for tmpl in sampled:
        question = build_question(tmpl["question_template"], metadata)
        answer = safe_eval_answer_expr(tmpl["answer_template"], metadata)

        item = {
            "question": question,
            "answer": answer,
        }

        if keep_metadata:
            item["metadata"] = metadata
        else:
            item["metadata"] = {
                "id": metadata.get("id"),
                "path": metadata.get("path"),
                "dataset": metadata.get("dataset"),
                "lang": metadata.get("lang"),
                "duration": metadata.get("duration"),
                "sampling_rate": metadata.get("sampling_rate"),
            }

        qa_pairs.append(item)

    return qa_pairs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-jsonl", required=True, help="Path to template JSONL.")
    parser.add_argument("--metadata", required=True, help="Path to metadata JSONL or JSONL.GZ.")
    parser.add_argument("--output", required=True, help="Output path, usually .jsonl.gz.")
    parser.add_argument("--samples-per-entry", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--no-replacement",
        action="store_true",
        help="Sample templates without replacement per metadata entry.",
    )
    parser.add_argument(
        "--keep-metadata",
        action="store_true",
        help="Keep the full original metadata object in each output entry.",
    )
    parser.add_argument(
        "--skip-errors",
        action="store_true",
        help="Skip malformed entries/templates instead of stopping.",
    )
    args = parser.parse_args()

    if args.samples_per_entry <= 0:
        raise ValueError("--samples-per-entry must be positive")

    rng = random.Random(args.seed)
    templates = load_templates(args.template_jsonl)

    total_meta = 0
    total_qa = 0
    skipped = 0

    with open_text(args.output, "wt") as fout:
        for metadata in iter_jsonl(args.metadata):
            total_meta += 1
            try:
                qa_pairs = generate_qa_for_entry(
                    metadata=metadata,
                    templates=templates,
                    samples_per_entry=args.samples_per_entry,
                    rng=rng,
                    replace=not args.no_replacement,
                    keep_metadata=args.keep_metadata,
                )

                for qa in qa_pairs:
                    fout.write(json.dumps(qa, ensure_ascii=False) + "\n")
                    total_qa += 1

            except Exception as e:
                if args.skip_errors:
                    skipped += 1
                    print(
                        f"[WARN] Skipping metadata entry #{total_meta}: {e}",
                        file=sys.stderr,
                    )
                    continue
                raise

    print(f"Loaded templates: {len(templates)}", file=sys.stderr)
    print(f"Processed metadata entries: {total_meta}", file=sys.stderr)
    print(f"Generated QA pairs: {total_qa}", file=sys.stderr)
    if skipped:
        print(f"Skipped entries: {skipped}", file=sys.stderr)


if __name__ == "__main__":
    main()