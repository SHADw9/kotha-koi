#!/usr/bin/env python3
"""Generate the kotha-koi app icon (PNG + ICO) with no external dependencies.

Design: deep-green rounded tile, cream speech bubble, green K monogram and a
terracotta conversation dot.
"""
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parent.parent
MASTER = 1024
SS = 2  # supersampling factor

GREEN = (15, 107, 87, 255)
CREAM = (255, 249, 238, 255)
TERRACOTTA = (201, 106, 59, 255)
TRANSPARENT = (0, 0, 0, 0)


def rounded_rect(x, y, x0, y0, x1, y1, r):
    if x < x0 or x > x1 or y < y0 or y > y1:
        return False
    dx = max(x0 + r - x, 0.0, x - (x1 - r))
    dy = max(y0 + r - y, 0.0, y - (y1 - r))
    return dx * dx + dy * dy <= r * r


def triangle(x, y, a, b, c):
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    d1 = sign((x, y), a, b)
    d2 = sign((x, y), b, c)
    d3 = sign((x, y), c, a)
    neg = d1 < 0 or d2 < 0 or d3 < 0
    pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (neg and pos)


def poly(x, y, points):
    inside = False
    j = len(points) - 1
    for i in range(len(points)):
        xi, yi = points[i]
        xj, yj = points[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def circle(x, y, cx, cy, r):
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def render_master():
    n = MASTER * SS
    rows = []
    for py in range(n):
        y = (py + 0.5) / SS
        row = bytearray()
        for px in range(n):
            x = (px + 0.5) / SS
            color = TRANSPARENT
            if rounded_rect(x, y, 0, 0, MASTER, MASTER, MASTER * 0.225):
                color = GREEN
            if rounded_rect(x, y, MASTER * 0.175, MASTER * 0.185, MASTER * 0.825,
                            MASTER * 0.655, MASTER * 0.145):
                color = CREAM
            if triangle(x, y, (MASTER * 0.34, MASTER * 0.62),
                        (MASTER * 0.255, MASTER * 0.815),
                        (MASTER * 0.485, MASTER * 0.655)):
                color = CREAM
            # K monogram, drawn as three thick bars.
            if rounded_rect(x, y, MASTER * 0.355, MASTER * 0.285, MASTER * 0.43,
                            MASTER * 0.575, MASTER * 0.025):
                color = GREEN
            if poly(x, y, [(MASTER * 0.425, MASTER * 0.44), (MASTER * 0.425, MASTER * 0.36),
                           (MASTER * 0.595, MASTER * 0.265), (MASTER * 0.635, MASTER * 0.335),
                           (MASTER * 0.475, MASTER * 0.43)]):
                color = GREEN
            if poly(x, y, [(MASTER * 0.425, MASTER * 0.42), (MASTER * 0.47, MASTER * 0.43),
                           (MASTER * 0.635, MASTER * 0.555), (MASTER * 0.59, MASTER * 0.625),
                           (MASTER * 0.425, MASTER * 0.485)]):
                color = GREEN
            if circle(x, y, MASTER * 0.725, MASTER * 0.735, MASTER * 0.058):
                color = TERRACOTTA
            row.extend(color)
        rows.append(bytes(row))
    return rows, n


def downsample(rows, src, size):
    out = []
    ratio = src / size
    for oy in range(size):
        sy = min(src - 1, int((oy + 0.5) * ratio))
        src_row = rows[sy]
        row = bytearray()
        for ox in range(size):
            sx = min(src - 1, int((ox + 0.5) * ratio))
            i = sx * 4
            row.extend(src_row[i:i + 4])
        out.append(bytes(row))
    return out


def png_bytes(rows, size):
    raw = b"".join(b"\x00" + r for r in rows)

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data +
                struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))

    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(raw, 9)) +
            chunk(b"IEND", b""))


def ico_bytes(pngs):
    count = len(pngs)
    header = struct.pack("<HHH", 0, 1, count)
    offset = 6 + 16 * count
    entries, payload = b"", b""
    for size, data in pngs:
        dim = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
        payload += data
    return header + entries + payload


def main():
    rows, src = render_master()
    masters = {}
    for size in (16, 32, 48, 64, 72, 96, 128, 144, 192, 256, 512):
        masters[size] = png_bytes(downsample(rows, src, size), size)

    android = ROOT / "android" / "app" / "src" / "main" / "res"
    for folder, size in (("mipmap-mdpi", 48), ("mipmap-hdpi", 72), ("mipmap-xhdpi", 96),
                         ("mipmap-xxhdpi", 144), ("mipmap-xxxhdpi", 192)):
        (android / folder / "ic_launcher.png").write_bytes(masters[size])

    icons = ROOT / "desktop" / "src-tauri" / "icons"
    icons.mkdir(parents=True, exist_ok=True)
    (icons / "32x32.png").write_bytes(masters[32])
    (icons / "128x128.png").write_bytes(masters[128])
    (icons / "128x128@2x.png").write_bytes(masters[256])
    (icons / "icon.png").write_bytes(masters[512])
    (icons / "icon.ico").write_bytes(
        ico_bytes([(s, masters[s]) for s in (16, 32, 48, 64, 128, 256)])
    )
    print("Wrote Android mipmaps and Tauri icons.")


if __name__ == "__main__":
    main()
