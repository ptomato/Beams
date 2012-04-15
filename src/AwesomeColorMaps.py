import numpy as N
from chaco.api import ColorMapper

def _rotate(x, y, angle):
    r, theta = N.hypot(x, y), N.arctan2(y, x)
    theta += angle
    return r * (N.cos(theta), N.sin(theta))

def isoluminant(rng, num_cycles=1, num_colors=256, reverse=False, **traits):
    """
    Generator function for a Chaco color scale that cycles through the hues
    @num_cycles times, while maintaining monotonic luminance (i.e., if it is
    printed in black and white, then it will be perceptually equal to a linear
    grayscale.
    
    Ported from the Matlab(R) code from: McNames, J. (2006). An effective color
    scale for simultaneous color and gray-scale publications. IEEE Signal
    Processing Magazine 23(1), 82--87.
    """
    
    # Triangular window function
    window = N.sqrt(3.0) / 8.0 * N.bartlett(num_colors)
    
    # Independent variable
    t = N.linspace(N.sqrt(3.0), 0.0, num_colors)
    
    # Initial values
    operand = (t - N.sqrt(3.0) / 2.0) * num_cycles * 2.0 * N.pi / N.sqrt(3.0)
    r0 = t
    g0 = window * N.cos(operand)
    b0 = window * N.sin(operand)
    
    # Convert RG to polar, rotate, and convert back
    r1, g1 = _rotate(r0, g0, N.arcsin(1.0 / N.sqrt(3.0)))
    b1 = b0
    
    # Convert RB to polar, rotate, and convert back
    r2, b2 = _rotate(r1, b1, N.pi / 4.0)
    g2 = g1
    
    # Ensure finite precision effects don't exceed unit cube boundaries
    r = r2.clip(0.0, 1.0)
    g = g2.clip(0.0, 1.0)
    b = b2.clip(0.0, 1.0)
    
    the_map = N.vstack((r, g, b)).T
    return ColorMapper.from_palette_array(the_map[::-1 if reverse else 1],
        range=rng, **traits)

def awesome(rng, **traits):
    """
    Generator function for a Chaco color scale that has low-intensity contrast.
    """
    return ColorMapper.from_palette_array(
	    N.loadtxt('../data/awesomecolormap.csv', delimiter=','),
	    range=rng, **traits)
