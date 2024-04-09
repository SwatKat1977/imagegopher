#!/bin/sh

echo "[INFO] Running Python linter"
python -m pylint $1 --rcfile=../.pylintrc
LINT_EXIT_CODE=$?

if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit $LINT_EXIT_CODE
fi
