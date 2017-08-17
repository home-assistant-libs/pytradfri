from .const import (ATTR_LIGHT_COLOR_X as X, ATTR_LIGHT_COLOR_Y as Y)
KNOWN_XY = {
  2200: {X: 33135, Y: 27211},
  2700: {X: 30140, Y: 26909},
  4000: {X: 24930, Y: 24694},
}

def can_dekelvinize(kelvins):
    return min(KNOWN_XY.keys()) <= kelvins <= max(KNOWN_XY.keys())

def dekelvinize(kelvins):
    if kelvins in KNOWN_XY:
        return KNOWN_XY[kelvins]
    else:
        knowns = KNOWN_XY.keys()
        lower_k = max([k for k in knowns if k < kelvins])
        higher_k = min([k for k in knowns if k > kelvins])
        offset = (kelvins - lower_k) / (higher_k - lower_k)
        lower = KNOWN_XY[lower_k]
        higher = KNOWN_XY[higher_k]
        return {coord:  int(offset * higher[coord] + (1 - offset) * lower[coord]) for coord in [X, Y]}
