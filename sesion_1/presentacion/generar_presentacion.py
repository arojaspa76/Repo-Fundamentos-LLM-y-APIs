"""
Genera la presentación de las Sesiones 1 y 2 del curso
"Fundamentos de Arquitectura LLM" con python-pptx.

    pip install python-pptx
    python presentacion/generar_presentacion.py

Salida: presentacion/Sesiones_01_02_Fundamentos_Arquitectura_LLM.pptx
Cada diapositiva incluye notas del orador con la explicación teórica completa.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import slides_s1  # noqa: E402
from pptx_helpers import Deck  # noqa: E402

try:
    import slides_s2  # noqa: E402
except ImportError:  # durante el desarrollo
    slides_s2 = None


def main(out: str | None = None) -> Path:
    deck = Deck()
    slides_s1.build(deck)
    if slides_s2 and "--solo-s1" not in sys.argv:
        slides_s2.build(deck)
    path = Path(out) if out else HERE / "Sesiones_01_02_Fundamentos_Arquitectura_LLM.pptx"
    deck.save(str(path))
    print(f"✅ {deck.n} diapositivas → {path}")
    return path


if __name__ == "__main__":
    main()
