from flask import render_template, url_for, redirect, request
from lmfdb.embedded_modular_forms import embedded_mfs_page
from lmfdb.base import getDBConnection

from sage.databases.cremona import class_to_int as cremona_to_int
from sage.databases.cremona import cremona_letter_code

import string

import re

credit_string = "Jonathan Bober"

#@embedded_mfs_page.route('/<int:level>/<int:weight>/<int:chi>/<orbit_or_number>')
#def form_or_orbit_page(level, weight, chi, orbit_or_number):
#    if orbit_or_number.isdigit():
#        return render_single_mf(level, weight, chi, int(orbit_or_number))
#    else:
#        return render_single_orbit(level, weight, chi, orbit_or_number)

@embedded_mfs_page.route("/<int:level>/<int:weight>/<int:chi>/")
def level_weight_chi_page(level, weight, chi):
    orbitsdb = getDBConnection().embedded_mfs.hecke_orbits
    orbits = orbitsdb.find({'level' : level, 'weight' : weight, 'chi' : chi})
    orbits = list(orbits)
    labelled = False
    if len(orbits) != 0 and orbits[0]['orbitnumber'] != 0:
        labelled = True
    return render_template("level_weight_chi.html", orbits=orbits,
                                                    level=level,
                                                    weight=weight,
                                                    chi=chi,
                                                    labelled=labelled)

@embedded_mfs_page.route("/<int:level>/<int:weight>/")
def Gamma1_page(level, weight):
    orbitsdb = getDBConnection().embedded_mfs.hecke_orbits
    orbits = orbitsdb.find({'level' : level, 'weight' : weight}).sort("chi")
    def tableentryprinter(orbit):
        level = orbit['level']
        weight = orbit['weight']
        chi = orbit['chi']
        if orbit['orbitnumber'] != 0:
            letterlabel = cremona_letter_code(orbit['orbitnumber'] - 1)
            url = url_for('.single_orbit_page', level=level, weight=weight, chi=chi, orbit=letterlabel)
            orbittext = r'''<a href='{}'>{}.{}.{}.{}</a>'''.format(url, level, weight, chi, letterlabel)
        else:
            orbittext = r'''{}.{}.{}.{}'''.format(level, weight, chi, orbit['j'])

        if orbit['poly'] == '':
            polytext = "Degree {}".format(orbit['degree'])
        else:
            polytext = re.sub(r"\^(\d+)", r"^{\1}", orbit['poly'])
            polytext = polytext.replace("*", "")
            if len(polytext) > 200:
                A = string.find(polytext, "}", 100)
                B = string.rfind(polytext, "}", 0, -100)
                polytext = polytext[:A+1] + " + \cdots " + polytext[B+1:]
            polytext = "${}$".format(polytext)
            #polytext = orbit['poly']

        tableentry = r'''<tr><td>{}</td><td>{}</td></tr>'''.format(orbittext, polytext)
        return tableentry

    return render_template("Gamma1.html", orbits=orbits,
                                          level=level,
                                          weight=weight,
                                          tableentryprinter=tableentryprinter)

@embedded_mfs_page.route('/<int:level>/<int:weight>/<int:chi>/<int:number>')
def render_single_mf(level, weight, chi, number):
    mfs = getDBConnection().embedded_mfs.mfs
    result = mfs.find_one({'level' : level, 'weight' : weight, 'chi' : chi, 'j' : number})
    if chi*chi % level == 1:
        real = True
    else:
        real = False
    return render_template('mf_display.html', mf=result, real=real)

@embedded_mfs_page.route('/<int:level>/<int:weight>/<int:chi>/<string:orbit>')
def single_orbit_page(level, weight, chi, orbit):
    # orbit is a cremona-style letter-label which we need to
    # convert into an integer to search the database

    orbits = getDBConnection().embedded_mfs.hecke_orbits
    mfs = getDBConnection().embedded_mfs.mfs

    orbit_number = int(cremona_to_int(orbit)) + 1
    letterlabel = cremona_letter_code(orbit_number - 1)
    orbitresult = orbits.find_one({'level' : level, 'weight' : weight, 'chi' : chi, 'orbitnumber' : orbit_number})
    embeddings = mfs.find({'level' : level, 'weight' : weight, 'chi' : {'$in' : orbitresult['chiorbit']}, 'heckeorbit' : orbit_number})

    return render_template('orbit_display.html', orbit=orbitresult, letterlabel = letterlabel, embeddings=embeddings)
