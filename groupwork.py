import os
import logging
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import configparser
import firebase_admin
from firebase_admin import credentials, firestore
from ChatGPT_HKBU import HKBU_ChatGPT
import json

REGISTER, INTERESTS = range(2)

# Set up logging
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 创建一个 StreamHandler 并设置日志级别
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# 创建一个格式化器并将其添加到处理器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# 将处理器添加到日志记录器
logger.addHandler(ch)
# Initialize Firebase
try:
     firebase_key={
  "type": "service_account",
  "project_id": "chatbot-13193",
  "private_key_id": "338ab1ce64cf193064cdc0a5f04c2798fcb66d95",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDEVtAOgf08/huC\nT3gfdXwjq5Nkbr5yzuy2uBF/vkI/SIi6V+9RQElKMgRXXIYWEl2n6XVey5mNBpmq\nrV7aSD/goknnqVFJA8+Nr7KIwz0zYgipbai8XiNHg99eAT44uBoXcR6XQmBb8beh\nTNwKOoqrl0QiLlQLa5dzAx+Api7pLzmwJronG3/PU+X5DefxlY6n59C0fCdRAKYf\nl5/ET9lPn3CzZOUXQo+ZvSOIwoEZPuWJ5VUdnIvQIjNTsnJamsSF0qmFXXt2IaJR\n/Yw0BGubS4H5yTSerJ6hmQRfxmydl2hQnznvRqC8FNfumVsdH+Pd2yZic3geXGtj\nqAKbHFJ/AgMBAAECggEABYqUXq8ehZfVEO117Mq1ETtTcp80MtX86lScRyhd2Elk\nyoBBhIqK8al4Y+V8R1KHYCjU+N2dh38V29z+yKxcroCwvfVnvObQTHsWpTOAHlt4\nS8feM6AjNhkrtwx+mWfgx06YWBk10lfVIJv5uImEcRQDhpobdyMMkuDAr9yA2xs/\nHgNEHoJVeJoPG11f7O2W0E5Cxz6ZdiH7yBDzSI8GByreBg27APJFwidearyXBEOg\nf5kDp54wNLiQgQ8EQp2u47PgxS22vaISmAv6fy5y5OJ4YTxe22O+34K/b3jrwzSj\nNfA1X4qAH6O5aGU8B2JpaUpiDSt868ZZ1I59ZvXe2QKBgQDlWL30/rwmFtxzNJFg\nVu9nYFGUKpLrqYLPgW+txTN3k5c0XC79gP3TD2zxg4jD1e2SD/1WWjq13wot55ON\nAD2PG6jDXD43cqrBDi03iNcbCx3bifU+aHp/+0ww6WFWeQuo53J1yyKAKqa4YfsO\nb+ielvtRm039F/76FjazoLsl1QKBgQDbKBGC/GPIOLFu+NQZTQacMuiHWE92JMb5\nKmVNRbNAoTJIq2TQv8BTS3Xmh6WLIpC/ZlIF9wdAhl7aPx0ZQkotbRoxrMTadMAQ\nWgR6zLlqHyUIVCK/HT70cn9Zxob2eh20oMFGpN+p+7LnM9vsK4RjuHxdNpQk/nA6\nUrQpuzrdAwKBgQDgjWXXxb4kMQgBSHv6bsQSXG0jfBfD44FveFUHN+ivcHOAUa20\niaJ8D0NkqJu02vWzqDIsZUXMoqfN0EpYqN6dCsDPHrbQBVaIlT/SewnZsaW3OTlE\ntHkUa9DqpuamCvhOlOYtzQlnodsA9vYf6ZRCCqPhAAV5BBCjfjJq57m1TQKBgQCG\nAS0cA8nbntbXvSyrv85/6h0GzTfhTMGhj4vbwPfHWAmQJ8UAY49tHyIbcOwHdH4/\nmogi/5aenMsY9iiLzl3fAuxWXYcM8QCTvwcoM1BYlGyneBK6+14ISI6YTW0u/yJ0\n1Sr5UE02+iG9f5dFBKLx+teIg5v4NuBWuUVSkxp+EwKBgQDJAYdjok+aNEd2XUIs\n5ouHB2AXKg3XujPUBavRGd8aMrV6bedIB8j+T9rpz48Bo6MskWBUdhfSoWfHphs0\nV2JHQxLgA53pFRXP/Hw0A7Fge8XHkjpBodQTw4oGrNvvswkYiQ+FCt/F1RMoXIJn\n18GKo8/FsPvxHqGyevkvnnuImw==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@chatbot-13193.iam.gserviceaccount.com",
  "client_id": "100976884821452095368",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40chatbot-13193.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

    # 使用从环境变量中获取的凭据初始化 Firebase
    try:
        cred = credentials.Certificate(firebase_key)
    except Exception as e:
        logging.error("Failed to create credentials from provided info: %s", e)
        raise

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    logging.info("Firebase initialized successfully.")

except ValueError as ve:
    logging.error(f"ValueError: {ve}")
except Exception as e:
    logging.error(f"Failed to initialize Firebase: {e}")

def start(update: Update, context: CallbackContext):
    """Start command, welcome the user and guide registration interest"""
    update.message.reply_text(
        "Welcome to the interest matching chatbot!\n"
        "You can register your interests with the /register command, including:\n"
        "- Online games\n"
        "- VR experiences\n"
        "- Social media groups\n"
        "- Music\n"
        "- Dancing\n"
        "Then I'll help you find people with similar interests!"
    )

def register(update: Update, context: CallbackContext):
    """Register Interests"""
    update.message.reply_text(
        "Please tell me your areas of interest (separate with commas):\n"
        "Example: online gaming, social media, VR, sports, music, etc."
    )
    return INTERESTS

def save_interests(update: Update, context: CallbackContext):
    """Saving user interests to Firestore"""
    user_id = update.effective_user.id
    interests = update.message.text.split(",")
    interests = [interest.strip() for interest in interests]
    
    logging.info(f"User ID: {user_id}, Interests: {interests}")  # 记录用户ID和兴趣

    # Storing user interests in Firestore
    try:
        user_ref = db.collection('users').document(str(user_id))
        user_ref.set({'interests': interests})
        update.message.reply_text("Your interest has been registered successfully! You can find people with same interests as you by using /find_matches command")
    except Exception as e:
        logging.error(f"Failed to save interests to Firestore: {e}")
        update.message.reply_text("There was an error saving your interests. Please try again later.")
    
    return ConversationHandler.END


def find_matches(update: Update, context: CallbackContext):
    """Find matching users from Firestore"""
    user_id = update.effective_user.id
    user_ref = db.collection('users').document(str(user_id))
    user_doc = user_ref.get()
    if not user_doc.exists:
        update.message.reply_text("You haven't registered your interest yet, please register first using the /register command!")
        return

    user_interests = user_doc.to_dict()['interests']
    user_interests = [interest.lower() for interest in user_interests]  
    user_username = user_doc.to_dict().get('username', '未知用户')  

    matches = []
    users_ref = db.collection('users')
    for doc in users_ref.stream():
        other_user_id = doc.id
        if other_user_id != str(user_id):
            other_interests = doc.to_dict().get('interests', [])
            other_interests = [interest.lower() for interest in other_interests]  
            other_username = doc.to_dict().get('username', '未知用户')  

            common_interests = set(user_interests) & set(other_interests)
            if common_interests:
                matches.append((other_user_id, other_username, common_interests))

    if matches:
        response = "Here are users who share the same interests with you:\n"
        for match in matches:
            response += f"User_Name: {match[1]}, User_ID: {match[0]}, Same_Interests: {', '.join(match[2])}\n"
    else:
        response = "Sorry, we currently cannot find users who share your interests."
    update.message.reply_text(response)

def equiped_chatgpt(update, context):
    global chatgpt
    user_message = update.message.text
    if "match users with similar interests" in user_message:
        reply_message = "OK, Please input /start command to start matching。"
    else:
        reply_message = chatgpt.submit(user_message)
    logging.info("Update: "+str(update))
    logging.info("context: "+str(update))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def main():
    global chatgpt
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    
    # Initialize ChatGPT
    chatgpt = HKBU_ChatGPT(config)

    # Registering a Command Processor
    start_handler = CommandHandler('start', start)
    register_handler = ConversationHandler(
        entry_points=[CommandHandler('register', register)],
        states={
            INTERESTS: [MessageHandler(Filters.text & (~Filters.command), save_interests)]
        },
        fallbacks=[]
    )
    find_matches_handler = CommandHandler('find_matches', find_matches)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(register_handler)
    dispatcher.add_handler(find_matches_handler)

    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
    
    # To start the bot:
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
