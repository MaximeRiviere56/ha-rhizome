"""Configuration pytest commune.

`pytest_plugins` ne peut etre declare que dans le conftest de la racine : le
harnais de Home Assistant est donc branche ici, et les fixtures propres a la
couche HA restent dans `tests/ha/conftest.py`.

Les tests de `tests/` eux-memes n'ont besoin de rien de tout cela : ils tournent
aussi sous `python3 -m unittest`, avec le Python du systeme.
"""

from __future__ import annotations

import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

pytest_plugins = "pytest_homeassistant_custom_component"
