import re
import requests
import json
import logging
from datetime import datetime
from telegram.ext import ConversationHandler
from telegram import ChatAction, InlineKeyboardMarkup
from bs4 import BeautifulSoup
from buttons import button1, button2, button3, button4, button5
from config import API_URL

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s,'
)
logger = logging.getLogger()


def start(update, context):
    logger.info(
        f'El usuario {update.effective_user["username"]}, ha iniciado una conversacion')
    update.message.reply_text(
        text='Hola {}👋, utiliza el botón de BUSCAR PCR y envíame el número de carné o pasaporte de la persona que deceas buscar.'.format(
            update.effective_user["first_name"]),
        reply_markup=InlineKeyboardMarkup([
            [button3],
            [button1, button2],
            [button5]
        ])
    )

def current_date_format(date):
    date_format = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
    messsage = date_format.strftime('%d-%m-%Y %H:%M')
    return messsage

def BuscarPrueba(text) :
    params = dict(buscar=text)
    res = requests.get(API_URL, params=params)
    msg = ''
    
    if res.status_code == 200:
        data = json.loads(res.text)
        atributo = data['resultado']
        for element in atributo:
            if len(element) == 0:
                msg += 'No se encontro ningun resultado'
                return msg
            else:    
                if element['fecha_resultado'] == None:
                    element['fecha_resultado'] = '---'
                if element['numero'] == None:
                    element['numero'] = '---'
                if element['placa'] == None:
                    element['placa'] = '---'
                if element['procesado'] == 'NO' and element['pcr'] == 'Positivo' or element['procesado'] == 'NO' and element['pcr'] == 'Negativo':
                    confirmacion = '(Pendiente por rectificar)'
                else:
                    confirmacion = ' '
                msg += '👤 Nombre: '+element['nombre']+ ' '+element['apellidos']+"\n"'🗓 Fecha de resultado: '+current_date_format(element['fecha_resultado'])+"\n"'🔬 Resultado: '+element['pcr']+' '+str(confirmacion)+"\n"'#⃣ Numero: '+element['numero']+"\n"'☑ Placa: '+element['placa']+"\n"
                
                return msg
    
    else:
        msg += 'El servidor no esta disponible en estos momentos, consulte mas tarde'
        return msg

def send_result(pcr_result, chat):
    chat.send_action(
        action=ChatAction.TYPING,
        timeout=None
    )
    if pcr_result:
        chat.send_message(
            text=pcr_result,
            reply_markup=InlineKeyboardMarkup([
                [button4]
            ])
            )
    else:
        error = 'No se han encontrado resultados para este carné o pasaporte.'
        chat.send_message(
            text=error,
            reply_markup=InlineKeyboardMarkup([
                [button4]
            ])
            )

def input_text(update, context):
    text = update.message.text
    if not re.match("^[0-9a-zA-Z].{5,10}$", text):
        pcr_result = 'El número de carné o pasaporte es incorrecto'
    else:
        pcr_result =  BuscarPrueba(text)
    chat = update.message.chat
    send_result(pcr_result, chat)
    return ConversationHandler.END


def parte_covid(update, context):
    logger.info(f'El usuario {update.effective_user["username"]}, ha solicitado parte diario')
    url = requests.get('https://www.infomed.hlg.sld.cu/parte-covid-19/')
    soup = BeautifulSoup(url.content, 'html.parser')
    result = soup.find('h2', {'class': 'dmbs-post-title'})
    date_element = soup.find('span', {'class': 'dmbs-post-date'})
    link = result.find('a')
    format_result = link.get('href')
    
    msj_parte_covid = str(date_element.text)+' 👉 '+str(format_result)+'amp'
    
    return msj_parte_covid