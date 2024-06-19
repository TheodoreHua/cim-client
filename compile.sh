#!/usr/bin/env bash
python -m nuitka --standalone src/main.py --output-filename=cim-client.bin --output-dir=dist/linux
