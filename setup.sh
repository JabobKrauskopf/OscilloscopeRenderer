#!/bin/bash
python3 -m venv .venv
pip install --upgrade pip
. .venv/bin/activate
pip install -r requirements.txt
