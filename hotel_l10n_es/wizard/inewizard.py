# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64  
import datetime
import calendar
import xml.etree.cElementTree as ET

import logging
_logger=logging.getLogger(__name__)

def get_years():
    year_list = []
    for i in range(2016, get_year()+1):
        year_list.append((i, str(i)))
    return year_list

def get_year():
    now = datetime.datetime.now()
    return int(now.year)

def get_month():
    now = datetime.datetime.now()
    month = int(now.month)-1
    if month <= 0:
        month = 12
    return month

class Wizard(models.TransientModel):
    _name = 'ine.wizard'

    txt_filename = fields.Char()
    txt_binary = fields.Binary()
    ine_month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                          (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), 
                          (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'), ], 
                          string='Month', default=get_month())
    ine_year = fields.Selection(get_years(), default=get_year(), string='Year')

    @api.one
    def generate_file(self):
        month_first_date=datetime.datetime(self.ine_year,self.ine_month,1)
        last_day=calendar.monthrange(self.ine_year,self.ine_month)[1] - 1
        #month_end_date=month_first_date + datetime.timedelta(days=calendar.monthrange(self.ine_year,self.ine_month)[1] - 1)
        month_end_date=month_first_date + datetime.timedelta(days=last_day)
        m_f_d_search = datetime.date(self.ine_year,self.ine_month,1)
        #m_e_d_search = m_f_d_search + datetime.timedelta(days=calendar.monthrange(self.ine_year,self.ine_month)[1] - 1)
        m_e_d_search = m_f_d_search + datetime.timedelta(days=last_day)
        last_day +=1
        
        # Seleccionamos los que tienen Entrada en el mes + salida en el mes + entrada antes y salida despues. Ordenandolos.
        lines = self.env['cardex'].search(['|','|','&',('exit_date','>=',m_f_d_search),('exit_date','<=',m_e_d_search),'&',('enter_date','>=',m_f_d_search),('enter_date','<=',m_e_d_search),'&',('enter_date','<=',m_f_d_search),('exit_date','>=',m_e_d_search)] , order="enter_date" )
        lines = lines.sorted(key=lambda r: str(r.partner_id.code_ine)+r.enter_date)

        compan = self.env.user.company_id

        encuesta = ET.Element("ENCUESTA")
        cabezera = ET.SubElement(encuesta, "CABEZERA")

        fecha = ET.SubElement(cabezera,"FECHA_REFERENCIA")
        ET.SubElement(fecha, "MES").text = '{:02d}'.format(self.ine_month)
        ET.SubElement(fecha, "ANYO").text = str(self.ine_year)

        month_end_date=datetime.datetime(self.ine_year,self.ine_month,1) + datetime.timedelta(days=calendar.monthrange(self.ine_year,self.ine_month)[1] - 1)
        ET.SubElement(cabezera,"DIAS_ABIERTO_MES_REFERENCIA").text = str(month_end_date.day)

        ET.SubElement(cabezera,"RAZON_SOCIAL").text = compan.name
        ET.SubElement(cabezera,"NOMBRE_ESTABLECIMIENTO").text = compan.property_name
        ET.SubElement(cabezera,"CIF_NIF").text = compan.vat
        ET.SubElement(cabezera,"NUMERO_REGISTRO").text = compan.tourism
        ET.SubElement(cabezera,"DIRECCION").text = compan.street
        ET.SubElement(cabezera,"CODIGO_POSTAL").text = compan.zip
        ET.SubElement(cabezera,"LOCALIDAD").text = compan.city
        ET.SubElement(cabezera,"MUNICIPIO").text = compan.city
        ET.SubElement(cabezera,"PROVINCIA").text = compan.state_id.display_name
        ET.SubElement(cabezera,"TELEFONO_1").text = compan.phone
        ET.SubElement(cabezera,"TIPO").text = compan.category_id.name
        ET.SubElement(cabezera,"CATEGORIA").text = compan.vat
        ET.SubElement(cabezera,"HABITACIONES").text = str(compan.rooms)
        ET.SubElement(cabezera,"PLAZAS_DISPONIBLES_SIN_SUPLETORIAS").text = str(compan.seats)
        ET.SubElement(cabezera,"URL").text = compan.website

        alojamiento = ET.SubElement(encuesta, "ALOJAMIENTO")
        #Bucle de RESIDENCIA


        ine_entrada = []
        ine_salidas = []
        ine_pernoct = []
        for x in xrange(last_day+1):
            ine_entrada.append(0)
            ine_salidas.append(0)
            ine_pernoct.append(0)

        for linea in lines:
            f_entrada = linea.enter_date.split('-')
            f_salida = linea.exit_date.split('-')
            # Ha entrado este mes
            if int(f_entrada[1]) == self.ine_month:
                ine_entrada[int(f_entrada[2])] += 1
                cuenta_entrada = int(f_entrada[2])
            else:
                # No marco entrada y cuento desde el dia 1
                cuenta_entrada = 1
            if int(f_salida[1]) == self.ine_month:
                ine_salidas[int(f_salida[2])] += 1
                cuenta_salida = int(f_salida[2])
            else:
                # No marco entrada y cuento desde el dia 1
                cuenta_salida = last_day
            #Contando pernoctaciones
            for i in range(cuenta_salida-cuenta_entrada):
                ine_pernoct[cuenta_entrada+i] += 1




            #if linea.enter_date == datetime.date(self.ine_year,self.ine_month,i):
            #    ET.SubElement(alojamiento,"Entrada_"+str(i)).text = str(linea.enter_date)
            alojamiento = ET.SubElement(encuesta, "RESIDENCIA")
            ET.SubElement(alojamiento,"Entrada").text = str(linea.enter_date)
            # ET.SubElement(alojamiento,"entrada_separada_ano").text = str(f_entrada[0])
            # ET.SubElement(alojamiento,"entrada_separada_mes").text = str(f_entrada[1])
            # ET.SubElement(alojamiento,"entrada_separada_dia").text = str(f_entrada[2])
            ET.SubElement(alojamiento,"Salida").text = str(linea.exit_date)
            ET.SubElement(alojamiento,"Estado").text = str(linea.reservation_id.state)
            ET.SubElement(alojamiento,"Doctipe").text = str(linea.partner_id.documenttype)
            ET.SubElement(alojamiento,"INEName").text = str(linea.partner_id.code_ine.name)
            ET.SubElement(alojamiento,"INEName").text = str(linea.partner_id.code_ine.code)
            ET.SubElement(alojamiento,"Codigohabita").text = str(linea.reservation_id.room_type_id.code_type)
            ET.SubElement(alojamiento,"Codigohabita").text = str(linea.partner_id.name)

        habitaciones = ET.SubElement(encuesta, "HABITACIONES")
        #Bucle de HABITACIONES_MOVIMIENTO

        personal = ET.SubElement(encuesta, "PERSONAL_OCUPADO")
        ET.SubElement(personal,"PERSONAL_NO_REMUNERADO").text = '0'
        ET.SubElement(personal,"PERSONAL_REMUNERADO_FIJO").text = str(compan.permanentstaff)
        ET.SubElement(personal,"PERSONAL_REMUNERADO_EVENTUAL").text = str(compan.eventualstaff)


        seguimiento = ET.SubElement(encuesta, "seguimiento_variables")
        ET.SubElement(seguimiento,"month_end_date").text = str(month_end_date)
        ET.SubElement(seguimiento,"month_first_date").text = str(month_first_date)
        for x,y in enumerate(ine_entrada):
            ET.SubElement(seguimiento,"ENTRADAS_"+str(x)).text = str(y)
        for x,y in enumerate(ine_salidas):
            ET.SubElement(seguimiento,"Salidas_"+str(x)).text = str(y)
        for x,y in enumerate(ine_pernoct):
            ET.SubElement(seguimiento,"Pernoctaciones_"+str(x)).text = str(y)
        ET.SubElement(alojamiento,"Primerdiadelmesbuscado").text = str(m_f_d_search)
        ET.SubElement(alojamiento,"Ultidiadelmesbuscado").text = str(m_e_d_search)
        ET.SubElement(seguimiento,"last_day").text = str(last_day)




        tree = ET.ElementTree(encuesta)

        xmlstr = '<?xml version="1.0" encoding="ISO-8859-1"?>'
        xmlstr += ET.tostring(encuesta)            
        file=base64.encodestring( xmlstr )
        return self.write({
             'txt_filename': 'INE_'+str(self.ine_month)+'_'+str(self.ine_year) +'.'+ 'xml',
             'txt_binary': base64.encodestring(xmlstr)
             })