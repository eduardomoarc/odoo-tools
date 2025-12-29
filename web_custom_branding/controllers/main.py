# -*- coding: utf-8 -*-
import base64
import json

from odoo import http
from odoo.http import request
from odoo.tools import ustr, file_open
from odoo.addons.web.controllers.webmanifest import WebManifest


class WebManifestCustom(WebManifest):

    def _get_pwa_icon_url(self, size):
        """
        Get PWA icon URL from attachment or return default static path.
        """
        ICP = request.env['ir.config_parameter'].sudo()
        # size is like "192" or "512"
        attachment_id = ICP.get_param(f'web.pwa_icon_{size}', False)

        if attachment_id:
            # Return the attachment URL
            return f'/web/image/{attachment_id}'

        # Default to custom branding icons from static folder
        return f'/web_custom_branding/static/img/pwa-icon-{size}x{size}.png'

    @http.route('/web/manifest.webmanifest', type='http', auth='public', methods=['GET'])
    def webmanifest(self):
        """
        Returns a WebManifest with custom branding.
        Overrides the default Odoo manifest to use custom icons and name.
        """
        ICP = request.env['ir.config_parameter'].sudo()
        web_app_name = ICP.get_param('web.web_app_name', 'Odoo')

        # Get custom colors or use defaults
        background_color = ICP.get_param('web.pwa_background_color', '#FFFFFF')
        theme_color = ICP.get_param('web.pwa_theme_color', '#FFFFFF')

        manifest = {
            'name': web_app_name,
            'short_name': web_app_name,
            'scope': '/web',
            'start_url': '/web',
            'display': 'standalone',
            'background_color': background_color,
            'theme_color': theme_color,
            'prefer_related_applications': False,
        }

        # Build icons list using attachment URLs or static files
        icon_configs = [
            {'size': '192', 'dimensions': '192x192'},
            {'size': '512', 'dimensions': '512x512'},
        ]

        manifest['icons'] = [{
            'src': self._get_pwa_icon_url(cfg['size']),
            'sizes': cfg['dimensions'],
            'type': 'image/png',
        } for cfg in icon_configs]

        manifest['shortcuts'] = self._get_shortcuts()
        body = json.dumps(manifest, default=ustr)
        response = request.make_response(body, [
            ('Content-Type', 'application/manifest+json'),
        ])
        return response

    def _icon_path(self):
        """Override to use custom icon for offline page"""
        return 'web_custom_branding/static/img/pwa-icon-192x192.png'

    @http.route('/web/offline', type='http', auth='public', methods=['GET'])
    def offline(self):
        """Returns the offline page with custom icon"""
        ICP = request.env['ir.config_parameter'].sudo()
        attachment_id = ICP.get_param('web.pwa_icon_192', False)

        if attachment_id:
            attachment = request.env['ir.attachment'].sudo().browse(int(attachment_id))
            if attachment.exists():
                odoo_icon = attachment.datas.decode('utf-8') if isinstance(attachment.datas, bytes) else attachment.datas
            else:
                odoo_icon = self._get_default_icon_base64()
        else:
            odoo_icon = self._get_default_icon_base64()

        return request.render('web.webclient_offline', {
            'odoo_icon': odoo_icon
        })

    def _get_default_icon_base64(self):
        """Get default icon as base64."""
        try:
            with file_open('web_custom_branding/static/img/pwa-icon-192x192.png', 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception:
            with file_open('web/static/img/odoo-icon-192x192.png', 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')