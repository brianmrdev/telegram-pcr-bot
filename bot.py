from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from config import TOKEN
from functions import start, input_text
from callback_query_handler import INPUT_TEXT, pcr_callback_query_handler, back_callback_query_handler, parte_callback_query_handler, acercade_callback_query_handler


if __name__ == '__main__' :    
    
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # add handler
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(pattern='back', callback=back_callback_query_handler))
    dp.add_handler(CallbackQueryHandler(pattern='parte', callback=parte_callback_query_handler))
    dp.add_handler(CallbackQueryHandler(pattern='acercade', callback=acercade_callback_query_handler))
    dp.add_handler(ConversationHandler(
        entry_points=[
            CallbackQueryHandler(pattern='pcr', callback=pcr_callback_query_handler)
        ],
        states={
            INPUT_TEXT: [MessageHandler(Filters.text, input_text)]
        },
        fallbacks=[]
    ))
    
    
    
    updater.start_polling()    
    updater.idle()