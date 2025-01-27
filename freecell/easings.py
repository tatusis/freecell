import math


def ease_out_quart(x: float) -> float:
    """Sharp acceleration and gradual deceleration animation"""
    return 1 - math.pow(1 - x, 5)
