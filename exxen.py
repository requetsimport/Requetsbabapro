import requests
import json
import random
from datetime import datetime
import base64
from Crypto.Cipher import AES
import re
import string

def pkcs7_pad(data, block_size=16):
    pad = block_size - (len(data) % block_size)
    return data + bytes([pad] * pad)

def pkcs7_unpad(data):
    pad = data[-1]
    return data[:-pad]

def aes_encrypt_urlsafe(plaintext, base64_key):
    key = base64.b64decode(base64_key)
    padded = pkcs7_pad(plaintext.encode('utf-8'))
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(encrypted).decode('utf-8')

def aes_decrypt_urlsafe(encrypted_b64, base64_key):
    key = base64.b64decode(base64_key)
    encrypted = base64.b64decode(encrypted_b64)
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(encrypted)
    return pkcs7_unpad(decrypted).decode('utf-8')

# Kullanıcıdan kart bilgilerini al
card_input = input("Kart bilgilerini (cardno|ay|yıl|cvv) şeklinde girin: ").strip()
card_parts = card_input.split('|')
if len(card_parts) != 4:
    exit(0)

card_number, month, year, cvv = card_parts

# Ay formatını düzelt (tek haneli ise başına 0 ekle)
month = month.zfill(2)

# Yıl formatını düzelt (4 haneli ise son 2 hanesini al)
if len(year) == 4:
    year = year[2:]

session = requests.Session()

# Rastgele kullanıcı bilgileri oluştur
first_names = ["Ahmet", "Mehmet", "Mustafa", "Ali", "Emre", "Burak", "Can", "Deniz", "Eren", "Hasan"]
last_names = ["Yilmaz", "Kaya", "Demir", "Celik", "Sahin", "Yildiz", "Aydin", "Ozturk", "Kurt", "Aslan"]

first_name = random.choice(first_names)
last_name = random.choice(last_names)
patterns = [
    f"{first_name.lower()}.{last_name.lower()}{random.randint(10,999)}",
    f"{first_name.lower()}{last_name.lower()}{random.randint(1000,9999)}",
    f"{first_name[0].lower()}{last_name.lower()}{random.randint(100,999)}",
    f"{first_name.lower()}_{last_name.lower()}"
]
random_email = f"{random.choice(patterns)}@gmail.com"
full_name = f"{first_name} {last_name}"

# Kayıt payload'ı
payload = json.dumps({
  "username": random_email,
  "password": "burakyalxin1B",
  "email": random_email,
  "country": "TR",
  "isPrivacyPoliciesAccepted": True,
  "isTAndCAccepted": True,
  "alertNotificationTxnSMS": True,
  "emailNotification": True,
  "phoneNumber": "",
  "name": full_name,
  "language": "EN",
  "deviceDetails": {
    "deviceName": "Chrome",
    "deviceType": "tablet",
    "modelNo": "137.0.0.0",
    "serialNo": "137.0.0.0",
    "brand": "Chrome",
    "os": "Android",
    "osVersion": "10"
  }
})

headers = {
  'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
  'Accept': "application/json, text/plain, */*",
  'Content-Type': "application/json",
  'sec-ch-ua': "\"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
  'sec-ch-ua-mobile': "?0",
  'sec-ch-ua-platform': "\"Android\"",
  'origin': "https://www.exxen.com",
  'sec-fetch-site': "same-site",
  'sec-fetch-mode': "cors",
  'sec-fetch-dest': "empty",
  'referer': "https://www.exxen.com/",
  'accept-language': "en-US,en;q=0.9,tr;q=0.8"
}

# Kullanıcı kaydı
url = "https://mw-proxy.app.exxen.com/user/register"
response = session.post(url, data=payload, headers=headers)

