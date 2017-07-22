from lmfdb.base import getDBConnection
from sage.all import ZZ, PowerSeriesRing, prime_range, previous_prime, gcd

def populate_dirichlet_coefficients(L, maxp = 100):
    '''
    (Use L['euler_factors'] to) Populate L['dirichlet_coefficients'] if
    L['dirichlet_coefficients'] doesn't exist.

    '''
    if 'dirichlet_coefficients' in L:
        return

    R = PowerSeriesRing(ZZ, 'x', ZZ(maxp).nbits())
    x = R.gen()
    coeffs = [0] * maxp
    coeffs[0] = 1

    for (p, factor) in zip(prime_range(maxp), L['euler_factors']):
        f = 1/R(factor)
        pp = p
        k = 1
        while pp < maxp:
            coeffs[pp - 1] = f[k]
            pp = pp*p
            k = k + 1

    if p != previous_prime(maxp):
        coeffs = coeffs[:p]

    maxcoeff = len(coeffs)
    for n1 in range(1, maxcoeff + 1):
        for n2 in range(1, maxcoeff + 1):
            if gcd(n1, n2) != 1:
                continue
            if n1*n2 <= maxcoeff:
                coeffs[n1*n2 - 1] = coeffs[n1-1] * coeffs[n2-1]

    L['dirichlet_coefficients'] = coeffs

def getLfunction(id):
    '''
    Takes an identifier for an L function and returns two dictionaries with a
    bunch of attributes filled. The first dictionary is for the L-function
    requested and the second is for the conjugate of that L-function, which
    might be the same as the first if the L-function is self-dual.

    Returns (None, None) if nothing is found.

    We first try to search for id as a url in the instances collection, and if
    there is nothing there we search for id in the Lhash field in the
    Lfunctions collection.

    so getLfunction("EllipticCurve/Q/11/a") works, as does
    getLfunction("1428752966040989219").
    '''
    LFDB = getDBConnection().Lfunctions

    result = LFDB.instances.find_one({'url' : id})
    if result is None:
        Lhash = id
    else:
        Lhash = result['Lhash']

    lfunction = LFDB.Lfunctions.find_one({'Lhash' : Lhash})
    if lfunction is None:
        return None, None
    if lfunction['self_dual']:
        conjugate = lfunction
    else:
        conjugate = LFDB.Lfunctions.find_one({'Lhash' : lfunction['conjugate']})

    instances = [x['url'] for x in LFDB.instances.find({'Lhash' : Lhash})]
    instances2 = [x['url'] for x in LFDB.instances.find({'Lhash' : conjugate['Lhash']})]

    lfunction['instances'] = instances
    conjugate['instances'] = instances2

    populate_dirichlet_coefficients(lfunction)
    populate_dirichlet_coefficients(conjugate)
    return lfunction, conjugate
