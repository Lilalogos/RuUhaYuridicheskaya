#!/bin/zsh
# Печатает в PDF тексты актов из evidence/law/SOURCES.tsv (КонсультантПлюс) и
# пишет source.url.txt / source.sha256 / meta.yml рядом. Повторный запуск
# пропускает уже скачанные.
SK="${0:A:h:h}"; LAW="$SK/evidence/law"; PR="$SK/scripts/print_pdf.sh"
while IFS=$'\t' read -r slug url title; do
  [[ -z "$slug" || "$slug" == \#* ]] && continue
  d="$LAW/$slug"; mkdir -p "$d"
  if [[ -s "$d/source.pdf" ]]; then echo "skip $slug"; continue; fi
  "$PR" "$url" "$d/source.pdf" 60 || { echo "FAIL $slug"; continue; }
  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  printf '%s\n  «Печать→PDF» (Chrome headless) страницы КонсультантПлюс, UTC %s\n' "$url" "$utc" > "$d/source.url.txt"
  (cd "$d" && shasum -a 256 source.pdf > source.sha256)
  red=$(pdftotext "$d/source.pdf" - 2>/dev/null | grep -m1 -oE "\(ред\. от [0-9.]+[^)]*\)|\(последняя редакция\)|с изм[^\n]{0,60}" )
  head1=$(pdftotext "$d/source.pdf" - 2>/dev/null | grep -m1 -E "\S" )
  cat > "$d/meta.yml" <<YML
id: $slug
kind: law_text
title: "$title"
source: КонсультантПлюс (www.consultant.ru), сохранённая страница
redaction_marker: "${red//\"/\'}"
first_line: "${head1//\"/\'}"
source_url: $url
captured_utc: $utc
text_layer: true
pages: $(pdfinfo "$d/source.pdf" 2>/dev/null | awk '/Pages/{print $2}')
notes: "Вторичный правовой справочник, который сам обзорный PDF называет местом сверки; официальное опубликование — publication.pravo.gov.ru (с этой машины недоступен)."
YML
  sleep 2
done < "$LAW/SOURCES.tsv"
echo "DONE $(ls -d $LAW/*/ | wc -l) folders"
