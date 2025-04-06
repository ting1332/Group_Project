import os
import logging
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import configparser
import firebase_admin
from firebase_admin import credentials, firestore
from ChatGPT_HKBU import HKBU_ChatGPT

REGISTER, INTERESTS = range(2)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize Firebase
try:
    # 从环境变量中获取服务账户密钥
    google_credentials = os.getenv('GOOGLE_CREDENTIALS')
    
    if not google_credentials:
        raise ValueError("Google credentials environment variable is not set.")
    
    # 将 JSON 字符串解析为字典
    cred_info = json.loads(google_credentials)
    
    # 使用从环境变量中获取的凭据初始化 Firebase
    cred = credentials.Certificate(cred_info)
    
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    logging.info("Firebase initialized successfully.")
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
