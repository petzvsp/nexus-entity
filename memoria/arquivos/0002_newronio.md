# newronio

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
☯ NEWRÔNIO v12.1 — QUANTUM + OLLAMA AUTO-START
Auto-detecta e inicia o Ollama em background na primeira execução.
Arquiteto: Peterson Kennedy Silva | Betim / MG
⚠️  Uso educacional e autorizado apenas
"""
import os, sys, json, time, sqlite3, subprocess, re, socket, platform, ssl
import hashlib, urllib.request, urllib.error, urllib.parse, base64, random, string
import warnings, math, shutil, ftplib, mimetypes
from datetime import datetime
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# 📦 NEXUS BRIDGE — carrega funções do projeto Nexus
# ═══════════════════════════════════════════════════════════════
sys.path.insert(0, str(Path.home() / "plugins"))
try:
    from nexus_bridge import get_bridge
    _nexus = get_bridge()
except Exception as _e:
    _nexus = None
