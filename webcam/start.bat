@echo off
title CTF de Cyrhades CamVirtuelle

echo installation des dependances
pip install -r %~dp0requirements.txt > nul 2>&1

python %~dp0src\webcam.py