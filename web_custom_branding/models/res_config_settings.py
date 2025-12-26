# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    web_title = fields.Char(
        default="Odoo",
        string="Window Title or tab title",
        config_parameter="web_title",
    )

    web_app_name = fields.Char(
        string="PWA App Name",
        help="The name displayed when installing the app (PWA)",
        config_parameter="web.web_app_name",
        default="Odoo",
    )

    pwa_icon = fields.Binary(
        string="PWA Icon",
        help="Icon for the Progressive Web App (recommended: 512x512 PNG)",
    )

    pwa_theme_color = fields.Char(
        string="PWA Theme Color",
        help="Theme color for the PWA (hex format, e.g., #714B67)",
        config_parameter="web.pwa_theme_color",
        default="#714B67",
    )

    pwa_background_color = fields.Char(
        string="PWA Background Color",
        help="Background color for the PWA splash screen (hex format)",
        config_parameter="web.pwa_background_color",
        default="#FFFFFF",
    )

    @api.model
    def get_web_title(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        web_title = ir_config.get_param("web_title", default="")
        return {"web_title": web_title}

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        pwa_icon = ICP.get_param('web.pwa_icon', False)
        if pwa_icon:
            res['pwa_icon'] = pwa_icon
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        if self.pwa_icon:
            # Store the icon as base64 in ir.config_parameter
            if isinstance(self.pwa_icon, bytes):
                icon_data = self.pwa_icon.decode('utf-8')
            else:
                icon_data = self.pwa_icon
            ICP.set_param('web.pwa_icon', icon_data)
        else:
            # If icon is cleared, remove the parameter
            ICP.set_param('web.pwa_icon', False)