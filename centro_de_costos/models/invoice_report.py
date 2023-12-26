# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from functools import lru_cache


class InvoiceReport(models.Model):
    _name = "centro_de_costos.invoice.report"
    _description = "Reporte de facturas y pagos en centro de costos"
    _auto = False
    _readonly = True

    # Defino los campos que se obtienen de la vista SQL
    move_name = fields.Char(string="Documento")
    partner_name = fields.Char(string="Partner")
    move_id = fields.Many2one('account.move', string="Move")
    move_type = fields.Selection([
        ('out_invoice', 'Factura cliente'),
        ('in_invoice', 'Factura proveedor'),
        ('out_refund', 'Nota de crédito cliente'),
        ('in_refund', 'Nota de crédito proveedor'),
    ], string="Tipo")

    date = fields.Date(string="Date")
    invoice_date = fields.Date(string="Fecha de factura")
    payment_date = fields.Date(string="Fecha de pago total")
    partner_id = fields.Many2one('res.partner', string="Partner")
    journal_id = fields.Many2one('account.journal', string="Diario")

    name = fields.Char(string="Name")
    afip_responsibility_type_id = fields.Many2one(
        'l10n_ar.afip.responsibility.type', string="AFIP Responsibility Type")
    document_type_id = fields.Many2one(
        'l10n_latam.document.type', string="Tipo documento")
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('posted', 'Confirmada'),
        ('cancel', 'Cancelada')
    ], string="State")
    payment_state = fields.Selection(selection=[
        ('not_paid', 'No pagado'),
        ('in_payment', 'Parcialmente pagado'),
        ('paid', 'Pagado')
    ], string='Estado de pago', readonly=True)
    centro_costo = fields.Many2one(
        'account.analytic.account', string='Centro de costos')
    credit = fields.Float(string='Crédito')
    debit = fields.Float(string='Débito')

    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, self._table)
        query = """
                SELECT
                    aml.id,
                    am.name as move_name,
                    rp.name as partner_name,
                    am.id as move_id,
                    am.move_type,
                    am.date,
                    am.invoice_date,
                    am.payment_state,
                    am.payment_date,
                    am.partner_id,
                    am.journal_id,
                    am.name,
                    am.state,
                    aml.analytic_account_id as centro_costo,
                    aml.credit,
                    aml.debit
                    
                FROM
                    account_move_line aml
                LEFT JOIN
                    account_move as am
                    ON aml.move_id = am.id
                LEFT JOIN
                    res_partner AS rp
                    ON rp.id = am.partner_id
                LEFT JOIN
                    account_analytic_account AS aa
                    ON aa.id = aml.analytic_account_id
                WHERE
                    am.move_type in ('out_invoice', 'in_invoice', 'out_refund', 'in_refund')
                    and aml.analytic_account_id is not NULL
                    and am.state = 'posted'
                        """
        sql = """CREATE or REPLACE VIEW %s as (%s)""" % (self._table, query)
        cr.execute(sql)
