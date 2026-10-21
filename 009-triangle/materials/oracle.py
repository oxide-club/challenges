"""Oráculo lento para entradas válidas pequenas; usa frações exatas em Python.

Uso: python3 materials/oracle.py < materials/triangle.txt > /tmp/reference.ppm
Não é um parser de referência para entradas malformadas nem solução em C.
"""
from fractions import Fraction as F
import sys


def render(text):
    data = iter(map(int, text.split()))
    w, h, count = next(data), next(data), next(data)
    pixels = [(0, 0, 0)] * (w * h)
    for _ in range(count):
        vertices = [tuple(next(data) for _ in range(5)) for _ in range(3)]
        def edge(a, b, p):
            return (b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0])
        area = edge(*vertices)
        if area == 0:
            continue
        if area < 0:
            vertices[1], vertices[2] = vertices[2], vertices[1]
            area = -area
        a, b, c = vertices
        for y in range(h):
            for x in range(w):
                p = F(2*x+1, 2), F(2*y+1, 2)
                weights = [edge(b,c,p), edge(c,a,p), edge(a,b,p)]
                edges = [(b,c), (c,a), (a,b)]
                covered = all(e > 0 or e == 0 and (v[1] < u[1] or
                    v[1] == u[1] and v[0] > u[0]) for e,(u,v) in zip(weights,edges))
                if covered:
                    channels = []
                    for k in range(2,5):
                        value = sum(weights[j]*vertices[j][k] for j in range(3))/area + F(1,2)
                        channels.append(value.numerator // value.denominator)
                    pixels[y*w+x] = tuple(channels)
    return f'P6\n{w} {h}\n255\n'.encode() + bytes(ch for p in pixels for ch in p)


if __name__ == '__main__':
    sys.stdout.buffer.write(render(sys.stdin.read()))
