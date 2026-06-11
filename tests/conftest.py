import sys
from pathlib import Path

# Aggiunge skyview/ al sys.path in modo che gli import assoluti interni al progetto
# (es. from config import ...) funzionino correttamente durante l'esecuzione dei test.
_skyview_dir = Path(__file__).resolve().parent.parent / "skyview"
sys.path.insert(0, str(_skyview_dir))
