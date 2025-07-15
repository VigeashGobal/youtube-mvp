#!/usr/bin/env bash
export PYTHONPATH=./backend
python3 -m uvicorn backend.app.main:app --reload --port 8000 