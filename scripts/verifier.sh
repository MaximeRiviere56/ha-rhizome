#!/usr/bin/env bash
# Batterie de verification complete. Monte l'environnement si besoin.
#
#   ./scripts/verifier.sh          tout
#   ./scripts/verifier.sh rapide   seulement les modules purs (sans Home Assistant)
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== modules purs (Python du systeme, sans dependance) =="
PYTHONPATH=tests python3 -m unittest discover -s tests -p 'test_*.py'

echo
echo "== coherence du catalogue =="
python3 tools/auditer_catalogue.py | tail -2

[ "${1:-}" = "rapide" ] && exit 0

if [ ! -x .venv/bin/python ]; then
  echo
  echo "== creation de l'environnement (Python 3.14 + Home Assistant) =="
  command -v uv >/dev/null || { echo "uv est requis : https://docs.astral.sh/uv/"; exit 1; }
  uv python install 3.14
  uv venv --python 3.14 .venv
  VIRTUAL_ENV=.venv uv pip install -r requirements-dev.txt
fi

echo
echo "== ruff =="
if command -v ruff >/dev/null; then ruff check .; else .venv/bin/python -m ruff check .; fi

echo
echo "== mypy =="
.venv/bin/python -m mypy custom_components/rhizome

echo
echo "== pytest =="
.venv/bin/python -m pytest -q --cov=custom_components/rhizome --cov-report=term-missing

echo
echo "Tout est vert."
