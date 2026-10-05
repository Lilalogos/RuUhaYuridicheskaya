#!/usr/bin/env python3
"""Пересчитывает производные значения релиза KB после любой правки applaw/.

Обновляет в applaw/RELEASE_PROFILE.json:
  * source_capsules / referenced_source_capsules — по sources/source_capsules.json;
  * case_semantic_sha256, gold-сводку, счётчики файлов и байт пакета;
и перезаписывает applaw/SHA256SUMS.txt штатным verify_checksums.write_manifest.

Счётчик байт включает сам RELEASE_PROFILE.json, поэтому пересчёт идёт до
стабилизации. Запуск из любого места:

    python3 -B scripts/refresh_release.py
    cd applaw && python3 -B scripts/validate_release.py --kb .
"""

from __future__ import annotations

import collections
import json
import os
import sys
from pathlib import Path

KB = Path(__file__).resolve().parent.parent / "applaw"
sys.path.insert(0, str(KB / "scripts"))

import validate_refs  # noqa: E402
import verify_checksums  # noqa: E402
from _kb import artifact_semantic_aggregate, case_card_records, gold_records, load_source_capsules  # noqa: E402


def main() -> int:
    profile_path = KB / "RELEASE_PROFILE.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"), object_pairs_hook=collections.OrderedDict)
    before = dict(profile)

    registry = load_source_capsules(KB)
    sources = [s for s in registry.get("sources", []) if isinstance(s, dict)]
    profile["source_capsules"] = len(sources)
    profile["referenced_source_capsules"] = sum(1 for s in sources if s.get("referenced") is True)
    profile["case_semantic_sha256"] = artifact_semantic_aggregate(case_card_records(KB))
    profile["gold_semantic_sha256"] = artifact_semantic_aggregate(gold_records(KB))
    gold_registry = json.loads((KB / "eval" / "gold.json").read_text(encoding="utf-8"))
    profile["gold_registry_summary"] = gold_registry.get("summary")

    for _ in range(5):
        profile_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        file_count, byte_count = validate_refs.package_totals(KB)
        if (
            profile.get("package_file_count_before_checksum") == file_count
            and profile.get("package_bytes_before_checksum") == byte_count
        ):
            break
        profile["package_file_count_before_checksum"] = file_count
        profile["package_bytes_before_checksum"] = byte_count
    else:
        print("!! счётчики пакета не стабилизировались", file=sys.stderr)
        return 1

    for key, value in profile.items():
        if before.get(key) != value:
            print(f"RELEASE_PROFILE.{key}: {before.get(key)!r} -> {value!r}")

    # verify_checksums требует запуска из корня пакета
    os.chdir(KB)
    return verify_checksums.write_manifest(KB)


if __name__ == "__main__":
    sys.exit(main())
