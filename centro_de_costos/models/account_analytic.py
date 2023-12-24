from odoo import api, fields, models
from odoo.exceptions import ValidationError
from pyxirr import xirr
from pyxirr import xnpv


class CentroDeCostos(models.Model):

    _inherit = "account.analytic.account"
    _description = "Centro de costo"
    name = fields.Char(
        string="Centro de costo", index=True, required=True, tracking=True
    )
    budget_project = fields.Monetary(
        string="Presupuesto proyectado",
        tracking=True,
        help="Presupuesto del proyecto",
    )

    balance = fields.Monetary(string="Margen bruto")

    margin_project = fields.Monetary(
        compute="_compute_margin_project",
        string="Margen de proyecto",
    )

    @api.depends("total_facturado", "total_facturado_proveedores")
    def _compute_margin_project(self):
        for record in self:
            record["margin_project"] = (
                record["total_facturado"] -
                record["total_facturado_proveedores"]
            )

    updatable_by_index = fields.Boolean(
        string="Actualizable por índice externo",
        tracking=True,
        help="Indica si el pendiente de facturar es actualizable por un índice",
        default=False,
    )

    def name_get(self):
        res = []
        for analytic in self:
            name = analytic.name
            if analytic.code:
                name = "[" + analytic.code + "] " + name
            if analytic.partner_id.commercial_partner_id.name:
                name = analytic.partner_id.commercial_partner_id.name + " - " + name
            res.append((analytic.id, name))
        return res

    def action_update_by_index(self):
        if self.updatable_by_index:
            raise ValidationError("Salida de la función actualizar")

    total_facturado = fields.Monetary(
        string="Total facturado", compute="_compute_total_facturado", store=True
    )

    @api.depends("line_ids")
    def _compute_total_facturado(self):
        for record in self:
            # Obtener las líneas de facturas de cliente relacionadas con la cuenta analítica
            lines = self.env["account.move.line"].search(
                [
                    ("analytic_account_id", "=", record.id),
                    ("journal_id.type", "=", "sale"),
                ]
            )
            # Resto de las facturas cliente las notas de crédito
            record.total_facturado = sum(lines.mapped(
                "credit")) - sum(lines.mapped("debit"))

    outstanding_invoice_amount = fields.Monetary(
        compute="_compute_outstanding_invoice_amount",
        string="Pendiente de facturación",
        search="search_outstanding_invoice_amount",
        inverse="inverse_outstanding_invoice_amount",
        store=True,
    )

    @api.depends("budget_project", "total_facturado")
    def _compute_outstanding_invoice_amount(self):
        for record in self:
            record["outstanding_invoice_amount"] = (
                record["budget_project"] - record["total_facturado"]
            )

    @api.depends("outstanding_invoice_amount", "total_facturado")
    def inverse_outstanding_invoice_amount(self):
        for record in self:
            record["budget_project"] = (
                record["outstanding_invoice_amount"] +
                record["total_facturado"]
            )

    def search_outstanding_invoice_amount(self, operator, value):
        return [("outstanding_invoice_amount", operator, value)]

    state = fields.Char(compute="_compute_state", string="Estado")

    @api.depends("outstanding_invoice_amount")
    def _compute_state(self):
        for record in self:
            if record["outstanding_invoice_amount"] <= 0:
                record["state"] = "Totalmente Facturado"
            else:
                record["state"] = "Pendiente de Facturar"

    total_facturado_proveedores = fields.Monetary(
        string="Total facturado a proveedores",
        compute="_compute_total_facturado_proveedores",
        store=True,
    )

    @api.depends("line_ids")
    def _compute_total_facturado_proveedores(self):
        for record in self:
            # Obtener las líneas de facturas de proveedor relacionadas con la cuenta analítica
            lines = self.env["account.move.line"].search(
                [
                    ("analytic_account_id", "=", record.id),
                    ("journal_id.type", "=", "purchase"),
                ]
            )
            # Calcular el total facturado a proveedores a partir de la suma de los montos de las líneas
            record.total_facturado_proveedores = sum(lines.mapped("debit"))

    tir_no_per = fields.Float(
        compute="_compute_rentabilidad", string="TIR.NO.PER",
        help="Calcula la tasa interna de retorno de un proyecto en función de una serie especificada de flujos de efectivo que no son necesariamente periódicos."
    )
    discount_rate = fields.Float(string="Tasa de descuento", default=0.15,
                                 help="Es el rendimiento mínimo que debe ofrecer un proyecto para que sea rentable su ejecución.")

    vna = fields.Monetary(compute="_compute_rentabilidad", string="Valor actual neto",
                          help="Calcula el valor actual neto de un proyecto en función de una serie de flujos de efectivo que no son necesariamente periódicos y de una tasa de descuento determinada.")

    @api.depends("line_ids", "discount_rate")
    def _compute_rentabilidad(self):
        for record in self:
            # invoice_reports.mapped(lambda r: (r.price_subtotal, r.move_id.payment_group_ids.payment_date))
            invoice_lines = self.env["account.move.line"].search(
                [
                    ("analytic_account_id", "=", record.id),
                ]
            )
            try:
                # Intento calcular la tasa de retorno de intervalos irregulares
                credit = invoice_lines.filtered(lambda r: r.credit != 0).mapped(
                    lambda r: (r.move_id.payment_date, r.credit))
                debit = invoice_lines.filtered(lambda r: r.debit != 0).mapped(
                    lambda r: (r.move_id.payment_date, (-1)*r.debit))
                cashflows = credit + debit
                tir = xirr(cashflows)
            except:
                tir = 0
            try:
                vna = xnpv(record.discount_rate, cashflows)
            except:
                vna = record.margin_project
            record.tir_no_per = tir
            record.vna = vna


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_date = fields.Date('Payment Date')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def reconcile(self):
        res = super(AccountMoveLine, self).reconcile()
        payment_date = None
        for rec in self:
            if rec.move_id.payment_id:
                payment_date = rec.move_id.payment_id.date
        for rec in self:
            if rec.move_id.move_type == 'out_invoice':
                rec.move_id.payment_date = payment_date
        return res
