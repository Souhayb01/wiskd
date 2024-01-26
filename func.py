import requests
import pycountry

import telebot
from telebot import types
import json
from geopy.geocoders import Nominatim

token = '6540253678:AAHaEit8_RW1hT7nJtQHz4jVaiBscqN3zrs'
bot = telebot.TeleBot(token, parse_mode=None)

contry_photo = {
    "taiwan":
    "AgACAgQAAxkBAAMkZa7YOyNRU4Te_l0bYrKTMM7r_cAAAr7AMRsp0XFR8_4HW5UO-qkBAAMCAANzAAM0BA",
    "sengapora":
    "AgACAgQAAxkBAAMjZa7YFCG_Oss2AjF4jHphebh5l94AArzAMRsp0XFRLge2DQQOzkUBAAMCAANzAAM0BA",
    "holanda":
    "AgACAgQAAxkBAAMlZa7YZITH1MqGIPLdtbW314MgoIMAAr_AMRsp0XFRrEaVP3bx98ABAAMCAANzAAM0BA"
}
arr_logi = [
    "تم الإستلام من قبل شركة الخدمات اللوجستية",
    "Received by logistics company", "Reçu par la société de logistique",
    "[Xiaoshan District] قيد المعالجة في مركز التصنيف",
    "[Xiaoshan District] Processing at sorting center",
    "[Xiaoshan District] A quitté le centre de tri"
]
arr_1 = [
    "Informations de livraison reçues par l'entrepôt par voie électronique",
    "Shipment information received by warehouse electronically",
    "تم إستلام بيانات الشحن إلكترونياً من قبل المخزن"
]
arr_from_chine = [
    "قيد مغادرة دولة/منطقة الإنطلاق", "Leaving from departure country/region",
    "En partance du pays/région de départ"
]
arr_arrived_transit = [
    "تم الوصول إلى دولة/منطقة التحويل", "Arrived in transit country/region",
    "Arrivé dans le pays/région de transit"
]
arr_depart_transit = [
    "تم مغادرة دولة/منطقة التحويل", "Departed from transit country/region",
    "A quitté le pays/région de transit"
]
arr_arrive_alg = [
    "تم الوصول إلى مكتب التحويل", "Arrived at linehaul office",
    "Arrivé au bureau de transport"
]
arr_alge = [
    "تم الإستلام من قبل شركة التوصيل المحلية",
    " تم الوصول إلى مركز التوصيل المحلي", "Arrived at local delivery center",
    " Received by local delivery company",
    "Arrivé au centre de livraison local",
    "Reçu par la société de livraison locale",
  "[Xiaoshan District] تم مغادرة مركز التصنيف",
  "وصل مركز النقل ببلد المغادرة"

]


def get_location(tracking_number):

  if tracking_number[:2] == "RB":
    return get_longitude_for_location("Sinagpore", "Sinagpore")
  if tracking_number[-2:] == "CZ":
    return get_longitude_for_location("Prague", "Czech Republic")
  if tracking_number[-2:] == "NL":
    return get_longitude_for_location("Amsterdam", "Netherlands")
  if tracking_number[-2:] == "TW":
    return get_longitude_for_location("Taipei", "Taiwan")
  if tracking_number[-2:] == "UZ":
    return get_longitude_for_location("Tashkent", "Uzbekistan")

def has_chat_id(data,user_id):
 for user in data["users"]:
    if user["id"] == user_id:
        return "chat_id" in user
 return False

def short_data(url, tracking_number):
  try:
    response = requests.get(url)

    if response.status_code == 200:
      data = json.loads(response.text)
      module_data = data.get("module")
      days_number = data["module"][0]["daysNumber"]

      detailList = next(item["detailList"] for item in module_data
                        if "detailList" in item)
      type_TRa = tracking_number[:2]

      first_event_processed = True
      for event in detailList:
        if first_event_processed:
          standerd_desc = event["standerdDesc"]
          time_str = event["timeStr"]
          type_TRa = tracking_number[:2]
          return standerd_desc, time_str, type_TRa
        first_event_processed = False

  except Exception as e:
    return 'send correct tracking number'


def get_country_name_by_code(country_code):
  try:
    country = pycountry.countries.get(alpha_2=country_code)
    if country:
      return country.name
    else:
      return "Country not found"
  except Exception as e:
    return f"Error: {e}"


