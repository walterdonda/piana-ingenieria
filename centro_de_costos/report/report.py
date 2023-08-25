from odoo import api, models
from datetime import date, datetime

class ReportCentroDeCostos(models.Model):
    _name = 'report.centro_de_costos.report_detalle_centro_de_costos'
    _description = 'reporte_centro_de_costos'

    @api.model
    def _get_report_values(self, docids, data=None):
        
        docs = self.env["account.analytic.account"].browse(docids)
        formatted_date = datetime.now().strftime('%Y-%m-%d')  # Formatea la fecha como "YYYY-MM-DD"
        docsargs={
            "docs": docs,
            "fecha": formatted_date,
        }

        return docsargs
    