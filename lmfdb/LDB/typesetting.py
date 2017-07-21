from lmfdb.LDB import LDBpage
from lmfdb.characters.utils import url_character
from sage.all import ZZ
import re

def typeset_sign(L, fmt = 'arithmetic'):
    pass

def typeset_functionalequation(L, fmt = 'arithmetic'):
    template = r'''\begin{{align}} \Lambda(s) & = {signfactor}{levelfactor}{gammaR}{gammaC}\cdot L(s) \cr
                & = \Lambda({weight} - s)
                \end{{align}}'''
    if 'root_number' in L:
        root_number = L['root_number']
        if root_number == -1:
            signstr = '-'
        elif root_number == 1:
            signstr = ''
        else:
            signstr = str(root_number)

    level = L['conductor']
    if level == 1:
        levelfactor = ''
    else:
        levelfactor = r'{}^{{s/2}}'.format(level)

    gammaRs, gammaCs = L['gamma_factors']
    gammaRstr= ''
    gammaCstr= ''
    for mu in gammaRs:
        if mu == 0:
            gammaRstr += r'\Gamma_\R(s)'.format(mu)
        else:
            gammaRstr += r'\Gamma_\R(s + {})'.format(mu)
    for nu in gammaCs:
        if nu == 0:
            gammaCstr += r'\Gamma_\C(s)'.format(nu)
        else:
            gammaCstr += r'\Gamma_\C(s + {})'.format(nu)

    return template.format( signfactor = signstr,
                            levelfactor = levelfactor,
                            gammaR = gammaRstr,
                            gammaC = gammaCstr,
                            weight = L['motivic_weight'] + 1 )


def typeset_character(chistr):
    # expecting a string of the form modulus.number
    modulus, number = chistr.split('.')
    url = url_character(type='Dirichlet', modulus=modulus, number=number)
    return r'''<a href="{}">$\chi_{{{}}}({},\cdot)$</a>'''.format(url, modulus, number)

def typeset_dirichletseries(L):
    if 'coeff_info' in L:
        # this is to handle the case when the coefficients might
        # be specified as algebraic numbers
        #
        # We expect L['coeff_info'] to be a three-element list, where the first
        # element is polynomial, the second is a floating point approximation
        # to a root of that polynomial, and the third is a letter to use for
        # the polynomial.
        #
        # We have a hack here which essentially treats Dirichlet L-functions as
        # a special case, since for these the polynomial will always be of the
        # form x^n - 1 for some n.

        poly = L['coeff_info'][0]
        match = re.match(r"^x\^(\d+) - 1$", poly)
        if not match:
            raise NotImplementedError
        d = ZZ(match.group(1))
        coeff_string = '1 '
        for n, coeff in enumerate(L['dirichlet_coefficients'][1:]):
            exponent = ZZ(coeff.split('^')[1])
            argument = exponent/d
            if argument == 0:
                coeff_string += r' + ${}^{{-s}}$'.format(n + 2)
            elif argument == ZZ(1)/ZZ(2):
                coeff_string += r' - ${}^{{-s}}$'.format(n + 2)
            elif argument == ZZ(1)/ZZ(4):
                coeff_string += r' + $i \cdot {}^{{-s}}$'.format(n + 2)
            elif argument == ZZ(1)/ZZ(4):
                coeff_string += r' - $i \cdot{}^{{-s}}$'.format(n + 2)
            else:
                coeff_string += r'+ $\zeta^{{{}}}\cdot{}^{{-s}}$'.format(exponent, n+2)
        coeff_string += ' $\cdots$'
        return coeff_string
    else:
        # otherwise we treat the dirichlet coefficients entry as a simple list of numbers.
        #
        # the following is not very good...
        return ' + '.join(['${}\cdot {}^{{-s}}$'.format(coeff, n + 1) for (n, coeff) in enumerate(L['dirichlet_coefficients'])])

def typeset_zeros(L):
    return L['positive_zeros']

@LDBpage.context_processor
def extra_functions():
    return {'typeset_character' : typeset_character,
            'typeset_dirichletseries' : typeset_dirichletseries,
            'typeset_zeros' : typeset_zeros,
            'typeset_functionalequation' : typeset_functionalequation}
