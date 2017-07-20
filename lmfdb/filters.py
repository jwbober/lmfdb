from base import app

@app.template_filter('floatpairtocomplexstring')
def float_pair_to_complex_string(z):
    x,y = z
    if y == 0:
        return '{}'.format(x)
    if y < 0:
        return '{} - i{}'.format(x, abs(y))
    else:
        return '{} + i{}'.format(x, y)

@app.template_filter('cremonalettercode')
def cremonalettercode(x):
    from sage.databases.cremona import cremona_letter_code
    return cremona_letter_code(x)
