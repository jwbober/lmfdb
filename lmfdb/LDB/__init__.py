# -*- coding: utf-8 -*-
from lmfdb.base import app
from flask import Blueprint

LDBpage = Blueprint("LDB", __name__, template_folder='templates', static_folder="static")

@LDBpage.context_processor
def body_class():
    return {'body_class': 'LDB'}

import main

assert main # silence pyflakes

app.register_blueprint(LDBpage, url_prefix="/LDB")
