from sre_parse import State
from odoo import api, fields, models
from odoo.exceptions import ValidationError


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

    balance = fields.Monetary(string="Margen financiero")

    margin_project = fields.Monetary(
        compute="_compute_margin_project",
        string="Margen de proyecto",
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

    @api.depends("budget_project", "total_facturado_proveedores")
    def _compute_margin_project(self):
        for record in self:
            record["margin_project"] = (
                record["budget_project"] - record["total_facturado_proveedores"]
            )

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
                record["outstanding_invoice_amount"] + record["total_facturado"]
            )

    def search_outstanding_invoice_amount(self, operator, value):
        return [("outstanding_invoice_amount", operator, value)]

    state = fields.Char(compute="_compute_state", string="Estado")

    @api.depends("outstanding_invoice_amount")
    def _compute_state(self):
        for record in self:
            if record["outstanding_invoice_amount"] == 0:
                record["state"] = "Totalmente Facturado"
            else:
                record["state"] = "Pendiente de Facturar"

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
            record.total_facturado = sum(lines.mapped("credit")) - sum(
                lines.mapped("debit")
            )

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
