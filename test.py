import json
import urllib3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    '''
    api proxy from gloriafood to Track-POD
    We allow only POST request
    
    To add new restaurant coppy all settings but "Restaurant Key" must be unique
    Must set "SERVER_KEY" in envs
    Must set "TRACK_POD_API_KEY" in envs
    '''
    print("START ORDER")
    print(json.dumps(event))

    return_code = 200
    return_data = 'All ok'
    ''' API key for authorize track pod '''
    TRACK_POD_API_KEY = os.environ['TRACK_POD_API_KEY']
    ''' authorize is only check correct server key from gloriafood '''
    SERVER_KEY = os.environ['SERVER_KEY']

    '''body is content from aws api gateway post'''
    if 'body' not in event:
        logger.error('No body in call')
        return {
            'statusCode': 200,
            'data': 'No body in call: {0}'.format(event),
            'body' : 'co tu sie dzieje',
        }
    body = json.loads(event['body'])
    count = 0
    if 'count' in body:
        count = body['count']

    ''' when we send 500 gloria send email to admin '''
    if 'orders' not in body:
        logger.error('No orders')
        return {
            'statusCode': 500,
            'data': 'no orders found',
        }

    logger.info('New orders: {}'.format(count))
    http = urllib3.PoolManager()

    for x in body['orders']:

        order_id = x['id']

        order_type = x['type']  # we use only "delivery
        order_status = x['status']  # we user only "accepted"
        order_payment_method = x['payment']
        order_accepted_at = x['accepted_at']
        order_fulfill_at = x['fulfill_at']  # UTC date string of when the order will be delivered or picked up.
        order_for_later = x['for_later']
        order_updated_at = x['updated_at']
        order_instructions = x['instructions']  # instructions from client
        order_restaurant_id = x['restaurant_id']
        order_restaurant_name = x['restaurant_name']
        order_restaurant_phone = x['restaurant_phone']
        order_restaurant_country = x['restaurant_country']
#         order_restaurant_state = x['restaurant_state']
        order_restaurant_city = x['restaurant_city']
        order_restaurant_zipcode = x['restaurant_zipcode']
        order_restaurant_street = x['restaurant_street']
        order_restaurant_latitude = x['restaurant_latitude']
        order_restaurant_longitude = x['restaurant_longitude']
        order_restaurant_timezone = x['restaurant_timezone']

        order_restaurant_address = '{}, {} {}'.format(order_restaurant_street, order_restaurant_city, order_restaurant_zipcode)

        order_restaurant_key = x['restaurant_key']
        order_restaurant_token = x['restaurant_token']

        order_client_id = x['client_id']
        order_client_first_name = x['client_first_name']
        order_client_last_name = x['client_last_name']
        order_client_email = x['client_email']
        order_client_phone = x['client_phone']

        order_client_address = x['client_address']
#         order_client_address_parts = x['client_address_parts']
        order_latitude = x['latitude']
        order_longitude = x['longitude']

        order_total_price = x['total_price']
        order_coupons = x['coupons']  # ist of promotion ids corresponding to coupon codes used during the ordering process (including those which were not applied in the end)
        order_items = []
        for i in x['items']:
            item = {
              "OrderLineId": i['id'],
              "GoodsId": i['id'],
              "GoodsName": i['name'],
              "GoodsUnit": "pcs.",
              "Note": i['instructions'],
              "Quantity": i['quantity'],
              "Cost": i['price']
            }
            order_items.append(item)

        order_type = x['type']

        '''
        track-pod
        Order type:
        0 - Delivery order;
        1 - Pickup order
        
        COD    number($double)
        example: 20.45
        Amount of Cash on Delivery
        '''
        # raise error when type is not 'delivery'
        if order_type != "delivery":
            error = 'UNSUPPORTED order_type: {} in {}'.format(order_type, order_restaurant_name)
            logger.error(error)
            return {
                'statusCode': 500,
                'data': 'error',
            }
        if order_status != 'accepted':
            error = 'UNSUPPORTED order_status: {} in {}'.format(order_status, order_restaurant_name)
            logger.error(error)
            return {
                'statusCode': 500,
                'data': 'error',
            }

        headers = {
            'X-API-KEY': TRACK_POD_API_KEY,
            'Content-Type' : 'application/json'
            }
        order_TimeSlotFrom = order_accepted_at
        if order_for_later:
            order_TimeSlotFrom = order_fulfill_at

        data = {
              "Number": order_id,
              "Id": '',
              "Date": order_accepted_at,
              "Type": "0",
              # "ShipperId": "357",
              # "Shipper": "Sanitex",
              "DepotId": order_restaurant_id,  # id magazynu
              "Depot": order_restaurant_address,
              "ClientId": order_client_id,
              "Client": '{} {}'.format(order_client_first_name, order_client_last_name),
              # "AddressId": "13587",
              "Address": order_client_address,
              "AddressLat": order_latitude,
              "AddressLon": order_longitude,

              # "AddressZone": "Zone 1",

              "TimeSlotFrom": order_TimeSlotFrom,
              "TimeSlotTo": order_fulfill_at,

              # "ServiceTime": "10",
              "Note": order_instructions,
              "ContactName": '{} {}'.format(order_client_first_name, order_client_last_name),
              "Phone": order_client_phone,
              "Email": order_client_email,
              # "Weight": "50.5",
              # "Volume": "8.54",
              # "Pallets": "3.5",
              # "COD": "20.45",
              "CODActual":order_total_price,
              # "InvoiceId": "inv0002",
              # "CustomerReferenceId": "ord123/1",
              # "Barcode": "1234567890123",
              "GoodsList": order_items,
              "CustomFields": [
                {
                  "Id": "cf_1882",
                  "Value": order_payment_method
                },
                {
                  "Id": "cf_1883",
                  "Value": order_for_later
                }
              ]

        }

        encoded_data = json.dumps(data).encode('utf-8')
    #     print(encoded_data)
        r = http.request(
            'POST',
            'https://api.track-pod.com/order/',
            body=encoded_data,
            headers=headers)

        logger.info('order {0} result {1}: {2}'.format(order_id, r.status, r.data))

        if r.status != 201:
            return_code = 500
            return_data = r.data

    print("END ORDER")
    return {
        'statusCode': return_code,
        'data': return_data,
    }
