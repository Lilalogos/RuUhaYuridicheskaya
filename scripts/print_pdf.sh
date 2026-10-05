#!/bin/zsh
# Печать веб-страницы в PDF headless Chrome с принудительным завершением.
# Chrome 154 после записи файла не выходит (висит updater) — ждём появления
# стабильного файла и убиваем процесс.
#   print_pdf.sh <url> <out.pdf> [timeout_s]
set -u
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
URL="$1"; OUT="$2"; TMO="${3:-45}"
PROFILE="$(mktemp -d /tmp/applaw-chrome.XXXXXX)"
rm -f "$OUT"
"$CH" --headless=new --disable-gpu --no-sandbox --disable-extensions --no-first-run \
  --user-data-dir="$PROFILE" --timeout=30000 --no-pdf-header-footer \
  --print-to-pdf="$OUT" "$URL" >/dev/null 2>&1 &
PID=$!
prev=-1
for i in $(seq 1 $TMO); do
  sleep 1
  if [[ -s "$OUT" ]]; then
    size=$(stat -f%z "$OUT")
    if [[ "$size" == "$prev" ]]; then break; fi
    prev=$size
  fi
  kill -0 $PID 2>/dev/null || break
done
kill $PID 2>/dev/null; sleep 0.3; kill -9 $PID 2>/dev/null
pkill -9 -f "user-data-dir=$PROFILE" 2>/dev/null
rm -rf "$PROFILE"
if [[ -s "$OUT" ]]; then
  echo "OK $(pdfinfo "$OUT" 2>/dev/null | awk '/Pages/{print $2}')p $(pdftotext "$OUT" - 2>/dev/null | wc -w | tr -d ' ')w $OUT"
else
  echo "FAIL $OUT"; exit 1
fi
