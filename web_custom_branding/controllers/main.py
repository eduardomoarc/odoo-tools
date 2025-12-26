# -*- coding: utf-8 -*-
import base64
import json
import mimetypes

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import ustr, file_open
from odoo.addons.web.controllers.webmanifest import WebManifest


class WebManifestCustom(WebManifest):

    def _get_pwa_icon_data(self, size):
        """
        Get PWA icon data from config or return default custom icon path.
        Returns tuple (is_base64, data) where:
        - is_base64=True means data is base64 encoded image
        - is_base64=False means data is a file path
        """
        ICP = request.env['ir.config_parameter'].sudo()
        icon_param = ICP.get_param('web.pwa_icon', False)

        if icon_param:
            return (True, icon_param)

        # Default to custom branding icons if they exist
        return (False, f'web_custom_branding/static/img/pwa-icon-{size}.png')

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

        # Check if custom icon is configured
        pwa_icon = ICP.get_param('web.pwa_icon', False)

        if pwa_icon:
            # Use base64 icon served through a controller
            icon_sizes = ['192x192', '512x512']
            manifest['icons'] = [{
                'src': f'/web/pwa-icon/{size}',
                'sizes': size,
                'type': 'image/png',
            } for size in icon_sizes]
        else:
            # Use default custom branding icons from static folder
            icon_sizes = ['192x192', '512x512']
            manifest['icons'] = [{
                'src': f'/web_custom_branding/static/img/pwa-icon-{size}.png',
                'sizes': size,
                'type': 'image/png',
            } for size in icon_sizes]

        manifest['shortcuts'] = self._get_shortcuts()
        body = json.dumps(manifest, default=ustr)
        response = request.make_response(body, [
            ('Content-Type', 'application/manifest+json'),
        ])
        return response

    @http.route('/web/pwa-icon/<string:size>', type='http', auth='public', methods=['GET'])
    def pwa_icon(self, size):
        """
        Serve the PWA icon from the configured base64 image.
        """
        ICP = request.env['ir.config_parameter'].sudo()
        pwa_icon = ICP.get_param('web.pwa_icon', False)

        if pwa_icon:
            try:
                image_data = base64.b64decode(pwa_icon)
                response = request.make_response(image_data, [
                    ('Content-Type', 'image/png'),
                    ('Cache-Control', 'public, max-age=604800'),
                ])
                return response
            except Exception:
                pass

        # Fallback to default icon
        try:
            with file_open(f'web_custom_branding/static/img/pwa-icon-{size}.png', 'rb') as f:
                image_data = f.read()
                response = request.make_response(image_data, [
                    ('Content-Type', 'image/png'),
                    ('Cache-Control', 'public, max-age=604800'),
                ])
                return response
        except Exception:
            # Final fallback to Odoo default
            with file_open(f'web/static/img/odoo-icon-{size}.png', 'rb') as f:
                image_data = f.read()
                response = request.make_response(image_data, [
                    ('Content-Type', 'image/png'),
                ])
                return response

    def _icon_path(self):
        """Override to use custom icon for offline page"""
        ICP = request.env['ir.config_parameter'].sudo()
        pwa_icon = ICP.get_param('web.pwa_icon', False)

        if pwa_icon:
            # Will be handled by the offline controller
            return 'web_custom_branding/static/img/pwa-icon-192x192.png'

        return 'web_custom_branding/static/img/pwa-icon-192x192.png'

    @http.route('/web/offline', type='http', auth='public', methods=['GET'])
    def offline(self):
        """Returns the offline page with custom icon"""
        ICP = request.env['ir.config_parameter'].sudo()
        pwa_icon = ICP.get_param('web.pwa_icon', False)

        if pwa_icon:
            odoo_icon = pwa_icon
        else:
            try:
                with file_open('web_custom_branding/static/img/pwa-icon-192x192.png', 'rb') as f:
                    odoo_icon = base64.b64encode(f.read()).decode('utf-8')
            except Exception:
                with file_open('web/static/img/odoo-icon-192x192.png', 'rb') as f:
                    odoo_icon = base64.b64encode(f.read()).decode('utf-8')

        return request.render('web.webclient_offline', {
            'odoo_icon': odoo_icon
        })