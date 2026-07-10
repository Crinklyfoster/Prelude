#!/bin/bash

backend/venv/bin/locust \
-f benchmarks/locustfile.py \
--host=http://localhost:8000
