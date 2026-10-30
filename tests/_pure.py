"""Charge les modules purs de l'integration sans executer son __init__.py.

`custom_components/rhizome/__init__.py` importe Home Assistant, absent de ce
Mac. Les deux modules qu'on veut tester n'en dependent pas : on les charge donc
dans un paquet synthetique, ce qui laisse leurs imports relatifs fonctionner.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import types

SRC = pathlib.Path(__file__).resolve().parent.parent / "custom_components" / "rhizome"
PAQUET = "rhizome_pur"


def _charger(nom_module: str):
    if PAQUET not in sys.modules:
        paquet = types.ModuleType(PAQUET)
        paquet.__path__ = [str(SRC)]
        sys.modules[PAQUET] = paquet

    complet = f"{PAQUET}.{nom_module}"
    if complet in sys.modules:
        return sys.modules[complet]

    spec = importlib.util.spec_from_file_location(complet, SRC / f"{nom_module}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[complet] = module
    spec.loader.exec_module(module)
    return module


i18n = _charger("i18n")
lifecycle = _charger("lifecycle")
phenology = _charger("phenology")
rotation = _charger("rotation")
serialisation = _charger("serialisation")
watering = _charger("watering")
