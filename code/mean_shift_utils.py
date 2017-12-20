import math
import numpy as np
from gaussian_kde import gaussian_kde

def euclidean_dist(pointA, pointB):
    if(len(pointA) != len(pointB)):
        raise Exception("expected point dimensionality to match")
    total = float(0)
    for dimension in range(0, len(pointA)):
        total += (pointA[dimension] - pointB[dimension])**2
    return math.sqrt(total)

def gaussian_kernel(distance, bandwidth,**kwargs):
    val = (1/(bandwidth*math.sqrt(2*math.pi))) * np.exp(-0.5*((distance / bandwidth))**2)
    return val

def gaussian_kernel_weighted(distance, bandwidth, **kwargs):
    """ATTENTION: 'weights' parameter should already be normalized"""
    val = kwargs['weights'] * (1/(bandwidth*math.sqrt(2*math.pi))) * np.exp(-0.5*((distance / bandwidth))**2)
    return val
    