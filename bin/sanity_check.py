#!/usr/bin/env python3

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")
import django
django.setup()

print('Django OK:', django.get_version())

import random
from coint.ibrx100 import CARTEIRA_IBRX
print('Lucky Ticker:', random.choice(CARTEIRA_IBRX))

