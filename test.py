import json
import urllib3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    print(json.dumps(event))

    track_pod_api_key = 'dfa0ded8-0e73-4ee1-88d9-cbd327806efa'

    body = json.loads(event['body'])
    count = 0
    if 'count' in body:
        count = body['count']

    logger.info('New orders: {}'.format(count))

    http = urllib3.PoolManager()

    if 'orders' not in body:
        logger.error('No orders')
        return {
            'statusCode': 403,
            'data': 'no orders found',
        }

    for x in body['orders']:

        order_id = x['id']

        order_type = x['type']  # we use only "delivery
        order_status = x['status']  # we user only "accepted"
        order_payment_method = x['payment']
        order_accepted_at = x['accepted_at']
        order_fulfill_at = x['fulfill_at']  # UTC date string of when the order will be delivered or picked up.
        order_updated_at = x['updated_at']
        order_instructions = x['instructions']  # instructions from client
        order_restaurant_id = x['restaurant_id']
        order_restaurant_name = x['restaurant_name']
        '''restaurant_phone    string    phone of the restaurant
        restaurant_country    string    country of the restaurant
        restaurant_state    string    state of the restaurant
        restaurant_city    string    city of the restaurant
        restaurant_zipcode    string    zipcode of the restaurant
        restaurant_street    string    street of the restaurant
        restaurant_latitude    string    latitude of the restaurant
        restaurant_longitude    string    longitude of the restaurant
        restaurant_timezone    string    timezone of restaurant; this is set automatically when you set the exact location in the Admin panel
        '''
        order_restaurant_key = x['restaurant_key']
        order_restaurant_token = x['restaurant_token']

        order_client_id = x['client_id']
        order_client_first_name = x['client_first_name']
        order_client_last_name = x['client_last_name']
        order_client_email = x['client_email']
        order_client_phone = x['client_phone']

        order_client_address = x['client_address']
        order_client_address_parts = x['client_address_parts']  # TODO: check it
        order_latitude = x['latitude']
        order_longitude = x['longitude']

        order_total_price = x['total_price']
        order_coupons = x['coupons']  # ist of promotion ids corresponding to coupon codes used during the ordering process (including those which were not applied in the end)
        order_items = x['items']

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
            error = 'UNSUPPORTED type: {} in {}'.format(order_type, order_restaurant_name)
            logger.error(error)
            return {
                'statusCode': 500,
                'data': 'error',
            }

        headers = {
            'X-API-KEY': track_pod_api_key,
            'Content-Type' : 'application/json'
            }

        data = {
              "Number": order_id,
              "Id": '',
              "Date": order_accepted_at,
              "Type": "0",
              # "ShipperId": "357",
              # "Shipper": "Sanitex",
              "DepotId": "1",  # id magazynu
              "Depot": "9 Riverside, Salford M7 1PA",
              "ClientId": order_client_id,
              "Client": '{} {}'.format(order_client_first_name, order_client_last_name),
              # "AddressId": "13587",
              "Address": order_client_address,
              "AddressLat": order_latitude,
              "AddressLon": order_longitude,

              # "AddressZone": "Zone 1",

              # TODO: dodatkowe pole?
              "TimeSlotFrom": "2019-02-01T09:00:00",
              "TimeSlotTo": "2019-02-01T18:00:00",

              # "ServiceTime": "10",
              "Note": order_instructions,
              "ContactName": '{} {}'.format(order_client_first_name, order_client_last_name),
              "Phone": order_client_phone,
              "Email": order_client_email,
              # "Weight": "50.5",
              # "Volume": "8.54",
              # "Pallets": "3.5",
              # todo: dodatkowe pole?
              # "COD": "20.45",
              # "InvoiceId": "inv0002",
              # "CustomerReferenceId": "ord123/1",
              # "Barcode": "1234567890123",
              "GoodsList": [
                {
                  "OrderLineId": "22435324",
                  "GoodsId": "30495",
                  "GoodsName": "Some big mystic box",
                  "GoodsUnit": "pcs.",
                  "Note": "ID3658AAA",
                  "Quantity": "10.5",
                  "Cost": "2.99"
                }
              ],
#               "CustomFields": [
#                 {
#                   "Id": "cf_456",
#                   "Value": "string"
#                 }
#               ]
        }

        encoded_data = json.dumps(data).encode('utf-8')
    #     print(encoded_data)
        r = http.request(
            'POST',
            'https://api.track-pod.com/order/',
            body=encoded_data,
            headers=headers)

        #     res = json.loads(r.data.decode('utf-8'    ))
        logger.info('order {0} result {1}: {2}'.format(order_id, r.status, r.data))
    return {
        'statusCode': 200,
        'data': 'its work',
    }
