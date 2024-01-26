import requests
import telebot
from telebot import types
import json
from server import keep_alive
from geopy.geocoders import Nominatim
from func import *

token = '6884256971:AAHUZtcNtdkGqVSzLqAT2oMd2yPQwlUAjM0'
bot = telebot.TeleBot(token, parse_mode=None)
WAITING_FOR_TRACKING_NUMBER = 'waiting_for_tracking_number'
WAITING_FOR_ORDER_NAME = 'waiting_for_order_name'

bot.delete_my_commands(scope=None, language_code=None)

commands = [
    telebot.types.BotCommand(command="start", description="ابدا الان"),
    telebot.types.BotCommand(command="my_order",
                             description="قائمة الطرود خاصة بك"),
    telebot.types.BotCommand(command="remove_order", description="حذف طرد "),
    telebot.types.BotCommand(command="add_order", description="اضافة طرد"),
    telebot.types.BotCommand(command="lang", description="تغير اللغة")
]

bot.set_my_commands(commands=commands)


@bot.message_handler(commands=['wiw2'])
def phit2o(message):
  for user in user_urls['users']:
    if has_chat_id(user_urls,user['id']):
     bot.send_message(user['chat_id'],'bot is working')
    
  bot.send_message(message.chat.id,'wiw')
@bot.message_handler(commands=['wiw'])
def phit2o(message):

  user_count = len(user_urls["users"])
  bot.send_message(message.chat.id, f'nember of user:{user_count}')
  """ for user in user_urls["users"]:
    user_id = user["id"]
    if "orders" in user:
      for order in user["orders"]:
        order_number = order["number"]
        order_name = order["name"]
        bot.send_message(
            message.chat.id,
            f"User ID: {user_id}, Order Number: {order_number}, Order Name: {order_name}"
        )
    else:
      # Handle the case where there are no orders for the user
      bot.send_message(message.chat.id, f"User ID: {user_id} has no orders.")"""


@bot.message_handler(commands=['start'])
def phito(message):
  user_id = str(message.chat.id)
  Lang = "ar"
  if check_user_id('users_data.json', user_id):
    for user in user_urls['users']:
        user['language'] = Lang
        if not has_chat_id(user_urls,user['id']):
         chat_id= message.chat.id
         add_chat_id(user_urls,user['id'],chat_id)
  else:
    new_user = {"id": user_id, "language": Lang,"chat_id":message.chat.id}
    user_urls["users"].append(new_user)
  bot.delete_message(message.chat.id, message.message_id)

  markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
  button1 = types.KeyboardButton("/my_order")
  button2 = types.KeyboardButton("/lang")
  button3 = types.KeyboardButton("/remove_order")
  button4 = types.KeyboardButton("/add_order")

  markup.add(button1, button2)
  markup.add(button3, button4)
  bot.send_message(message.chat.id,
                   "مرحبا بك في بوت تتبع طرود من علي اكسبراس",
                   reply_markup=markup)
  with open('users_data.json', 'w') as file:
   json.dump(user_urls, file)

@bot.message_handler(commands=['my_order'])
def menu_handler(message):
  keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
  user_id = str(message.from_user.id)
  for user in user_urls['users']:

    if user['id'] == user_id and 'orders' in user:
      for button in user['orders']:
        tracking_numb = button["number"]

        url = generate_tracking_url(button['number'], user['language'])
        days = get_data(url, tracking_numb)[1]
        button2 = types.InlineKeyboardButton(
            text="مجموعة لشراء من علي اكسبراس",
            url='https://t.me/+iFuk9ep7UdpjZTI0')
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=button['name'] + ' ' +
                                               days,
                                               callback_data=button['name']))
      keyboard.add(button2)

      bot.send_message(message.chat.id, 'your order', reply_markup=keyboard)


@bot.message_handler(commands=['lang'])
def menu_handler(message):

  markuplang = types.InlineKeyboardMarkup()
  button7 = types.InlineKeyboardButton(text='العربية', callback_data='العربية')
  button8 = types.InlineKeyboardButton(text='anglish', callback_data='anglish')
  button9 = types.InlineKeyboardButton(text='francais',
                                       callback_data='francais')
  markuplang.add(button7)
  markuplang.add(button8, button9)
  bot.send_message(message.chat.id,
                   "مرحبا بك اختر اللغة التي تريد",
                   reply_markup=markuplang)


