#!/usr/bin/env bash

source venv/bin/activate

dir=$(pwd)
PYTHONPATH="${PYTHONPATH}:${dir}"
export PYTHONPATH


python parse.py