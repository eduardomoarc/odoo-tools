# -*- coding: utf-8 -*-
{
    'name': "Web Custom Branding",

    'summary': "Customization of Odoo branding elements",

    'description': """
        This module allows you to customize Odoo branding elements for a white-label experience:

        User Menu Customization:
        - Hides "My Odoo.com account" option
        - Hides "Documentation" link
        - Hides "Support" link

        Login Page:
        - Removes "Powered by Odoo" footer text

        Window Title:
        - Configurable custom window/browser tab title
        - Settings available in General Settings > Window section

        PWA (Progressive Web App):
        - Custom app name for browser installation
        - Custom PWA icon (replaces Odoo icon in browser install button)
        - Configurable theme color (browser toolbar)
        - Configurable background color (splash screen)
        - Settings available in General Settings > PWA section

        Settings Panel:
        - Hides the "About" section from General Settings

        Offline Page:
        - Custom offline message
    """,

    'author': "Eduardo Morón",

    'category': 'Website',
    'version': '17.0.1.0.0',
    'license': 'LGPL-3',

    'depends': ['base', 'web', 'base_setup'],
    "images": ["static/description/main_screen.png"],

    'data': [
        'views/res_config_settings_views.xml',
        'views/web_templates.xml',
        'views/webclient_offline.xml',
        'views/web_layout.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'web_custom_branding/static/src/js/custom_title.js',
            'web_custom_branding/static/src/js/user_menu.js',
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
}