if response.status_code == 201:
    res_data = response.json()
    auth_token = res_data['bearer']['auth']['token']
    
    # Ödeme imzası oluştur
    url = "https://mw-proxy.app.exxen.com/user/generatePaymentSignature"
    payload = json.dumps({
      "query": f"successCallbackURL=https%3A%2F%2Fwww.exxen.com%2F&failureCallbackURL=https%3A%2F%2Fwww.exxen.com%2Fsubscription&sku=SPOR%2CEXXEN-RKLMYOK-WITHOUT-AD%2CEXXEN-RKLMVAR-WITH-AD&amount=499&dmaID=TR&currencyCode=TL&couponCode=&userip=&transactionType=PURCHASE&locale=EN&accessToken={auth_token}&tracking=0&backUrl=https%3A%2F%2Fwww.exxen.com%2Fsubscription&planChange=FALSE"
    })
    headers['authorization'] = f"Bearer {auth_token}"
    response = session.post(url, data=payload, headers=headers)
    
    if response.status_code == 200:
        veri = response.json()
        signature = veri["signature"]
        ip_adresi = veri["ip"]
        
        # Ödeme sayfasına yönlendirme
        url = "https://exxen-web.evergent.com/api/paytr/checkout"
        payload = f"successCallbackURL=https%3A%2F%2Fwww.exxen.com%2F&failureCallbackURL=https%3A%2F%2Fwww.exxen.com%2Fsubscription&sku=SPOR%2CEXXEN-RKLMYOK-WITHOUT-AD%2CEXXEN-RKLMVAR-WITH-AD&amount=499&dmaID=TR&currencyCode=TL&couponCode=&userip={ip_adresi}&transactionType=PURCHASE&locale=EN&accessToken={auth_token}&tracking=0&backUrl=https%3A%2F%2Fwww.exxen.com%2Fsubscription&planChange=FALSE&signature={signature}"
        
        headers = {
          'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
          'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
          'Content-Type': "application/x-www-form-urlencoded",
          'cache-control': "max-age=0",
          'sec-ch-ua': "\"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
          'sec-ch-ua-mobile': "?0",
          'sec-ch-ua-platform': "\"Android\"",
          'upgrade-insecure-requests': "1",
          'origin': "https://www.exxen.com",
          'sec-fetch-site': "cross-site",
          'sec-fetch-mode': "navigate",
          'sec-fetch-user': "?1",
          'sec-fetch-dest': "document",
          'referer': "https://www.exxen.com/",
          'accept-language': "en-US,en;q=0.9,tr;q=0.8"
        }
        
        response = session.post(url, data=payload, headers=headers,allow_redirects=False)
        html_content = response.text
        
        # Checkout ID'yi regex ile al
        match = re.search(r'/checkout/([a-zA-Z0-9_-]+)', html_content)
        if match:
            checkout_id = match.group(1)
            
            # Rastgele merchant_oid oluştur
            prefix = ''.join(random.choices(string.ascii_uppercase, k=24))
            timestamp = str(int(datetime.now().timestamp() * 1000))
            merchant_oid = prefix + timestamp
            
            # Kredi kartı bilgileriyle ödeme yap
            json_data = {
              "data": {
                "values": {
                  "cardIcon": "",
                  "params": {
                    "successCallbackURL": "https://www.exxen.com/",
                    "failureCallbackURL": "https://www.exxen.com/subscription",
                    "sku": "SPOR,EXXEN-RKLMYOK-WITHOUT-AD,EXXEN-RKLMVAR-WITH-AD",
                    "dmaID": "TR",
                    "currencyCode": "TL",
                    "couponCode": "",
                    "userip": ip_adresi,
                    "transactionType": "PURCHASE",
                    "locale": "EN",
                    "tracking": "0",
                    "backUrl": "https://www.exxen.com/subscription",
                    "planChange": "FALSE"
                  },
                  "transactionId": checkout_id,
                  "skuList": [
                    "SPOR",
                    "EXXEN-RKLMYOK-WITHOUT-AD",
                    "EXXEN-RKLMVAR-WITH-AD"
                  ],
                  "channelPartnerID": "EXXEN_TR",
                  "cpCustomerID": res_data['accountId'],
                  "email": random_email,
                  "firstName": first_name,
                  "merchant_oid": merchant_oid,
                  "user_basket": "[]",
                  "card_type": "",
                  "card_number": card_number,
                  "expiry_month": month,
                  "expiry_year": year,
                  "cvv": cvv,
                  "cc_owner": full_name
                }
              },
              "action": "api/paytr/submitaction"
            }
            
            key = "ZW9ueHNJWUFMcVd6M25GRw=="
            plaintext = json.dumps(json_data, separators=(',', ':'))
            encrypted = aes_encrypt_urlsafe(plaintext, key)
            
            url = "https://exxen-web.evergent.com/api/paytr/submitaction"
            submit_payload = json.dumps({
              "q": encrypted
            })
            submit_headers = {
              'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
              'Accept': "application/json, text/plain, */*",
              'Content-Type': "application/json",
              'sec-ch-ua': "\"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
              'sec-ch-ua-mobile': "?0",
              'sec-ch-ua-platform': "\"Android\"",
              'origin': "https://exxen-web.evergent.com",
              'sec-fetch-site': "same-origin",
              'sec-fetch-mode': "cors",
              'sec-fetch-dest': "empty",
              'referer': f"https://exxen-web.evergent.com/checkout/{checkout_id}",
              'accept-language': "en-US,en;q=0.9,tr;q=0.8",
            }
            
            response = session.post(url, data=submit_payload, headers=submit_headers)
            
            if response.status_code == 200:
                response_json = response.json()
                encrypted_response = response_json['r']
                decrypted_response = aes_decrypt_urlsafe(encrypted_response, key)
                print(decrypted_response)