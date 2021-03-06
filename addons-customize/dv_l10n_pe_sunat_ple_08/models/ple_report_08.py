# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from ...dv_l10n_pe_sunat_ple.models.ple_report import get_last_day
from ...dv_l10n_pe_sunat_ple.models.ple_report import fill_name_data
from ...dv_l10n_pe_sunat_ple.models.ple_report import number_to_ascii_chr

#import base64
from base64 import b64decode, b64encode
import datetime
from io import StringIO, BytesIO
#import pandas
import logging
_logging = logging.getLogger(__name__)

class PLEReport08(models.Model) :
	_name = 'ple.report.08'
	_description = 'PLE 08 - Estructura del Registro de Compras'
	_inherit = 'ple.report.templ'
	
	year = fields.Integer(required=True)
	month = fields.Selection(selection_add=[], required=True)
	
	bill_ids = fields.Many2many(comodel_name='account.move', string='Compras', readonly=True)
	
	# Normal
	ple_txt_01 = fields.Text(string='Contenido del TXT 8.1')
	ple_txt_01_binary = fields.Binary(string='TXT 8.1')
	ple_txt_01_filename = fields.Char(string='Nombre del TXT 8.1')
	ple_xls_01_binary = fields.Binary(string='Excel 8.1')
	ple_xls_01_filename = fields.Char(string='Nombre del Excel 8.1')

	# No domiciliado
	ple_txt_02 = fields.Text(string='Contenido del TXT 8.2')
	ple_txt_02_binary = fields.Binary(string='TXT 8.2', readonly=True)
	ple_txt_02_filename = fields.Char(string='Nombre del TXT 8.2')
	ple_xls_02_binary = fields.Binary(string='Excel 8.2', readonly=True)
	ple_xls_02_filename = fields.Char(string='Nombre del Excel 8.2')

	# Simplicado
	ple_txt_03 = fields.Text(string='Contenido del TXT 8.3')
	ple_txt_03_binary = fields.Binary(string='TXT 8.3', readonly=True)
	ple_txt_03_filename = fields.Char(string='Nombre del TXT 8.3')
	ple_xls_03_binary = fields.Binary(string='Excel 8.3', readonly=True)
	ple_xls_03_filename = fields.Char(string='Nombre del Excel 8.3')

	documento_compra_ids = fields.Many2many('l10n_latam.document.type', 'ple_report_l10n_latam_id', 'report_id', 'doc_id', string='Documentos a incluir', required=False, domain="[('sub_type', 'in', ['purchase'])]")
	
	def get_default_filename(self, ple_id='080100', tiene_datos=False) :
		name = super().get_default_filename()
		name_dict = {
			'month': str(self.month).rjust(2,'0'),
			'ple_id': ple_id,
		}
		if not tiene_datos :
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
		doc_type_ids = []
		for reg in self.documento_compra_ids:
			doc_type_ids.append(reg.id)

		bills = self.env.ref('base.pe').id
		bills = [
			('company_id','=',self.company_id.id),
			('company_id.partner_id.country_id','=',bills),
			('move_type','in',['in_invoice','in_refund']),
			('state','=','posted'),
			('date','>=',str(start)),
			('date','<=',str(end)),
		]
		if self.documento_compra_ids:
			bills.append(('l10n_latam_document_type_id', 'in', doc_type_ids))
		bills = self.env[self.bill_ids._name].search(bills, order='date asc, ref asc')
		self.bill_ids = bills
		return res
	
	def generate_report(self) :
		res = super().generate_report()
		lines_to_write_01 = []
		lines_to_write_02 = []
		lines_to_write_03 = []
		bills = self.bill_ids.sudo()
		peru = self.env.ref('base.pe')
		contador = 1
		fecha_inicio = datetime.date(self.year, int(self.month), 1)

		for move in bills :
			m_01 = []
			try :
				sunat_number = move.ref
				sunat_number = sunat_number and ('-' in sunat_number) and sunat_number.split('-') or ['','']
				sunat_code = move.l10n_latam_document_type_code or '00'
				sunat_partner_code = move.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code
				sunat_partner_vat = move.partner_id.vat
				sunat_partner_name = move.partner_id.name
				move_id = move.l10n_latam_document_number
				invoice_date = move.invoice_date
				date_due = move.invoice_date_due
				amount_untaxed = move.amount_untaxed
				amount_tax = move.amount_tax
				amount_total = move.amount_total
				#1-4
				#m_01.extend([periodo.strftime('%Y%m00'), str(number), ('A'+str(number).rjust(9,'0')), invoice.invoice_date.strftime('%d/%m/%Y')])
				m_01.extend([
					move.date.strftime('%Y%m00'),
					move.seat_number or '',
					('M'+str(1).rjust(9,'0')),
					invoice_date.strftime('%d/%m/%Y'),
				])
				contador = contador + 1
				#5
				if date_due :
					m_01.append(date_due.strftime('%d/%m/%Y'))
				else :
					m_01.append('')
				#6-10
				m_01.extend([
					sunat_code,
					sunat_number[0],
					'',
					sunat_number[1],
					'',
				])
				#11-13
				if sunat_partner_code and sunat_partner_vat and sunat_partner_name :
					m_01.extend([
						sunat_partner_code,
						sunat_partner_vat,
						sunat_partner_name,
					])
				else :
					m_01.extend(['', '', ''])
				#14-15
				total_sin_impuestos = abs(move.amount_untaxed_signed)
				total_impuestos = abs(move.amount_tax_signed)
				m_01.extend([format(total_sin_impuestos, '.2f'), format(total_impuestos, '.2f')])
				#16-23
				m_01.extend(['', '', '', '', '', '', '0.00', '']) #ICBP
				#24
				monto_total = abs(move.amount_total_signed)
				m_01.extend([format(monto_total, '.2f')])
				#25-26 (Codigo de moneda y tipo de cambio - son opcionales)
				m_01.extend([ '', ''])
				#27-31
				# notas credito
				if sunat_code in ['07'] :
					origin = move.reversed_entry_id
					origin_number = origin.ref
					origin_number = origin_number and ('-' in origin_number) and origin_number.split('-') or ['', '']
					#m_01.extend([origin.invoice_date.strftime('%d/%m/%Y'), origin.l10n_latam_document_type_code])
					if origin.invoice_date and origin.l10n_latam_document_type_code:
						m_01.extend([origin.invoice_date.strftime('%d/%m/%Y'), origin.l10n_latam_document_type_code])
					else:
						m_01.extend(['', ''])
					m_01.append(origin_number[0])
					m_01.append('')
					m_01.append(origin_number[1])
				# notas debito
				elif sunat_code in ['08'] :
					origin = move.debit_origin_id
					origin_number = origin.ref
					origin_number = origin_number and ('-' in origin_number) and origin_number.split('-') or ['', '']
					#m_01.extend([origin.invoice_date.strftime('%d/%m/%Y'), origin.l10n_latam_document_type_code])
					if origin.invoice_date and origin.l10n_latam_document_type_code:
						m_01.extend([origin.invoice_date.strftime('%d/%m/%Y'), origin.l10n_latam_document_type_code])
					else:
						m_01.extend(['', ''])
					m_01.append(origin_number[0])
					m_01.append('')
					m_01.append(origin_number[1])
				else :
					m_01.extend(['', '', '', '', ''])
				
				#32-33 (Datos para pago de detracciones)
				if False: #move.tiene_detraccion and move.pago_detraccion:
					m_01.extend([move.pago_detraccion.date.strftime('%d/%m/%Y'), move.pago_detraccion.transaction_number])
				else:
					m_01.extend(['', ''])
				#34 (Datos para pago de retencion)
				if False: #move.tiene_retencion:
					m_01.extend(['1'])
				else:
					m_01.extend([''])
				#35-38 
				m_01.extend(['', '', '', ''])
				#39-43
				codigo = '1'
				if invoice_date < fecha_inicio:
					codigo = '6'
				m_01.extend(['', '', '',codigo, ''])
				
				#m_01.extend(['', '', '', '', '', '', '', '', '', '', codigo, ''])
			except Exception as e:
				raise Warning('Ocurrio un inconveniente: %s' % str(e))
				m_01 = []
			
			if move.partner_id.country_id == peru:
				lines_to_write_01.append('|'.join(m_01))
			m_02 = []
			try:
				# 1-4
				m_02.extend(m_01[0:5])
				# 5-7
				m_02.extend(m_01[6:9]),
				# 8-10
				m_02.extend([m_01[23],'',m_01[23]]),
				# 11-15
				m_02.extend([
					# 11 Tipo de Comprobante de Pago o Documento que sustenta el cr??dito fiscal
					move.l10n_pe_non_domic_sustent_document_type_id.code or '',
					# 12 Serie del comprobante de pago o documento que sustenta el cr??dito fiscal. En los casos de la Declaraci??n ??nica de Aduanas (DUA) o de la Declaraci??n Simplificada de Importaci??n (DSI) se consignar?? el c??digo de la dependencia Aduanera.
					move.l10n_pe_non_domic_sustent_serie or '',
					# 13 A??o de emisi??n de la DUA o DSI que sustenta el cr??dito fiscal
					move.l10n_pe_non_domic_sustent_dua_emission_year or '',
					# 14 N??mero del comprobante de pago o documento o n??mero de orden del formulario f??sico o virtual donde conste el pago del impuesto, trat??ndose de la utilizaci??n de servicios prestados por no domiciliados u otros, n??mero de la DUA o de la DSI, que sustente el cr??dito fiscal.
					move.l10n_pe_non_domic_sustent_number or '',
					# 15 Monto de retenci??n del IGV
					str(move.l10n_pe_non_domic_igv_withholding_amount),
				])
				# 16-24
				m_02.extend([
						# 16 REQUIRED: C??digo  de la Moneda (Tabla 4)
						move.currency_id.name,
						# 17 Tipo de cambio (5)
						move.invoice_date_currency_rate,
						# 18 REQUIRED: Pais de la residencia del sujeto no domiciliado
						move.l10n_pe_partner_country_name,
						# 19 REQUIRED: Apellidos y nombres, denominaci??n o raz??n social  del sujeto no domiciliado. En caso de personas naturales se debe consignar los datos en el siguiente orden: apellido paterno, apellido materno y nombre completo.
						move.l10n_pe_partner_name,
						# 20 Domicilio en el extranjero del sujeto no domiciliado
						move.l10n_pe_partner_street,
						# 21 REQUIRED: N??mero de identificaci??n del sujeto no domiciliado
						move.l10n_pe_partner_vat or '',
						# 22 N??mero de identificaci??n fiscal del beneficiario efectivo de los pagos
						'',
						# 23 Apellidos y nombres, denominaci??n o raz??n social  del beneficiario efectivo de los pagos. En caso de personas naturales se debe consignar los datos en el siguiente orden: apellido paterno, apellido materno y nombre completo.
						'',
						# 24 Pais de la residencia del beneficiario efectivo de los pagos
						'',
				])
				# 25-36
				m_02.extend([
					# 25 V??nculo entre el contribuyente y el residente en el extranjero
					move.l10n_pe_non_domic_vinculation_id.code or '',
					# 26 Renta Bruta
					str(move.l10n_pe_non_domic_brute_rent_amount),
					# 27 Deducci??n / Costo de Enajenaci??n de bienes de capital
					str(move.l10n_pe_non_domic_disposal_capital_assets_cost),
					# 28 Renta Neta
					str(move.l10n_pe_non_domic_net_rent_amount),
					# 29 Tasa de retenci??n
					str(move.l10n_pe_non_domic_withholding_rate),
					# 30 Impuesto retenido
					str(move.l10n_pe_non_domic_withheld_tax),
					# 31 REQUIRED: Convenios para evitar la doble imposici??n Tabla 25
					move.l10n_pe_non_domic_agreement_id.code or '',
					# 32 Exoneraci??n aplicada
					move.l10n_pe_non_domic_applied_exemption_id.code or '',
					# 33 REQUIRED: Tipo de Renta
					move.l10n_pe_non_domic_rent_type_id.code or '',
					# 34 Modalidad del servicio prestado por el no domiciliado
					move.l10n_pe_non_domic_service_type_id.code or '',
					# 35 Aplicaci??n del penultimo parrafo del Art. 76?? de la Ley del Impuesto a la Renta
					move.l10n_pe_non_domic_tax_rent_code,
					# 36 REQUIRED: Estado que identifica la oportunidad de la anotaci??n o indicaci??n si ??sta corresponde a un ajuste.
					move.l10n_pe_no_domic_annotation_opportunity_status
				])	
			except:
				raise Warning('Ocurrio un inconveniente: %s' % str(e))
				m_02 = []
			if move.partner_id.country_id != peru:
				lines_to_write_02.append('|'.join(m_02))

			m_03 = []
			if m_01:
				m_03.extend(m_01[0:4])
				m_03.append(m_01[4])
				m_03.extend([
					m_01[5],
					m_01[6],
					m_01[8],
				])
				m_03.extend(m_01[10:13])
				m_03.extend(m_01[13:15])
				m_03.append(m_01[21]) #ICBP
				m_03.extend(m_01[22:26])
				m_03.extend([
					m_01[26],
					m_01[27],
					m_01[28],
					m_01[30],
				])
				m_03.extend(m_01[31:35]+m_01[36:39]+m_01[40:])
			if move.partner_id.country_id == peru:
				lines_to_write_03.append('|'.join(m_03))
		name_01 = self.get_default_filename(ple_id='080100', tiene_datos=bool(lines_to_write_01))
		lines_to_write_01.append('')
		txt_string_01 = '\r\n'.join(lines_to_write_01)
		dict_to_write = dict()
		if txt_string_01 :
			xlsx_file_base_64 = self._generate_xlsx_base64_bytes(lines_to_write_01, name_01[2:], headers=[
				'Periodo',
				'N??mero correlativo del mes o C??digo ??nico de la Operaci??n (CUO)',
				'N??mero correlativo del asiento contable',
				'Fecha de emisi??n del comprobante de pago o documento',
				'Fecha de Vencimiento o Fecha de Pago',
				'Tipo de Comprobante de Pago o Documento',
				'Serie del comprobante de pago o documento o c??digo de la dependencia Aduanera',
				'A??o de emisi??n de la DUA o DSI',
				'N??mero del comprobante de pago o documento o n??mero de orden del formulario f??sico o virtual o n??mero final',
				'N??mero final',
				'Tipo de Documento de Identidad del proveedor',
				'N??mero de RUC del proveedor o n??mero de documento de Identidad',
				'Apellidos y nombres, denominaci??n o raz??n social del proveedor',
				'Base imponible de las adquisiciones gravadas que dan derecho a cr??dito fiscal y/o saldo a favor por exportaci??n, destinadas exclusivamente a operaciones gravadas y/o de exportaci??n',
				'Monto del Impuesto General a las Ventas y/o Impuesto de Promoci??n Municipal',
				'Base imponible de las adquisiciones gravadas que dan derecho a cr??dito fiscal y/o saldo a favor por exportaci??n, destinadas a operaciones gravadas y/o de exportaci??n y a operaciones no gravadas',
				'Monto del Impuesto General a las Ventas y/o Impuesto de Promoci??n Municipal',
				'Base imponible de las adquisiciones gravadas que no dan derecho a cr??dito fiscal y/o saldo a favor por exportaci??n, por no estar destinadas a operaciones gravadas y/o de exportaci??n',
				'Monto del Impuesto General a las Ventas y/o Impuesto de Promoci??n Municipal',
				'Valor de las adquisiciones no gravadas',
				'Monto del Impuesto Selectivo al Consumo en los casos en que el sujeto pueda utilizarlo como deducci??n',
				'Impuesto al Consumo de las Bolsas de Pl??stico',
				'Otros conceptos, tributos y cargos que no formen parte de la base imponible',
				'Importe total de las adquisiciones registradas seg??n comprobante de pago',
				'C??digo de la Moneda',
				'Tipo de cambio',
				'Fecha de emisi??n del comprobante de pago que se modifica',
				'Tipo de comprobante de pago que se modifica',
				'N??mero de serie del comprobante de pago que se modifica',
				'C??digo de la dependencia Aduanera de la Declaraci??n ??nica de Aduanas (DUA) o de la Declaraci??n Simplificada de Importaci??n (DSI)',
				'N??mero del comprobante de pago que se modifica',
				'Fecha de emisi??n de la Constancia de Dep??sito de Detracci??n',
				'N??mero de la Constancia de Dep??sito de Detracci??n',
				'Marca del comprobante de pago sujeto a retenci??n',
				'Clasificaci??n de los bienes y servicios adquiridos',
				'Identificaci??n del Contrato o del proyecto',
				'Error tipo 1: inconsistencia en el tipo de cambio',
				'Error tipo 2: inconsistencia por proveedores no habidos',
				'Error tipo 3: inconsistencia por proveedores que renunciaron a la exoneraci??n del Ap??ndice I del IGV',
				'Error tipo 4: inconsistencia por DNIs que fueron utilizados en las Liquidaciones de Compra y que ya cuentan con RUC',
				'Indicador de Comprobantes de pago cancelados con medios de pago',
				'Estado que identifica la oportunidad de la anotaci??n o indicaci??n si ??sta corresponde a un ajuste',
			])
			dict_to_write.update({
				'ple_txt_01': txt_string_01,
				'ple_txt_01_binary': b64encode(txt_string_01.encode()),
				'ple_txt_01_filename': name_01 + '.txt',
				'ple_xls_01_binary': xlsx_file_base_64.encode(),
				'ple_xls_01_filename': name_01 + '.xls',
			})
		else :
			dict_to_write.update({
				'ple_txt_01': False,
				'ple_txt_01_binary': False,
				'ple_txt_01_filename': False,
				'ple_xls_01_binary': False,
				'ple_xls_01_filename': False,
			})

		name_02 = self.get_default_filename(ple_id='080200', tiene_datos=bool(lines_to_write_02))
		lines_to_write_02.append('')
		txt_string_02 = '\r\n'.join(lines_to_write_02)
		if txt_string_02:
			xlsx_file_base_64 = self._generate_xlsx_base64_bytes(lines_to_write_02, name_02[2:], headers=[
			])
			dict_to_write.update({
				'ple_txt_02': txt_string_02,
				'ple_txt_02_binary': b64encode(txt_string_02.encode()),
				'ple_txt_02_filename': name_02 + '.txt',
				'ple_xls_02_binary': xlsx_file_base_64.encode(),
				'ple_xls_02_filename': name_02 + '.xls',
			})
		else:
			txt_string_02 = " "
			dict_to_write.update({
				'ple_txt_02': txt_string_02,
				'ple_txt_02_binary': b64encode(txt_string_02.encode()),
				'ple_txt_02_filename': name_02 + '.txt',
				'ple_xls_02_binary': False,
				'ple_xls_02_filename': False,
			})

		name_03 = self.get_default_filename(ple_id='080300', tiene_datos=bool(lines_to_write_03))
		lines_to_write_03.append('')
		txt_string_03 = '\r\n'.join(lines_to_write_03)
		if txt_string_03 :
			xlsx_file_base_64 = self._generate_xlsx_base64_bytes(lines_to_write_03, name_03[2:], headers=[
				'Periodo',
				'N??mero correlativo del mes o C??digo ??nico de la Operaci??n (CUO)',
				'N??mero correlativo del asiento contable',
				'Fecha de emisi??n del comprobante de pago o documento',
				'Fecha de Vencimiento o Fecha de Pago',
				'Tipo de Comprobante de Pago o Documento',
				'Serie del comprobante de pago o documento o c??digo de la dependencia Aduanera',
				'N??mero del comprobante de pago o documento o n??mero de orden del formulario f??sico o virtual o n??mero final',
				'N??mero final',
				'Tipo de Documento de Identidad del proveedor',
				'N??mero de RUC del proveedor o n??mero de documento de Identidad',
				'Apellidos y nombres, denominaci??n o raz??n social del proveedor',
				'Base imponible de las adquisiciones gravadas que dan derecho a cr??dito fiscal y/o saldo a favor por exportaci??n, destinadas exclusivamente a operaciones gravadas y/o de exportaci??n',
				'Monto del Impuesto General a las Ventas y/o Impuesto de Promoci??n Municipal',
				'Impuesto al Consumo de las Bolsas de Pl??stico',
				'Otros conceptos, tributos y cargos que no formen parte de la base imponible',
				'Importe total de las adquisiciones registradas seg??n comprobante de pago',
				'C??digo de la Moneda',
				'Tipo de cambio',
				'Fecha de emisi??n del comprobante de pago que se modifica',
				'Tipo de comprobante de pago que se modifica',
				'N??mero de serie del comprobante de pago que se modifica',
				'N??mero del comprobante de pago que se modifica',
				'Fecha de emisi??n de la Constancia de Dep??sito de Detracci??n',
				'N??mero de la Constancia de Dep??sito de Detracci??n',
				'Marca del comprobante de pago sujeto a retenci??n',
				'Clasificaci??n de los bienes y servicios adquiridos',
				'Error tipo 1: inconsistencia en el tipo de cambio',
				'Error tipo 2: inconsistencia por proveedores no habidos',
				'Error tipo 3: inconsistencia por proveedores que renunciaron a la exoneraci??n del Ap??ndice I del IGV',
				'Indicador de Comprobantes de pago cancelados con medios de pago',
				'Estado que identifica la oportunidad de la anotaci??n o indicaci??n si ??sta corresponde a un ajuste',
			])
			dict_to_write.update({
				'ple_txt_03': txt_string_03,
				'ple_txt_03_binary': b64encode(txt_string_03.encode()),
				'ple_txt_03_filename': name_03 + '.txt',
				'ple_xls_03_binary': xlsx_file_base_64.encode(),
				'ple_xls_03_filename': name_03 + '.xls',
			})
		else :
			dict_to_write.update({
				'ple_txt_03': False,
				'ple_txt_03_binary': False,
				'ple_txt_03_filename': False,
				'ple_xls_03_binary': False,
				'ple_xls_03_filename': False,
			})
		dict_to_write.update({
			'date_generated': str(fields.Datetime.now()),
		})
		res = self.write(dict_to_write)
		return res