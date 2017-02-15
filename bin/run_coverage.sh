#!/bin/bash

PYTHONPATH=src PF1010_SYSCHANGE_SETTINGS=test_settings.cfg coverage run test/api_test.py xml && coverage xml --include=src/app.py