WAITING_FOR_TRACKING_NUMBER = 'waiting_for_tracking_number'
WAITING_FOR_ORDER_NAME = 'waiting_for_order_name'
with open('users_data.json', 'r') as file:
  user_urls = json.load(file)


@bot.message_handler(commands=['remove_order'])
def remove_order(message):
  bot.send_message(message.chat.id, 'Enter the tracking number to remove:')
  bot.register_next_step_handler(message, remove_order_confirm)


def remove_order_confirm(message):
  tracking_number_to_remove = message.text
  user_id = str(message.from_user.id)

  # Find the user with the given ID in your existing data
  for user in user_urls['users']:
    if user['id'] == user_id and 'orders' in user:
      # Check if the tracking number exists in the user's orders
      for order in user['orders']:
        if order['number'] == tracking_number_to_remove:
          # Remove the order
          user['orders'].remove(order)
          bot.send_message(
              message.chat.id,
              f'Tracking number {tracking_number_to_remove} has been removed.')
          break
      else:
        bot.send_message(
            message.chat.id,
            f'Tracking number {tracking_number_to_remove} not found for removal.'
        )
      break
  else:
    bot.send_message(message.chat.id,
                     'User not found or does not have any orders.')

  with open('users_data.json', 'w') as file:
    json.dump(user_urls, file)


@bot.message_handler(commands=['add_order'])
def add_order(message):
  bot.send_message(message.chat.id, 'أرسل رقم التتبع ')
  bot.register_next_step_handler(message, add_order_number)


def add_order_number(message):
  tracking_number = message.text
  if not track_shipment(tracking_number):
    bot.send_message(message.chat.id, 'أرسل اسم لهذا التتبع')
    bot.register_next_step_handler(message, add_order_name, tracking_number)
  else:
    bot.send_message(message.chat.id, 'رقم تتبع غير صالح')


def add_order_name(message, tracking_number):
  user_id = str(message.from_user.id)
  order_name = message.text

  # Find the user with the given ID in your existing data
  for user in user_urls['users']:
    if user['id'] == user_id:
      if 'orders' not in user:
        user['orders'] = []
      user['orders'].append({'number': tracking_number, 'name': order_name})
      bot.send_message(message.chat.id, "تم اضافة الطرد بنجاح")
      break

  with open('users_data.json', 'w') as file:
    json.dump(user_urls, file)


