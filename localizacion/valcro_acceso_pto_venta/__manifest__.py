{
    'name': 'Valcro Usuarios de Punto de venta permitidos v2',
    'version': '11.0.0.2.0',
    'category': 'Point of Sale',
    'license': 'AGPL-3',
    'summary': 'Acceso Restringido solo para usuarios a Ciertos puntos de venta v2',
    'author': "Ing. Darrell Sojo",
    'website': 'dsojo.tanfe@gmail.com/',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'security/ir_rule.xml',
        'views/res_users_view.xml',
    ],
    'installable': True,
    'application': True,
}
