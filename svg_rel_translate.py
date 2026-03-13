#!/usr/bin/env python3
"""
Преобразует абсолютный path SVG в относительный с вынесением начальной точки в translate.
Использование: python svg_rel_translate.py "d-строкa"
"""

import sys
from svg.path import parse_path
from svg.path.path import Move, Line, CubicBezier, QuadraticBezier, Arc, Close

def format_coord(value):
    """Форматирует число с 4 знаками после запятой, убирая лишние нули."""
    s = f"{value:.4f}"
    return s.rstrip('0').rstrip('.') if '.' in s else s

def rel_command(seg, current_abs, is_first):
    """
    Возвращает строку относительной команды для сегмента seg.
    current_abs — абсолютная позиция пера перед выполнением команды.
    is_first — флаг первого сегмента (нужен для Move).
    Возвращает (cmd_string, new_abs), где new_abs — абсолютная позиция после команды.
    """
    if isinstance(seg, Move):
        if is_first:
            return "M0 0", seg.end
        else:
            delta = seg.end - current_abs
            return f"m {format_coord(delta.real)} {format_coord(delta.imag)}", seg.end
    elif isinstance(seg, Line):
        delta = seg.end - current_abs
        return f"l {format_coord(delta.real)} {format_coord(delta.imag)}", seg.end
    elif isinstance(seg, CubicBezier):
        c1 = seg.control1 - current_abs
        c2 = seg.control2 - current_abs
        e = seg.end - current_abs
        cmd = (f"c {format_coord(c1.real)} {format_coord(c1.imag)} "
               f"{format_coord(c2.real)} {format_coord(c2.imag)} "
               f"{format_coord(e.real)} {format_coord(e.imag)}")
        return cmd, seg.end
    elif isinstance(seg, QuadraticBezier):
        c = seg.control - current_abs
        e = seg.end - current_abs
        cmd = f"q {format_coord(c.real)} {format_coord(c.imag)} {format_coord(e.real)} {format_coord(e.imag)}"
        return cmd, seg.end
    elif isinstance(seg, Arc):
        e = seg.end - current_abs
        cmd = (f"a {format_coord(seg.radius.real)} {format_coord(seg.radius.imag)} "
               f"{seg.rotation} {int(seg.arc)} {int(seg.sweep)} "
               f"{format_coord(e.real)} {format_coord(e.imag)}")
        return cmd, seg.end
    elif isinstance(seg, Close):
        # Close возвращает перо в начало подконтура, но команда z не требует координат
        return "z", seg.end  # seg.end == seg.start (начало подконтура)
    else:
        return "", current_abs

def convert_path(d_string):
    path = parse_path(d_string)
    if not path:
        return d_string, (0, 0)

    # Базовая точка — конец первого сегмента (первый Move)
    first = path[0]
    if isinstance(first, Move):
        base_x, base_y = first.end.real, first.end.imag
    else:
        base_x, base_y = first.start.real, first.start.imag
    base = complex(base_x, base_y)

    new_parts = []
    current_abs = base  # начинаем с базовой точки

    for i, seg in enumerate(path):
        cmd, current_abs = rel_command(seg, current_abs, is_first=(i == 0))
        new_parts.append(cmd)

    new_d = " ".join(new_parts)
    return new_d, (base_x, base_y)

def main():
    if len(sys.argv) < 2:
        print("Использование: python svg_rel_translate.py \"d-строкa\"")
        sys.exit(1)

    d_input = sys.argv[1]
    try:
        new_d, (tx, ty) = convert_path(d_input)
        tx_str = format_coord(tx)
        ty_str = format_coord(ty)
        print(f'<path transform="translate({tx_str} {ty_str})" d="{new_d}" />')
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
