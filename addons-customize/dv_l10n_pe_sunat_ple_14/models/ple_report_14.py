# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from ...dv_l10n_pe_sunat_ple.models.ple_report import get_last_day
from ...dv_l10n_pe_sunat_ple.models.ple_report import fill_name_data
from ...dv_l10n_pe_sunat_ple.models.ple_report import number_to_ascii_chr

from base64 import b64decode, b64encode
import datetime
from io import StringIO, BytesIO
import logging
_logging = logging.getLogger(__name__)

class PLEReport14(models.Model) :
	_name = 'ple.report.14'
	_description = 'PLE 14 - Estructura del Registro de Ventas'
	_inherit = 'ple.report.templ'
	
	year = fields.Integer(required=True)
	month = fields.Selection(selection_add=[], required=True)
	
	invoice_ids = fields.Many2many(comodel_name='account.move', string='Ventas', readonly=True)
	
	ple_txt_01 = fields.Text(string='Contenido del TXT 14.1')
	ple_txt_01_binary = fields.Binary(string='TXT 14.1')
	ple_txt_01_filename = fields.Char(string='Nombre del TXT 14.1')
	ple_xls_01_binary = fields.Binary(string='Excel 14.1')
	ple_xls_01_filename = fields.Char(string='Nombre del Excel 14.1')
	ple_txt_02 = fields.Text(string='Contenido del TXT 14.2')
	ple_txt_02_binary = fields.Binary(string='TXT 14.2', readonly=True)
	ple_txt_02_filename = fields.Char(string='Nombre del TXT 14.2')
	ple_xls_02_binary = fields.Binary(string='Excel 14.2', readonly=True)
	ple_xls_02_filename = fields.Char(string='Nombre del Excel 14.2')
	
	def get_default_filename(self, ple_id='140100', empty=False) :
		name = super().get_default_filename()
		name_dict = {
			'month': str(self.month).rjust(2,'0'),
			'ple_id': ple_id,
		}
		if empty :
			name_dict.update({
				'contenido': '0',
			})
		fill_name_data(name_dict)
		name = name % name_dict
		return name
	
	def update_report(self) :
		res = super().update_report()
		start = datetime.date(self.year, int(self.month), 1)
		end = get_last_day(start)
		#current_offset = fields.Datetime.context_timestamp(self, fields.Datetime.now()).utcoffset()
		#start = start - current_offset
		#end = end - current_offset
		invoices = self.env.ref('base.pe').id
		invoices = [
			('company_id','=',self.company_id.id),
			('company_id.partner_id.country_id','=',invoices),
			('move_type','in',['out_invoice','out_refund']),
			('state','=','posted'),
			('invoice_date','>=',str(start)),
			('invoice_date','<=',str(end)),
		]
		invoices = self.env[self.invoice_ids._name].search(invoices, order='invoice_date asc, name asc')
		self.invoice_ids = invoices
		return res
	
	def generate_report(self) :
		res = super().generate_report()
		lines_to_write = []
		lines_to_write_2 = []
		invoices = self.invoice_ids.sudo()
		for move in invoices :
			m_1 = []
			try :
				sunat_number = move.name
				sunat_number = sunat_number and ('-' in sunat_number) and sunat_number.split('-') or ['','']
				sunat_code = move.l10n_latam_document_type_code or ''
				sunat_partner_code = move.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code
				sunat_partner_vat = move.partner_id.vat
				sunat_partner_name = move.partner_id.name
				move_id = move.id
				invoice_date = move.invoice_date
				date_due = move.invoice_date_due
				#1-4
				#m_1.extend([periodo.strftime('%Y%m00'), str(number), ('A'+str(number).rjust(9,'0')), invoice.invoice_date.strftime('%d/%m/%Y')])
				m_1.extend([
					invoice_date.strftime('%Y%m00'),
					move.seat_number or '',
					('M'+str(move_id).rjust(9,'0')),
					invoice_date.strftime('%d/%m/%Y'),
				])
				#5
				if date_due :
					m_1.append(date_due.strftime('%d/%m/%Y'))
				else :
					m_1.append('')
				#6-9
				m_1.extend([
					sunat_code,
					sunat_number[0],
					sunat_number[1],
					'',
				])
				#10-13
				if sunat_partner_code and sunat_partner_vat and sunat_partner_name :
					m_1.extend([
						sunat_partner_code,
						sunat_partner_vat,
						sunat_partner_name,
						'',
					])
				else :
					m_1.extend(['', '', '', ''])
				#14-18
				m_1.extend([format(move.amount_untaxed, '.2f'), '', format(move.amount_tax, '.2f'), '', ''])
				#19-24
				m_1.extend(['', '', '', '', '0.00', '']) #ICBP
				#25-27
				m_1.extend([format(move.amount_total, '.2f'), '', ''])
				#28-31
				if sunat_code in ['07', '08'] :
					origin = (sunat_code == '07') and move.credit_origin_id or move.debit_origin_id
					origin_number = origin.name
					origin_number = origin_number and ('-' in origin_number) and origin_number.split('-') or ['', '']
					if origin.invoice_date and origin.l10n_latam_document_type_code:
						m_1.extend([origin.invoice_date.strftime('%d/%m/%Y'), origin.l10n_latam_document_type_code])
					else:
						m_1.extend(['', ''])
					m_1.extend(origin_number)
				else :
					m_1.extend(['', '', '', ''])
				#32-36
				m_1.extend(['', '', '', '1', ''])
				_logging.info('m_1')
				_logging.info(m_1)
			except Exception as e:
				_logging.info('error en lineaaaaaaaaaaaaaa66666666666 2253')
				_logging.info(e)
				m_1 = []
			if m_1 :
				lines_to_write.append('|'.join(m_1))
			m_2 = []
			if m_1 :
				#1-4
				#m_1.extend([
				#    invoice_date.strftime('%Y%m00'),
				#    move.seat_number or '',
				#    ('A'+str(move_id).rjust(9,'0')),
				#    invoice_date.strftime('%d/%m/%Y'),
				#])
				m_2.extend(m_1[0:4])
				#5
				#if date_due :
				#    m_1.append(date_due.strftime('%d/%m/%Y'))
				#else :
				#    m_1.append('')
				m_2.append(m_1[4])
				#6-9
				#m_1.extend([
				#    sunat_code,
				#    sunat_number[0],
				#    sunat_number[1],
				#    '',
				#])
				m_2.extend(m_1[5:9])
				#10-12
				#if sunat_partner_code and sunat_partner_vat and sunat_partner_name :
				#    m_1.extend([
				#        sunat_partner_code,
				#        sunat_partner_vat,
				#        sunat_partner_name,
				#    ])
				#else :
				#    m_1.extend(['', '', ''])
				m_2.extend(m_1[9:12])
				#13-14
				#m_1.extend([format(move.amount_untaxed, '.2f'), '', format(move.amount_tax, '.2f'), '', ''])
				m_2.extend([
					m_1[13],
					m_1[15],
				])
				#15-16
				#m_1.extend(['', '', '', '', '0.00', '']) #ICBP
				m_2.extend(m_1[22:24])
				#17-19
				#m_1.extend([format(move.amount_total, '.2f'), '', ''])
				m_2.extend(m_1[24:27])
				#20-23
				#if sunat_code in ['07', '08'] :
				#    origin = (sunat_code == '07') and move.credit_origin_id or move.debit_origin_id
				#    origin_number = origin.name
				#    origin_number = origin_number and ('-' in origin_number) and origin_number.split('-') or ['', '']
				#    m_1.extend([origin.invoice_date.strftime('%d/%m/%Y'), origin.l10n_latam_document_type_code])
				#    m_1.extend(origin_number)
				#else :
				#    m_1.extend(['', '', '', ''])
				m_2.extend(m_1[27:31])
				#32-36
				#m_1.extend(['', '', '', '1', ''])
				m_2.extend(m_1[32:])
				_logging.info('m_2')
				_logging.info(m_2)
			if m_2 :
				lines_to_write_2.append('|'.join(m_2))
		name_01 = self.get_default_filename(ple_id='140100', empty=bool(lines_to_write))
		lines_to_write.append('')
		txt_string_01 = '\r\n'.join(lines_to_write)
		dict_to_write = dict()
		if txt_string_01 :
			xlsx_file_base_64 = self._generate_xlsx_base64_bytes(lines_to_write, name_01[2:], headers=[
				'Periodo',
				'N??mero correlativo del mes o C??digo ??nico de la Operaci??n (CUO)',
				'N??mero correlativo del asiento contable',
				'Fecha de emisi??n del Comprobante de Pago',
				'Fecha de Vencimiento o Fecha de Pago',
				'Tipo de Comprobante de Pago o Documento',
				'N??mero serie del comprobante de pago o documento o n??mero de serie de la maquina registradora',
				'N??mero del comprobante de pago o documento o n??mero inicial o constancia de dep??sito',
				'N??mero final',
				'Tipo de Documento de Identidad del cliente',
				'N??mero de Documento de Identidad del cliente',
				'Apellidos y nombres, denominaci??n o raz??n social del cliente',
				'Valor facturado de la exportaci??n',
				'Base imponible de la operaci??n gravada',
				'Descuento de la Base Imponible',
				'Impuesto General a las Ventas y/o Impuesto de Promoci??n Municipal',
				'Descuento del Impuesto General a las Ventas y/o Impuesto de Promoci??n Municipal',
				'Importe total de la operaci??n exonerada',
				'Importe total de la operaci??n inafecta',
				'Impuesto Selectivo al Consumo',
				'Base imponible de la operaci??n gravada con el Impuesto a las Ventas del Arroz Pilado',
				'Impuesto a las Ventas del Arroz Pilado',
				'Impuesto al Consumo de las Bolsas de Pl??stico',
				'Otros conceptos, tributos y cargos que no forman parte de la base imponible',
				'Importe total del comprobante de pago',
				'C??digo de la Moneda',
				'Tipo de cambio',
				'Fecha de emisi??n del comprobante de pago o documento original que se modifica o documento referencial al documento que sustenta el cr??dito fiscal',
				'Tipo del comprobante de pago que se modifica',
				'N??mero de serie del comprobante de pago que se modifica o C??digo de la Dependencia Aduanera',
				'N??mero del comprobante de pago que se modifica o N??mero de la DUA',
				'Identificaci??n del Contrato o del proyecto',
				'Error tipo 1: inconsistencia en el tipo de cambio',
				'Indicador de Comprobantes de pago cancelados con medios de pago',
				'Estado que identifica la oportunidad de la anotaci??n o indicaci??n',
			])
			dict_to_write.update({
				'ple_txt_01': txt_string_01,
				'ple_txt_01_binary': b64encode(txt_string_01.encode()),
				'ple_txt_01_filename': name_01 + '.txt',
				'ple_xls_01_binary': xlsx_file_base_64.encode(),
				'ple_xls_01_filename': name_01 + '.xlsx',
			})
		else :
			dict_to_write.update({
				'ple_txt_01': False,
				'ple_txt_01_binary': False,
				'ple_txt_01_filename': False,
				'ple_xls_01_binary': False,
				'ple_xls_01_filename': False,
			})
		name_02 = self.get_default_filename(ple_id='140200', empty=bool(lines_to_write_2))
		lines_to_write_2.append('')
		txt_string_02 = '\r\n'.join(lines_to_write_2)
		if txt_string_02 :
			xlsx_file_base_64 = self._generate_xlsx_base64_bytes(lines_to_write_2, name_02[2:], headers=[
				'Periodo',
				'N??mero correlativo del mes o C??digo ??nico de la Operaci??n (CUO)',
				'N??mero correlativo del asiento contable',
				'Fecha de emisi??n del Comprobante de Pago',
				'Fecha de Vencimiento o Fecha de Pago',
				'Tipo de Comprobante de Pago o Documento',
				'N??mero serie del comprobante de pago o documento o n??mero de serie de la maquina registradora',
				'N??mero del comprobante de pago o documento o n??mero inicial o constancia de dep??sito',
				'N??mero final',
				'Tipo de Documento de Identidad del cliente',
				'N??mero de Documento de Identidad del cliente',
				'Apellidos y nombres, denominaci??n o raz??n social del cliente',
				'Valor facturado de la exportaci??n',
				'Base imponible de la operaci??n gravada',
				'Descuento de la Base Imponible',
				'Impuesto General a las Ventas y/o Impuesto de Promoci??n Municipal',
				'Descuento del Impuesto General a las Ventas y/o Impuesto de Promoci??n Municipal',
				'Importe total de la operaci??n exonerada',
				'Importe total de la operaci??n inafecta',
				'Impuesto Selectivo al Consumo',
				'Base imponible de la operaci??n gravada con el Impuesto a las Ventas del Arroz Pilado',
				'Impuesto a las Ventas del Arroz Pilado',
				'Impuesto al Consumo de las Bolsas de Pl??stico',
				'Otros conceptos, tributos y cargos que no forman parte de la base imponible',
				'Importe total del comprobante de pago',
				'C??digo de la Moneda',
				'Tipo de cambio',
				'Fecha de emisi??n del comprobante de pago o documento original que se modifica o documento referencial al documento que sustenta el cr??dito fiscal',
				'Tipo del comprobante de pago que se modifica',
				'N??mero de serie del comprobante de pago que se modifica o C??digo de la Dependencia Aduanera',
				'N??mero del comprobante de pago que se modifica o N??mero de la DUA',
				'Identificaci??n del Contrato o del proyecto',
				'Error tipo 1: inconsistencia en el tipo de cambio',
				'Indicador de Comprobantes de pago cancelados con medios de pago',
				'Estado que identifica la oportunidad de la anotaci??n o indicaci??n',
			])
   		
			dict_to_write.update({
				'ple_txt_02': txt_string_02,
				'ple_txt_02_binary': b64encode(txt_string_02.encode()),
				'ple_txt_02_filename': name_02 + '.txt',
				'ple_xls_02_binary': xlsx_file_base_64.encode(),
				'ple_xls_02_filename': name_02 + '.xlsx',
			})
		else :
			dict_to_write.update({
				'ple_txt_02': False,
				'ple_txt_02_binary': False,
				'ple_txt_02_filename': False,
				'ple_xls_02_binary': False,
				'ple_xls_02_filename': False,
			})
		dict_to_write.update({
			'date_generated': str(fields.Datetime.now()),
		})
		res = self.write(dict_to_write)
		return res
