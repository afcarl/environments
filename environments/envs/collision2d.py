
class Segment(object):

    def __init__(self, xa, ya, xb, yb):
        if xa <= xb: # increasing abscissae
            self.xa, self.ya = xb, yb
            self.xb, self.yb = xa, ya
        else:
            self.xa, self.ya = xa, ya
            self.xb, self.yb = xb, yb
        self.x_min = min(xa, yb)
        self.x_max = max(xa, yb)
        self.y_min = min(ya, yb)
        self.y_max = max(ya, yb)


def near(a, b, rtol=1e-5, atol=1e-8):
    return abs(a - b) < (atol + rtol * abs(b))

def segment_intersection(s1, s2):
    """Return True if segment cross, False if parallel or otherwise."""
    if (s1.x_max < s2.x_min or s2.x_max < s1.x_min or
        s1.y_max < s2.y_min or s2.y_max < s1.y_min):
        return False

    a, b = s1.xb - s1.xa, s2.xa - s2.xb
    c, d = s1.yb - s1.ya, s2.ya - s2.yb
    e, f = s2.xa - s1.xa, s2.ya - s1.ya

    denom = float(a*d - b*c)
    if near(denom, 0): # parallel
        return False
    else:
        t = (e*d - b*f)/denom
        s = (a*f - e*c)/denom
        return 0<=t<=1 and 0<=s<=1
