#!/bin/zsh
# Печатает карточки документов Базы решений ФАС в evidence/enforcement/<id>/source.pdf
# по списку <id>\t<url>; пишет source.url.txt и source.sha256. meta.yml/quotes.md — вручную.
SK="${0:A:h:h}"; PR="$SK/scripts/print_pdf.sh"; LIST="$1"
while IFS=$'\t' read -r id url; do
  [[ -z "$id" ]] && continue
  d="$SK/evidence/enforcement/$id"; mkdir -p "$d"
  if [[ -s "$d/source.pdf" ]]; then echo "skip $id"; continue; fi
  "$PR" "$url" "$d/source.pdf" 60 || { echo "FAIL $id"; continue; }
  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  printf 'source.pdf: %s\n  «Печать→PDF» (Chrome headless) карточки документа в Базе решений ФАС, UTC %s\nнайдено поиском br.fas.gov.ru (type=2), прогон 2026-10-04 «сбор пробелов»\n' "$url" "$utc" > "$d/source.url.txt"
  (cd "$d" && shasum -a 256 source.pdf > source.sha256)
  sleep 2
done < "$LIST"
echo DONE
