from flask import render_template, url_for, redirect, request, make_response
from lmfdb.LDB import LDBpage
import lmfdb.LDB.typesetting
from sage.all import spline, plot
from lmfdb.LDB.dbinterface import getLfunction

import os
import tempfile

import re

@LDBpage.route("/<path:instance>")
def route(instance):
    lfunction, conjugate = getLfunction(instance)
    if lfunction is None:
        return "Not found"

    sign_string = ''
    if 'sign_arg' in lfunction:
        sign_string = r'$e({})$'.format(lfunction['sign_arg'])
    else:
        sign_string = r'${}$'.format(lfunction['root_number'])
    properties = [
            ('Degree',  str(lfunction['degree'])),
            ('Conductor', str(lfunction['conductor'])),
            ('Sign', sign_string),
            ('Self-dual', str(lfunction['self_dual'])),
            ('Motivic Weight', str(lfunction['motivic_weight']))
                ]

    origins = [(url, r'/' + url) for url in lfunction['instances']]

    return render_template("Lfunction_from_DB.html",
            L = lfunction,
            properties2 = properties,
            origins = origins
            )

@LDBpage.route("/plot/<path:instance>")
def Lplot(instance):
    xmin = request.args.get('xmin', -30, float)
    xmax = request.args.get('xmax', 30, float)
    width = request.args.get('width', 10.0, float)
    height = request.args.get('height', 5.0, float)
    if width > 75:
        width = 75.0
    if height  > 75:
        height = 75.0

    lfunction, conjugate = getLfunction(instance)
    if lfunction is None:
        return "Not found"
    ploty = list(reversed(conjugate['plot_values'])) + lfunction['plot_values'][1:]

    dx = lfunction['plot_delta']
    dx2 = conjugate['plot_delta']
    plotx = [n * dx2 for n in range(-len(conjugate['plot_values']) + 1, 1)] + \
                                [n * dx  for n in range(1, len(lfunction['plot_values']))]

    #P = plot(spline(zip(plotx, ploty)), xmin=plotx[0], xmax=plotx[-1])
    P = plot(spline(zip(plotx, ploty)), xmin=xmin, xmax=xmax)

    filename = tempfile.mktemp(suffix='.png')
    P.save(filename, figsize=[width,height])
    data = file(filename).read()
    os.remove(filename)

    response = make_response(data)
    response.headers['Content-type'] = 'image/png'
    return response
