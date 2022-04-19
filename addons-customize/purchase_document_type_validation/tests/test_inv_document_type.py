from odoo.tests.common import TransactionCase
from odoo.tests.common import Form
from odoo.exceptions import AccessError


class TestSaleDocumentType(TransactionCase):

    def setUp(self):
        super(TestSaleDocumentType, self).setUp()
        self.inv_document_type_model = self.env['l10n_latam.document.type']
        self.res_users = self.env['res.users']
        self.purchase_account = self.env['account.account'].search([('code', '=', '6111000')])
        self.currency_pen = self.env['res.currency'].search([('name', '=', 'PEN')])
        self.partner_id = self.env ['res.partner'].create({
            'name': 'franco',
        })
        self.journal_id = self.env['account.journal'].create({
            'name': 'Diario',
            'type': 'purchase',
            'default_account_id': self.purchase_account.id,
            'code': 'test',
            'currency_id': self.currency_pen.id,
        })
        self.document_attrs = {
            'code': '10',
            'name': 'Factura',
            'country_id': self.env.ref('base.pe').id,
        }
        self.document_attrs_purchase = {
            'code': '10',
            'name': 'Factura',
            'country_id': self.env.ref('base.pe').id,
            'prefix_length_validation' : 'equal',
            'prefix_long': 4,
            'prefix_validation': 'letters',
            'correlative_length_validation' : 'equal',
            'correlative_long': 8,
            'correlative_validation': 'letters'
        }
        
    def create_inv_document_type(self, **kwargs):
        inv_document = self.inv_document_type_model.create({
            'code': kwargs.get('code'),
            'name': kwargs.get('name'),
            'country_id': kwargs.get('country_id'),

        })
        if kwargs.get('country_id'):
            inv_document.update({
                'prefix_length_validation': kwargs.get('prefix_length_validation'),
                'prefix_long': kwargs.get('prefix_long'),
                'prefix_validation': kwargs.get('prefix_validation'),
                'correlative_length_validation': kwargs.get('correlative_length_validation'),
                'correlative_long': kwargs.get('correlative_long'),
                'correlative_validation': kwargs.get('correlative_validation'),
            })
        return inv_document
    
    def create_res_users_by_group(self, groups, nro):
        user = self.res_users.create({
            'login': 'test_user%d' % nro,
            'name': 'Usuario%d - T' % nro,
            'email': 'usert%d@example.com' % nro,
            'notification_type': 'email',
            'groups_id': [(6, 0, groups)]
        })
        return user

    def test_01_create_inv_document_type(self):
        document1 = self.create_inv_document_type(**self.document_attrs)        
        self.assertTrue(document1)
        print('------------TEST OK - CREATE------------')

    def test_02_onchange_invoice_purchase_document_type_validate_reference(self):
        invoice_form_purchase = Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        document = self.create_inv_document_type(**self.document_attrs_purchase)
        invoice_form_purchase.partner_id = self.partner_id
        invoice_form_purchase.journal_id = self.journal_id
        invoice_form_purchase.l10n_latam_document_type_id = document
        prefix_val = '1234'
        suffix_val = 'TST01922'
        invoice_form_purchase.ref = prefix_val + '-' + suffix_val
        invoice_form_purchase.save()
        self.assertEqual(invoice_form_purchase.error_dialog,'')
        print('------------TEST OK - VALIDATE ------------')

    def test_03_inv_document_type_permissions(self):
        
        document = self.create_inv_document_type(**self.document_attrs)
        group_account_manager = self.env.ref('account.group_account_manager')

        # set a different user(account role) to prove permissions
        user_account = self.create_res_users_by_group([group_account_manager.id], 1)

        # should do
        document.with_user(user_account).read()
        document.with_user(user_account).write({'name': 'prueba - account'})
        print('------------TEST OK - USER ACCOUNT------------')

        # set a different user to prove permissions
        user = self.create_res_users_by_group([], 2)

        # shouldn't do
        self.assertRaises(AccessError, document.with_user(user).write, {'name': 'prueba - normal'})
        self.assertRaises(AccessError, document.with_user(user).unlink)

        # should do
        document.with_user(user).read()
        print('------------TEST OK - NORMAL USER------------')