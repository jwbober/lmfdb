# -*- coding: utf-8 -*-
from lmfdb.base import app
from flask import Blueprint

embedded_mfs_page = Blueprint("embedded_mfs", __name__, template_folder='templates', static_folder="static")

@embedded_mfs_page.context_processor
def body_class():
    return {'body_class': 'embedded_mfs'}

import main

assert main # silence pyflakes

app.register_blueprint(embedded_mfs_page, url_prefix="/EmbeddedModularForms")
