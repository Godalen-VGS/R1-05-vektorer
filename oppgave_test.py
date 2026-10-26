"""Automatisk retting av R1-05-vektorer.

Hver sjekk i SJEKKER er én deltest, og poengene fordeles likt på dem.
De samme sjekkene ligger i "Test løsningen din"-cellen nederst i notebooken.
"""
import pytest

from notebook_loader import last_notebook

def naer(a, b, rel=1e-3):
    """Sant hvis tallet a er innenfor rel (relativt) av b."""
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if b == 0:
        return abs(a) < 1e-9
    return abs(a - b) <= rel * abs(b)


def S(tekst):
    """Gjør tekst om til et sympy-uttrykk, f.eks. S("x**2 - 1")."""
    import sympy
    return sympy.sympify(tekst, locals={n: sympy.Symbol(n) for n in ("N", "O", "Q", "S")})


def lik(a, b):
    """Sant hvis a og b er matematisk like.

    Lister og mengder sammenlignes uten hensyn til rekkefølge, tupler (koordinater) i rekkefølge.
    """
    import sympy
    if a is None:
        return False
    if isinstance(b, tuple):
        if not isinstance(a, (tuple, list, sympy.Tuple)) or len(a) != len(b):
            return False
        return all(lik(x, y) for x, y in zip(a, b))
    if isinstance(b, (list, set)):
        if isinstance(a, sympy.FiniteSet):
            a = list(a)
        if not isinstance(a, (list, tuple, set)) or len(a) != len(b):
            return False
        rest = list(a)
        for y in b:
            for i, x in enumerate(rest):
                if lik(x, y):
                    del rest[i]
                    break
            else:
                return False
        return True
    if isinstance(b, dict):
        if not isinstance(a, dict) or len(a) != len(b):
            return False
        a = {str(k): v for k, v in a.items()}
        return all(str(k) in a and lik(a[str(k)], v) for k, v in b.items())
    try:
        a, b = sympy.sympify(a), sympy.sympify(b)
    except (sympy.SympifyError, TypeError):
        return False
    vanlige = lambda u: u.subs({s: sympy.Symbol(s.name) for s in u.free_symbols})
    a, b = vanlige(a), vanlige(b)
    if isinstance(a, sympy.Set) or isinstance(b, sympy.Set):
        return a == b
    if getattr(b, "is_Relational", False):
        return a == b
    try:
        return sympy.simplify(a - b) == 0
    except TypeError:
        return a == b

oppgave = last_notebook("oppgave")

SJEKKER = [
    ('1_lengde', 'lengde([3, 4]) skal gi 5', 'naer(lengde([3, 4]), 5) and naer(lengde([1, 1]), 2**0.5)'),
    ('1_skalar', 'skalarprodukt([1, 2], [3, 4]) skal gi 11', 'naer(skalarprodukt([1, 2], [3, 4]), 11) and naer(skalarprodukt([2, -1], [1, 2]), 0)'),
    ('2_rett', 'vinkel([1, 0], [0, 1]) skal gi 90', 'naer(vinkel([1, 0], [0, 1]), 90)'),
    ('2_45', 'vinkel([1, 1], [1, 0]) skal gi 45', 'naer(vinkel([1, 1], [1, 0]), 45)'),
    ('2_stump', 'vinkel([1, 0], [-1, 1]) skal gi 135', 'naer(vinkel([1, 0], [-1, 1]), 135)'),
    ('3_ortogonal', 'er_ortogonal([2, -1], [1, 2]) skal gi True og er_ortogonal([1, 1], [1, 0]) False', 'er_ortogonal([2, -1], [1, 2]) == True and er_ortogonal([1, 1], [1, 0]) == False'),
    ('3_parallell', 'er_parallell([2, 4], [-1, -2]) skal gi True og er_parallell([1, 2], [2, 1]) False', 'er_parallell([2, 4], [-1, -2]) == True and er_parallell([1, 2], [2, 1]) == False'),
    ('4_mellom', 'vektor_mellom([1, 2], [5, 4]) skal gi [4, 2]', 'list(vektor_mellom([1, 2], [5, 4])) == [4, 2]'),
    ('4_linje', 'punkt_paa_linje([1, 2], [4, 2], 0.5) skal gi [3, 3]', 'all(naer(a, b) for a, b in zip(punkt_paa_linje([1, 2], [4, 2], 0.5), [3, 3]))'),
    ('6_kryss', 'skjaering([0, 0], [1, 1], [0, 4], [1, -1]) skal gi (2, 2)', 'all(naer(a, b) for a, b in zip(skjaering([0, 0], [1, 1], [0, 4], [1, -1]), [2, 2]))'),
    ('6_annet', 'skjaering([1, 0], [0, 1], [0, 3], [2, 1]) skal gi (1, 3.5)', 'all(naer(a, b) for a, b in zip(skjaering([1, 0], [0, 1], [0, 3], [2, 1]), [1, 3.5]))'),
    ('6_parallell', 'skjaering skal gi None for parallelle linjer', 'skjaering([0, 0], [1, 2], [1, 0], [2, 4]) is None and skjaering([0, 0], [1, 1], [0, 4], [1, -1]) is not None'),
]


@pytest.mark.parametrize(
    "beskrivelse,uttrykk", [s[1:] for s in SJEKKER], ids=[s[0] for s in SJEKKER]
)
def test_sjekk(beskrivelse, uttrykk):
    navnerom = {**vars(oppgave), "naer": naer, "lik": lik, "S": S}
    assert eval(uttrykk, navnerom), beskrivelse
