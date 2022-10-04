import logging
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardMarkup
from buttons import button1, button2, button3, button4, button5
from functions import parte_covid
from config import MESSAGE_ABOUT


INPUT_TEXT = 0

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s,'
)
logger = logging.getLogger()


def back_callback_query_handler(update, context):
    query = update.callback_query
    query.answer()

    query.edit_message_text(
        text='Hola {}👋, utiliza el botón de BUSCAR PCR y envíame el número de carné o pasaporte de la persona que deceas buscar.'.format(update.effective_user["first_name"]),
        reply_markup=InlineKeyboardMarkup([
            [button3],
            [button1, button2],
            [button5]
        ])
    )


def pcr_callback_query_handler(update, context):
    logger.info(
        f'El usuario {update.effective_user["username"]}, ha solicitado resultado de pcr')
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Para saber el resultado envíame un mensaje con su número de carné o pasaporte.'
    )
    return INPUT_TEXT


def parte_callback_query_handler(update, context):
    query = update.callback_query
    query.answer()
    msj = parte_covid(update, context)
    
    query.edit_message_text(
        text=str(msj),
        reply_markup=InlineKeyboardMarkup([
            [button4],
        ])
    )

def acercade_callback_query_handler(update, context):
    query = update.callback_query
    query.answer()
    msj = MESSAGE_ABOUT
    
    query.edit_message_text(
        text=str(msj),
        reply_markup=InlineKeyboardMarkup([
            [button4],
        ])
    )