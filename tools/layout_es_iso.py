"""Posición de cada tecla del Flux (75 %, ISO español) sobre el fondo de 1920x1080.

Medido sobre el contorno gris que Polymath dibuja en su vista previa del teclado
(diablo2/polymath_preview1.png): paso de 118,3 px entre teclas, tecla de 1u = 107 px
(hueco de 11,5 px), primera columna en x=24. La fila de funciones va separada de la de
números. Encima de y≈337 queda la franja de módulos.

Las fotos (diablo2/calibration*.jpg) confirman la distribución, pero salen desplazadas
por el paralaje: las teclas tienen altura y se ven en ángulo.
"""
PITCH = 118.3
GAP = 11.5
X0 = 24
ROW_TOP = [337, 484, 601, 719, 838, 955]
KEY_H = 106.5

# Filas de arriba abajo: (nombre, ancho en u). La Enter ISO se divide en sus dos filas.
ROWS = [
    [("Esc", 1)] + [(f"F{i}", 1) for i in range(1, 13)] + [("PrtSc", 1), ("Pause", 1), ("Delete", 1)],
    [("º", 1)] + [(c, 1) for c in "1234567890"] + [("'", 1), ("¡", 1), ("Backspace", 2), ("Home", 1)],
    [("Tab", 1.5)] + [(c, 1) for c in "QWERTYUIOP"] + [("`", 1), ("+", 1), ("Enter", 1.5), ("End", 1)],
    [("Caps", 1.75)] + [(c, 1) for c in "ASDFGHJKLÑ"] + [("´", 1), ("Ç", 1), ("Enter2", 1.25), ("PgUp", 1)],
    [("LShift", 1.25), ("<", 1)] + [(c, 1) for c in "ZXCVBNM"] + [(",", 1), (".", 1), ("-", 1),
                                                                  ("RShift", 1.75), ("Up", 1), ("PgDn", 1)],
    [("LCtrl", 1.25), ("MT", 1), ("Win", 1), ("LAlt", 1), ("Space", 5.75), ("RAlt", 1), ("MT1", 1),
     ("RCtrl", 1), ("Left", 1), ("Down", 1), ("Right", 1)],
]


def keys():
    """{nombre: (x0, y0, x1, y1)} en píxeles del fondo: el contorno de la tecla."""
    out = {}
    for r, row in enumerate(ROWS):
        u = 0.0
        for name, w in row:
            out[name] = (X0 + u * PITCH, ROW_TOP[r], X0 + (u + w) * PITCH - GAP, ROW_TOP[r] + KEY_H)
            u += w
        assert u == 16, (r, u)
    return out
