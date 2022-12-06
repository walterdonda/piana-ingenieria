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

    @api.depends("budget_project", "debit")
    def _compute_margin_project(self):
        for record in self:
            record["margin_project"] = record["budget_project"] - record["debit"]

    outstanding_invoice_amount = fields.Monetary(
        compute="_compute_outstanding_invoice_amount",
        string="Pendiente de facturación",
        search="search_outstanding_invoice_amount",
        inverse="inverse_outstanding_invoice_amount",
        store=True,
    )

    @api.depends("budget_project", "credit")
    def _compute_outstanding_invoice_amount(self):
        for record in self:
            record["outstanding_invoice_amount"] = (
                record["budget_project"] - record["credit"]
            )

    @api.depends("outstanding_invoice_amount", "credit")
    def inverse_outstanding_invoice_amount(self):
        for record in self:
            record["budget_project"] = (
                record["outstanding_invoice_amount"] + record["credit"]
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
