# utils.py

import requests
import json
from django.conf import settings


def clean_address(address):
    """Remove new lines & extra spaces"""
    if not address:
        return ""

    address = address.replace("\n", " ")
    address = " ".join(address.split())

    return address


def create_shipment(order, name, phone, pincode, city, state):

    url = f"{settings.DELIVERY_BASE_URL}/api/cmu/create.json"

    headers = {
        "Authorization": f"Token {settings.DELIVERY_API_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        # ✅ COD Logic
        cod_amount = str(order.total_price) if order.payment_method == "Cash On Delivery" else "0"

        # ✅ CLEAN ADDRESS पहले
        clean_add = clean_address(order.address)

        # ✅ JSON SAFE DATA (no manual string)
        shipment_data = {
            "shipments": [{
                "name": str(name),
                "add": clean_add,
                "pin": str(pincode),
                "city": str(city),
                "state": str(state),
                "phone": str(phone),
                "order": str(order.order_id),
                "products_desc": str(order.product) if order.product else "Custom Product",
                "quantity": int(order.quantity),
                "cod_amount": cod_amount,
                "payment_mode": "COD" if order.payment_method == "Cash On Delivery" else "Prepaid"
            }]
        }

        payload = {
            "format": "json",
            "data": json.dumps(shipment_data)   # ✅ सबसे important fix
        }


        response = requests.post(url, data=payload, headers=headers, timeout=10)


        data = response.json()

        # ❌ API error
        if data.get("error"):
            return data, None, None

        # ✅ SUCCESS
        packages = data.get("packages", [])

        if packages:
            package = packages[0]
            awb = package.get("waybill")
            ref = package.get("refnum")

            return data, awb, ref

        return data, None, None

    except requests.exceptions.RequestException as e:
        return None, None, None

    except Exception as e:
        return None, None, None
    
    
    




def track_shipment(awb):
    url = f"https://track.delhivery.com/api/v1/packages/json/?waybill={awb}"

    headers = {
        "Authorization": f"Token {settings.DELIVERY_API_TOKEN}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        shipment = data["ShipmentData"][0]["Shipment"]
        return shipment["Status"]["Status"]

    except Exception as e:
        return None


def map_status(delhivery_status, order=None):

    # ✅ LOCAL cancel सबसे पहले
    if order and order.status == "Cancelled":
        return "Cancelled"

    # 🔥 IMPORTANT FIX
    # अगर shipment_status "Not Picked" है और user cancel कर चुका है
    if delhivery_status == "Not Picked" and order and order.status == "Cancelled":
        return "Cancelled"

    if delhivery_status in ["Manifested"]:
        return "Ordered"

    elif delhivery_status in ["In Transit"]:
        return "Shipped"

    elif delhivery_status in ["Out for Delivery"]:
        return "Out for Delivery"

    elif delhivery_status in ["Delivered"]:
        return "Delivered"

    elif delhivery_status in ["Cancelled", "RTO"]:
        return "Cancelled"

    return "Processing"
    

def update_order_status(order):

    if not order.awb_number:
        return

    try:
        delhivery_status = track_shipment(order.awb_number)

        if not delhivery_status:
            return

        # 🔥 FIX 1
        new_status = map_status(delhivery_status, order)

        # 🔥 FIX 3 (cancel override protection)
        if order.status == "Cancelled":
            return

        # 🔥 FIX 2 (shipment_status update)
        if order.status != new_status or order.shipment_status != delhivery_status:

            order.status = new_status
            order.shipment_status = delhivery_status

            order.save()
            
    except Exception as e:
        print("Tracking Update Error:", e)
    
    
    

def cancel_shipment(awb):
    url = "https://track.delhivery.com/api/p/edit"

    headers = {
        "Authorization": f"Token {settings.DELIVERY_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "waybill": awb,
        "cancellation": "true"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return None
    
    
    
    