'''@bot.message_handler(
    func=lambda message: message.text is not None and message.text != "",
    state=WAITING_FOR_TRACKING_NUMBER)
def add_order_number(message):
  tracking_number = message.text
  if not track_shipment(tracking_number):
    bot.send_message(message.chat.id, 'أرسل اسم لهذا التتبع')
    bot.register_next_step_handler(message, add_order_name, tracking_number)
  else:
    bot.send_message(message.chat.id, 'رقم تتبع غير صالح')


@bot.message_handler(
    func=lambda message: message.text is not None and message.text != "",
    state=WAITING_FOR_ORDER_NAME)
def add_order_name(message, tracking_number):
  user_id = str(message.from_user.id)
  order_name = message.text

  # Find the user with the given ID in your existing data
  for user in user_urls['users']:
    if user['id'] == user_id:
      if 'orders' not in user:
        user['orders'] = []
      user['orders'].append({'number': tracking_number, 'name': order_name})
      bot.send_message(message.chat.id, "تم اضافة الطرد بنجاح")
      break
  WAITING_FOR_TRACKING_NUMBER = 'waiting_for_tracking_number'
  WAITING_FOR_ORDER_NAME = 'waiting_for_order_name'

  with open('users_data.json', 'w') as file:
    json.dump(user_urls, file)
  bot.clear_step_handler_by_chat_id(chat_id=message.chat.id,
                                    state=WAITING_FOR_TRACKING_NUMBER)
  bot.clear_step_handler_by_chat_id(chat_id=message.chat.id,
                                    state=WAITING_FOR_ORDER_NAME)'''


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
  user_id = str(call.message.chat.id)
  for user in user_urls['users']:
    if user['id'] == user_id:
      for button in user['orders']:
        chose_botton = button['name']
        if call.data == chose_botton:
          tracking_numb = button["number"]

          url = generate_tracking_url(button['number'], user['language'])
          data_short = short_data(url, tracking_numb)
          text = data_short[1]
          time = data_short[0]
          tra = data_short[2]
          markuplang2 = types.InlineKeyboardMarkup()
          button7 = types.InlineKeyboardButton(
              text='معلومات عن رقم التتبع', callback_data=f'track_info {tra}')
          button8 = types.InlineKeyboardButton(
              text='تفاصيل اكثر', callback_data=f'show_data {tracking_numb}')
          button9 = types.InlineKeyboardButton(
              text='موقع الطرد', callback_data=f'location {tracking_numb}')
          markuplang2.add(button8, button7)
          markuplang2.add(button9)
          if tracking_numb[-2:] == 'TW':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id,
                           contry_photo.get('taiwan'),
                           f"{time}   {text}",
                           reply_markup=markuplang2)
          elif tracking_numb[-2:] == 'SG':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id,
                           contry_photo.get('sengapora'),
                           f"{time}   {text}",
                           reply_markup=markuplang2)
          elif tracking_numb[-2:] == 'NL':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id,
                           contry_photo.get('sengapora'),
                           f"{time}   {text}",
                           reply_markup=markuplang2)
          else:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id,
                             f"{time}   {text}",
                             reply_markup=markuplang2)

          #bot.send_message(call.message.chat.id,get_data(url, tracking_numb)[0])
  if call.data.split()[0] == "track_info":
    if call.data.split()[1] == 'RB':
      bot.delete_message(call.message.chat.id, call.message.message_id)
      bot.send_message(
          call.message.chat.id,
          "\n رقم التتبع بريد مسجل \n بريد سنغفوري \n معدل مدة الوصول الى جزائر 16 الى 24 يوم\n \n "
      )
  elif call.data.split()[0] == "location":
    user_id = str(call.message.chat.id)
    tracking_number = call.data.split()[1]
    url = generate_tracking_url(tracking_number, 'en')
    data = short_data(url, tracking_number)
    loc = str(data[0])
    if loc in arr_depart_transit or loc in arr_arrived_transit:
      locations = get_location(tracking_number)
      bot.delete_message(call.message.chat.id, call.message.message_id)
      bot.send_location(call.message.chat.id, locations[1], locations[0])
    elif loc in arr_arrive_alg or loc in arr_alge:
      locations = get_longitude_for_location("Algiers", "Algeria")
      bot.delete_message(call.message.chat.id, call.message.message_id)
      bot.send_location(call.message.chat.id, locations[1], locations[0])

    else:
      locations = get_longitude_for_location("Beijing", "China")
      bot.delete_message(call.message.chat.id, call.message.message_id)
      bot.send_location(call.message.chat.id, locations[1], locations[0])
    """"if tracking_numb[:2] == "RB":
              s = get_longitude_for_location("singapore", "Singapore")
          if loca in arr_arrived_transit or loca in arr_depart_transit:
            if tracking_numb[:2] == "RB":
              s = get_longitude_for_location("singapore", "Singapore")
              print(s)"""
  elif call.data.split()[0] == "show_data":
    user_id = str(call.message.chat.id)
    for user in user_urls['users']:
      if user['id'] == user_id:

        for button in user['orders']:

          if button["number"] == call.data.split()[1]:
            tracking_numb = button["number"]

            url = generate_tracking_url(button['number'], user['language'])
            tetx = get_data(url, tracking_numb)[0]
            bot.delete_message(call.message.chat.id, call.message.message_id)

            bot.send_message(call.message.chat.id, tetx)
  if call.data == 'العربية':
    user_id = str(call.message.chat.id)
    Lang = "ar"
    if check_user_id('users_data.json', user_id):
      for user in user_urls['users']:
        user['language'] = Lang
    else:
      new_user = {"id": user_id, "language": Lang}
      user_urls["users"].append(new_user)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Done")
    with open('users_data.json', 'w') as file:
      json.dump(user_urls, file)
  if call.data == 'francais':
    user_id = str(call.message.chat.id)
    Lang = "fr"
    if check_user_id('users_data.json', user_id):
      for user in user_urls['users']:
        user['language'] = Lang
    else:
      new_user = {"id": user_id, "language": Lang}
      user_urls["users"].append(new_user)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Done")
    with open('users_data.json', 'w') as file:
      json.dump(user_urls, file)

  if call.data == 'anglish':

    user_id = str(call.message.chat.id)
    Lang = "en"
    if check_user_id('users_data.json', user_id):
      for user in user_urls['users']:
        user['language'] = Lang
    else:
      new_user = {"id": user_id, "language": Lang}
      user_urls["users"].append(new_user)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Done")

    with open('users_data.json', 'w') as file:
      json.dump(user_urls, file)


keep_alive()
bot.infinity_polling()
