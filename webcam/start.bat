@echo off
title CTF de Cyrhades CamVirtuelle

pip install -r %~dp0requirements.txt

python %~dp0src\webcam.py