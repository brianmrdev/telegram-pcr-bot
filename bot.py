# -*- coding: utf-8 -*-
import logging
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import ChatAction, InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
import requests
import json
import re

from config import TOKEN, URL

#Configurar Logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s,'
)
logger = logging.getLogger()

INPUT_TEXT = 0

def start(update, context):
    logger.info(f'El usuario {update.effective_user["username"]}, ha iniciado una conversacion')
    button1 = InlineKeyboardButton(text='📰 Parte Oficial', callback_data='parte')
    button2 = InlineKeyboardButton(text='📥 Descargar APK', url='https://www.apklis.cu/application/cu.nat.apivanis.pcrholguin')
    button3 = InlineKeyboardButton(text='🔍 Buscar PCR', callback_data='pcr')
    update.message.reply_text(
        text='Soy un asistente para conocer el resultados de las pruebas PCR en Holguín.\n\n¿Qué deceas hacer?',
        reply_markup=InlineKeyboardMarkup([
            [button3],
            [button1, button2]
        ])
    )

def acercadelautor(update, context):
    logger.info(f'El usuario {update.effective_user["username"]}, ha solicitado informacion del autor')
    update.message.reply_text(text='https://www.linkedin.com/in/brianmrdev/')

def parte_covid(update, context):
    logger.info(f'El usuario {update.effective_user["username"]}, ha solicitado parte diario')
    url = requests.get('https://www.infomed.hlg.sld.cu/parte-covid-19/')
    soup = BeautifulSoup(url.content, 'html.parser')
    result = soup.find('h2', {'class': 'dmbs-post-title'})
    date_element = soup.find('span', {'class': 'dmbs-post-date'})
    link = result.find('a')
    format_result = link.get('href')

    context.bot.send_message(chat_id=update.effective_chat.id, text=str(date_element.text)+' 👉 '+str(format_result)+'amp') 

def parte_callback_query_handler(update, context):
   input = update.callback_query.data
   if input == 'parte':
       parte_covid(update, context)

def pcr_command_handler(update, context):
    logger.info(f'El usuario {update.effective_user["username"]}, ha solicitado resultado de pcr')
    update.message.reply_text('Para saber el resultado envíame un mensaje con tu número de carné o pasaporte.')
    return INPUT_TEXT

def pcr_callback_query_handler(update, context):
    logger.info(f'El usuario {update.effective_user["username"]}, ha solicitado resultado de pcr')
    input = update.callback_query.data
    if input == 'pcr':
       context.bot.send_message(chat_id=update.effective_chat.id, text='Para saber el resultado envíame un mensaje con tu número de carné o pasaporte.')
       return INPUT_TEXT

def BuscarPrueba(text) :
    params = dict(buscar=text)
    res = requests.get(URL, params=params)
    msg = ''
    
    if res:    
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
                msg += '👤 Nombre: '+element['nombre']+ ' '+element['apellidos']+"\n"'🗓 Fecha de resultado: '+element['fecha_resultado']+"\n"'🔬 Resultado: '+element['pcr']+' '+str(confirmacion)+"\n"'#⃣ Numero: '+element['numero']+"\n"'☑ Placa: '+element['placa']+"\n"
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
        chat.send_message(text=pcr_result)
    else:
        error = 'No se han encontrado resultados para este carné o pasaporte.'
        chat.send_message(text=error)

def input_text(update, context):
    text = update.message.text
    if not re.match("^[0-9a-zA-Z].{5,10}$", text):
        pcr_result = 'El número de carné o pasaporte es incorrecto'
    else:
        pcr_result =  BuscarPrueba(text)
    chat = update.message.chat
    send_result(pcr_result, chat)
    return ConversationHandler.END

if __name__ == '__main__':
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    
    #add handler
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('acercadelautor', acercadelautor))
    dp.add_handler(CommandHandler('parte', parte_covid))
    dp.add_handler(CallbackQueryHandler(pattern='parte', callback=parte_callback_query_handler))
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('pcr', pcr_command_handler),
            CallbackQueryHandler(pattern='pcr', callback=pcr_callback_query_handler)
        ],
        states={
            INPUT_TEXT: [MessageHandler(Filters.text, input_text)]
        },
        fallbacks=[]
    ))
    

    updater.start_polling()
    updater.idle()
