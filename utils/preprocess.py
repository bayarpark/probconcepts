import numpy as np
from typing import List, Tuple
from sklearn.neighbors import KernelDensity
from scipy.signal import argrelextrema
from math import inf

get_intervals

def get_intervals(data  : List[float],
                  coef  : float = 1,
                  alpha : float = 0.05) -> List[Tuple[float, float]]: 
    
    """ 
    :param data:  list of target features for splitting to intervals
    :param coef:  coefficient for KDE bandwidth
    :param alpha: proportionality factor of intersection of intervals 
    
    :returns: list of tuples covering all feature values
    """
    
    if len(data) < 2:
        raise ValueError("Too few elements for splitting.")

    sorted_data = np.sort(np.array(data))

    # how to calculate bandwidth?
    """
    bandwidth = 0
    for i in range(len(sorted_data) - 1):
        step = sorted_data[i+1] - sorted_data[i]
        if step < bandwidth:
            bandwidth = step
    """
    
    min_elem = sorted_data[0]
    max_elem = sorted_data[-1]
    
    var = np.std(sorted_data)
    
    a = sorted_data.reshape(-1,1)
 
    kde = KernelDensity(bandwidth = var / coef, kernel='gaussian').fit(a)
    s = np.linspace(min_elem, max_elem, num = 200)
    e = kde.score_samples(s.reshape(-1,1))
    
    # getting locale mins of density functions
    arg_min, _ = argrelextrema(e, np.less)[0], argrelextrema(e, np.greater)[0] 
    mins = list(s[arg_min])
   
    # all intervals points
    points = [-inf] + [min_elem] + mins + [max_elem] + [inf]
    
    # non-crossing intervals
    # at least there are 3 intervals: (-ing, min), (min, max), (max +inf)
    intervals = [(points[i], points[i+1]) for i in range(len(points) - 1)] 
    
    # crossing intervals
    cross_intervals = []
    
    # interval=(a,b). Suppose that eps = (b-a) * alpha
    # adding (-inf, min+eps) 
    
    eps_l = abs((intervals[1][1] - intervals[1][0])*alpha)
    cross_intervals.append((-inf, min_elem+eps_l))
    
    # other intervals = (a-eps, b+eps)
    for interval in intervals[1:-1]:
        a = interval[0]
        b = interval[1]
        eps = abs((b - a)*alpha)
        cross_intervals.append((a-eps, b+eps))
    
    # adding (max-eps, +inf)
    
    eps_r = abs((intervals[-2][1] - intervals[-2][0])*alpha)
    cross_intervals.append((max_elem-eps_r, +inf))
    
    return cross_intervals