def get_longitude_for_location(country, state):
  geolocator = Nominatim(user_agent="state_geocoding")
  location = geolocator.geocode(f"{state}, {country}")

  if location:
    location2 = [location.longitude, location.latitude]
    return location2
  else:
    print(f"Location not found for {state_name}")
    return None


def check_user_id(json_file, user_id):
  # Load the JSON data from the file
  with open(json_file, "r") as file:
    data = json.load(file)
  for user in data["users"]:
    if user["id"] == user_id:
      return True

  return False

def track_shipment(tracking_number):
   url_template = "https://global.cainiao.com/global/detail.json?mailNos={}&lang=en&language=en"
   url = url_template.format(tracking_number)
   response = requests.get(url)

   if response.status_code == 200:
      data = response.json()

      module_data = data.get('module', [])
      if module_data and 'detailList' in module_data[0] and module_data[0]['detailList'] == []:
        return True
      return False
   else:
      return False

def generate_tracking_url(tracking_number, language="en-US"):
  url_template = "https://global.cainiao.com/global/detail.json?mailNos={}&lang={}&language={}"
  return url_template.format(tracking_number, language, language)


def get_data(url, tracking_number):

  response = requests.get(url)

  if response.status_code == 200:
    data = json.loads(response.text)
    module_data = data.get("module")
    days_number = data["module"][0]["daysNumber"]

    detailList = next(item["detailList"] for item in module_data
                      if "detailList" in item)
    first_event_processed = True

    # Initialize empty string to store combined information

    unique_events = set()
    combined_info = ""
    for event in detailList:

        standerd_desc = event["standerdDesc"]
        time_str = event["timeStr"]



        if standerd_desc in arr_arrived_transit:
          contry = tracking_number[-2:]
          #print(get_country_name_by_code(contry))
          if contry == 'SG':
            combined_info += f'{time_str}\n {standerd_desc}\n----------------🛬🇸🇬📦------------------\n'
          elif contry == 'PL':
            combined_info += f'{time_str}\n {standerd_desc}\n----------------🛬🇵🇱📦-----------------\n'
          elif contry == 'TW':
            combined_info += f'{time_str}\n {standerd_desc}\n-----------------🛬🇹🇼📦---------------\n'
        elif standerd_desc in arr_depart_transit:
          contry = tracking_number[-2:]
          #print(get_country_name_by_code(contry))
          if contry == 'SG':
            combined_info += f'{time_str}\n {standerd_desc}\n-------------------------🛫🇸🇬📦-------------------------\n'
          elif contry == 'PL':
            combined_info += f'{time_str}\n {standerd_desc}\n-------------------------🛫🇵🇱📦-------------------------\n'
          elif contry == 'TW':
            combined_info += f'{time_str}\n {standerd_desc}\n-------------------------🛫🇹🇼📦-------------------------\n'
        elif standerd_desc in arr_arrive_alg:
          combined_info += f'{time_str}\n {standerd_desc}\n-------------------------🛬🇩🇿📦-------------------------\n'
        elif standerd_desc in arr_logi:
          combined_info += f'{time_str}\n {standerd_desc}\n-------------------------🏢🏢-------------------------\n'
        elif standerd_desc in arr_1:
          combined_info += f'{time_str}\n {standerd_desc}\n-------------------------📋📋-------------------------\n'
        elif standerd_desc in arr_alge:
          combined_info += f'{time_str}\n {standerd_desc}\n-------------------------🚚🚚-------------------------\n'
        elif standerd_desc == 'الطرد جاهز للشحن من قِبل المستودع' or standerd_desc == "تم شحن وإرسال الطرد من المستودع":
          combined_info += f'{time_str}\n {standerd_desc}\n-------------------------📦-------------------------\n'

        elif standerd_desc in arr_from_chine:
          combined_info += f'{time_str}\n {standerd_desc}\n-------------------------🛫🇨🇳📦-------------------------\n'
        elif standerd_desc == 'تم الوصول إلى مكتب التحويل' or standerd_desc == "قيد مغادرة دولة/منطقة الإنطلاق":
          combined_info += f'{time_str}\n {standerd_desc}\n-------------------------✈️-------------------------\n'
        # Concatenate time and title for each event
        else:
          combined_info += f'{time_str}\n {standerd_desc}\n-------------------------📦📦-------------------------\n'
    return combined_info, days_number
    # Print and send a single message with all combined information
