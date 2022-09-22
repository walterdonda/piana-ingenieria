# -*- coding: utf-8 -*-
# from odoo import http


# class Piana-ingenieria(http.Controller):
#     @http.route('/piana-ingenieria/piana-ingenieria', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/piana-ingenieria/piana-ingenieria/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('piana-ingenieria.listing', {
#             'root': '/piana-ingenieria/piana-ingenieria',
#             'objects': http.request.env['piana-ingenieria.piana-ingenieria'].search([]),
#         })

#     @http.route('/piana-ingenieria/piana-ingenieria/objects/<model("piana-ingenieria.piana-ingenieria"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('piana-ingenieria.object', {
#             'object': obj
#         })
