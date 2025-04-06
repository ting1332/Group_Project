import os
import base64
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

logging.basicConfig(level=logging.DEBUG)

# Initialize Firebase
try:
   # encoded_private_key = os.getenv('FIREBASE_KEY')
     encoded_private_key = 'ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiY2hhdGJvdC0xMzE5MyIsCiAgInByaXZhdGVfa2V5X2lkIjogImQzY2QyZWNmYjg5OThjZDZlYTc4MTNmNWE5MDZhYTJmMTNhNWVlM2YiLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2d0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktrd2dnU2xBZ0VBQW9JQkFRQ2xZenBrdG5YNzM2L2tcbllWbzYyK1BsMVg5MWxqbkdEeGxDeHk4b1ZjOVVqZHRHM2ZRNjRUbFdteStTcXpLUjJTNUJhOXdibTNwc2RaZFNcbkxvMERybk40Uml6MSswSGEzaTFqbGdRSnQvQjRLVFpGZGpvQ29ERGtWaXlUcThZazlsY0QzUlN4aFVxL3o3RzZcblZxMDJyZzRDVENJcGEvWTlzYjNDQXk3YVZrN3UrWWgzdlY2M0QzcVBwRWRCemlpNElaS3dRclVDbFVZVHRoL3pcbm1XU0tRR1ZkUXBzOFBZZ1hPa25EczZBQkFOY3lVYkpGUzlFcXBVbzRhelZSK1hmMjVLTjBPdVRmZjlvazZrS29cbnlHVjlmWkxKdjV5enlWNWJZZDNGcGxJM3NsZFgxRHQxbkpucElBOFQ0cmgzTVFMRUhTU1JJQk9nRVFVMVVhdDRcbmQ0RmtMNEJoQWdNQkFBRUNnZ0VBRFNTTmgyTllqT09CdnN4ZHR6K3lKSm1LdjNWb3NleVJQVlZHMGhXL25DQ0pcbnhGL3ZBSjdWUjZTZGF6SmZtbWQvM1lNTXdzVGdQYTQ2a0RWU3ozQVZqUUZHb1dXT0hpNTV2T2cyK2U2OEZWQnhcbkY2UUZpQi9pd3NKMldHWFdJU25TVUdSSk9MSTI5bmN5MEhRQzM4MkZIM21kWFYxTy9DZ2J4RWNzZWYxUjJIdXJcbkVrOTJLcmZ4clpEVGw1LzFkY0JqNXV6a3k5em5wVHhuUTF3ZXlmdUJTUmxZUThBN1BXVVZtSnRmeGpjMStnRkRcbmxldzdza1Fjd1VzZGEzNUFhMUU5OUc0L2VnSk5vc0VRS0JKTStzZDhhYisrTi8rY2s1ckF5NnNhNXcxa1VEcTZcbjNvOTFDZXpobEFyR0tkeFVUM290Qnd2WVc1c05lRXdoSGdQWXNFYlc0UUtCZ1FEa2phVmVmamJNeElIYXhoUUdcbjRIczdmd1plTThtYkttc0d2MmJ6a0JGZklCbkNabDhkYUVWdEVQZlluSjdVMHdjWWo5cHRQakpMb2RrMnhrY2tcbithaXg1L3V4K2RqNVBzYzJEU1JSQkUyZ25QaGU5VjRyNW4wU3NKaHVXT1BhblQzMUtSd1NrMzVtdXduT1V3SWlcbnhJVUNiSnAzMk9PMW5ONzhvNkpYRmdIZWt3S0JnUUM1UDdJZ3dRQXVITTQybGtyOC9ZR3dHVFY0bHQ4b1FBQXBcblZxTE5lM0tBVDRNNXR5dnZVb2RrMzRQcmZmNVFMSm5DcFZRMS9QbUg5UFJlSy9WZ1NFTDFtRHNUQ0N0ckVqNXVcbjNNeFY1UnZ1TG9wS1Z4cGJscjdUYXZ0NllDc2dieUc1RDlRY3NydzV6UWhqYk05b1JCZTNIdmxBTGduZHlMenZcbm5GcnVWSDVKdXdLQmdRRE1rdkRUZkx2R1c1b3ozWnF0Y1I4ODZQMGxNc3VoSkwyNXczYitTaFVTaFdRcE9vS21cbml0K2h1VTl2UnZsd1hCZDg1NzVHakNadXhrYnNIVnd1LzN6OUNUMmtWNVBidlZLSTBnaVFyLzVmNWtEMmxrQWRcbm9XaVFZeHQ5b2ZrSmhEZWlDcE1ER1p4SmpkOUFHOUxNbGdUTVg3Ti8xTlkxaUYyYjIwZ0RGVUxGR3dLQmdRQ3VcblFrVzgyL0RnYjhabndROC9WdlUxQXpHeWd6SGV1ZjJzNVV0MlFnYmV2bTB4MEtYcWxkYTVSQ3pqVEh6N1RFbERcbnVhUXl1UXErSXVYdzVDY0pjRkJVbU9RUkxpRXhzbEs2bE1jK2thdXBiV3czTENLbVAzSzRqQzJOMjRNV0dwUTlcbmNxOVVZNm4rTVdvUHBSNmg5VlBkdGF3Ly9FN1pxMmhYZWR4cnoxMlEyd0tCZ1FDUHlNU2VCRUM5ZERGcVk1YlhcbkpZMmdJM1RQUEJxZWJSdjRKdFk5L0JSaEpVbzAvZXVKVWVaTnNzbjlDdElZQ3V2YTdINTVYbDJBYk1BQ25ZeHNcbmJUcy9VSmh4YUNUVTAzSXF5b1B3eG9BTWxLSk9iVXVGSmc4MG9HL0dmZzh4dE4vVFJqUlJ5eHpYRStFdGJhSk9cbmJxRFVYYy9GakNtQThOZkFkcklkOFc4eVl3PT1cbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsCiAgImNsaWVudF9lbWFpbCI6ICJmaXJlYmFzZS1hZG1pbnNkay1mYnN2Y0BjaGF0Ym90LTEzMTkzLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjEwMDk3Njg4NDgyMTQ1MjA5NTM2OCIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvZmlyZWJhc2UtYWRtaW5zZGstZmJzdmMlNDBjaGF0Ym90LTEzMTkzLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAidW5pdmVyc2VfZG9tYWluIjogImdvb2dsZWFwaXMuY29tIgp9'

    
logging.debug("siyao:%s", encoded_private_key)

# 解码 Base64 字符串
    decoded_private_key = base64.b64decode(encoded_private_key).decode('utf-8')

# 将解码后的私钥转换为字典
    config = json.loads(decoded_private_key)
    # 初始化 Firebase Admin SDK
    cred = credentials.Certificate(config)
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
