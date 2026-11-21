import math, random
random.seed(7)
def inv(v, flipz=True):
    x,y,z = v; r2 = x*x+y*y+z*z
    return (x/r2, -y/r2, (-z if flipz else z)/r2)
def rotz(v, t):
    x,y,z = v; c,s = math.cos(t), math.sin(t)
    return (c*x - s*y, s*x + c*y, z)
def add(a,b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
def sub(a,b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def scl(a,s): return (a[0]*s, a[1]*s, a[2]*s)
def norm(a):
    l = math.sqrt(sum(c*c for c in a)); return tuple(c/l for c in a)
def invsum(q, n, flipz=True):
    S = (0.0,0.0,0.0)
    for k in range(n):
        t = 2*math.pi*k/n
        w = (math.cos(t), math.sin(t), 0.0)
        S = add(S, rotz(inv(sub(q, w), flipz), t))
    return add((1.0,0.0,0.0), scl(inv(S, flipz), n))
def mercator(d, n):
    x,y,z = d; r = math.sqrt(x*x+y*y+z*z)
    Z = max(-0.999999999, min(0.999999999, z/r)); Zn = math.tanh(n*math.atanh(Z))
    h = math.sqrt(max(0.0, 1-Zn*Zn)); p = math.atan2(y,x)*n; R = r**n
    return (R*h*math.cos(p), R*h*math.sin(p), R*Zn)
def dist(a,b): return math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))
for flipz in (True, False):
    print("reciprocal flips", "y and z" if flipz else "y only")
    for n in (2,3,4,5,8):
        worst_sphere = 0.0; worst_plane = 0.0; worst_len = 0.0
        for _ in range(400):
            d = norm((random.gauss(0,1), random.gauss(0,1), random.gauss(0,1)))
            g = invsum(d, n, flipz)
            worst_sphere = max(worst_sphere, dist(g, mercator(d, n)))
            worst_len = max(worst_len, abs(math.sqrt(sum(c*c for c in g)) - 1))
            r = random.uniform(0.2, 1.8); a = random.uniform(0, 2*math.pi)
            q = (r*math.cos(a), r*math.sin(a), 0.0)
            f = invsum(q, n, flipz)
            worst_plane = max(worst_plane, dist(f, (r**n*math.cos(n*a), r**n*math.sin(n*a), 0.0)))
        print(f"  n={n}: on unit sphere vs Mercator max err {worst_sphere:.2e}, |result|-1 max {worst_len:.2e}; in plane z=0 vs complex z^n max err {worst_plane:.2e}")
