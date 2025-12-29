# -*- coding: utf-8 -*-
import base64
import io

from PIL import Image

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

    def _resize_image(self, image_data, size):
        """Resize image to specified size (square)."""
        img = Image.open(io.BytesIO(base64.b64decode(image_data)))
        img = img.convert('RGBA')
        img = img.resize((size, size), Image.LANCZOS)
        output = io.BytesIO()
        img.save(output, format='PNG')
        return base64.b64encode(output.getvalue())

    def _create_pwa_icon_attachment(self, image_data, size, name=None):
        """Create or update PWA icon attachment for a specific size."""
        Attachment = self.env['ir.attachment'].sudo()
        attachment_name = name or f'pwa-icon-{size}x{size}.png'

        # Search for existing attachment
        attachment = Attachment.search([
            ('name', '=', attachment_name),
            ('res_model', '=', 'ir.ui.view'),
            ('res_id', '=', 0),
        ], limit=1)

        # Resize image to the target size
        resized_data = self._resize_image(image_data, size)

        if attachment:
            attachment.write({'datas': resized_data})
        else:
            attachment = Attachment.create({
                'name': attachment_name,
                'type': 'binary',
                'datas': resized_data,
                'mimetype': 'image/png',
                'public': True,
                'res_model': 'ir.ui.view',
                'res_id': 0,
            })

        return attachment.id

    @api.model
    def get_web_title(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        web_title = ir_config.get_param("web_title", default="")
        return {"web_title": web_title}

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        # Load the 512x512 icon for display in settings
        attachment_id = ICP.get_param('web.pwa_icon_512', False)
        if attachment_id:
            attachment = self.env['ir.attachment'].sudo().browse(int(attachment_id))
            if attachment.exists():
                res['pwa_icon'] = attachment.datas
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        if self.pwa_icon:
            # Get the image data
            if isinstance(self.pwa_icon, bytes):
                image_data = self.pwa_icon.decode('utf-8')
            else:
                image_data = self.pwa_icon

            # Create attachments for both sizes
            attachment_192_id = self._create_pwa_icon_attachment(image_data, 192)
            attachment_512_id = self._create_pwa_icon_attachment(image_data, 512)

            # Save attachment IDs in config parameters
            ICP.set_param('web.pwa_icon_192', attachment_192_id)
            ICP.set_param('web.pwa_icon_512', attachment_512_id)
        else:
            # If icon is cleared, remove the attachments and parameters
            for size in ['192', '512']:
                attachment_id = ICP.get_param(f'web.pwa_icon_{size}', False)
                if attachment_id:
                    attachment = self.env['ir.attachment'].sudo().browse(int(attachment_id))
                    if attachment.exists():
                        attachment.unlink()
                ICP.set_param(f'web.pwa_icon_{size}', False)