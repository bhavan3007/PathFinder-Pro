import math
from scipy.stats import norm

def calculate_probability(mean, sigma, target):
    z_score = (target - mean) / sigma
    probability = (norm.cdf(z_score))*100
    return z_score, probability
