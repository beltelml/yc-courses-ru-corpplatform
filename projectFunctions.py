#Load necessary libraries
import mysql.connector
import random
from faker import Faker
from projectCollections import sqls, stores
from datetime import timedelta, datetime
import pandas as pd

f = Faker('ru_RU')

date_grid_entity = datetime.now();
grid_increment_id = '00000000001'
grid_entity_id = 1
item_item_id = 2

total_record_inserted = 0
total_orders_inserted = 0

def GenCoordinate():
    yCoor = [37,38]
    chance = [90,10]
    return '[55.'+str(random.randint(0, 999999))+','+str(random.choices(yCoor,chance)).replace('[', '').replace(']', '') + '.' + str(random.randint(0, 999999))+']'

def ParseSql(sql_items, created_at):
    sql_items_copy = sql_items.copy();
    global grid_entity_id
    global grid_increment_id
    global item_item_id
    grid_entity_id = grid_entity_id + 1
    item_item_id = item_item_id + 1
    next_item_item_id = item_item_id + 1
    next_p1_item_item_id = next_item_item_id + 1
    next_p2_item_item_id = next_item_item_id + 2
    grid_increment_id = str((int(grid_increment_id) + 1))

    billing_address = f.address()
    customer_email = f.email()
    names = f.name().split(" ")
    customer_first_name = names[0]#f.first_name()
    customer_lastname = names[1]#f.last_name()
    customer_name = customer_first_name+' '+customer_lastname
    ip_address = f.ipv4()
    pickup_location_code = GenCoordinate();
    updated_at = created_at + pd.DateOffset(seconds=random.randint(4, 30))
    protection_code = f.uuid4().replace('-','')

    store = random.choice(stores)

    for item in sql_items:
        sql_items_copy[item] = sql_items_copy[item].replace('{grid_entity_id}', str(grid_entity_id))
        sql_items_copy[item] = sql_items_copy[item].replace('{grid_increment_id}', grid_increment_id)
        sql_items_copy[item] = sql_items_copy[item].replace('{item_item_id}', str(item_item_id))
        sql_items_copy[item] = sql_items_copy[item].replace('{next_item_item_id}', str(next_item_item_id))
        sql_items_copy[item] = sql_items_copy[item].replace('{next_p1_item_item_id}', str(next_p1_item_item_id))
        sql_items_copy[item] = sql_items_copy[item].replace('{next_p2_item_item_id}', str(next_p2_item_item_id))        
        sql_items_copy[item] = sql_items_copy[item].replace('{created_at}', str(created_at))
        sql_items_copy[item] = sql_items_copy[item].replace('{updated_at}', str(updated_at))
        sql_items_copy[item] = sql_items_copy[item].replace('{billing_address}', billing_address)
        sql_items_copy[item] = sql_items_copy[item].replace('{shipping_address}', billing_address)
        sql_items_copy[item] = sql_items_copy[item].replace('{customer_email}', customer_email)
        sql_items_copy[item] = sql_items_copy[item].replace('{customer_name}', customer_name)
        sql_items_copy[item] = sql_items_copy[item].replace('{customer_first_name}', customer_first_name)
        sql_items_copy[item] = sql_items_copy[item].replace('{customer_lastname}', customer_lastname)
        sql_items_copy[item] = sql_items_copy[item].replace('{ip_address}', ip_address)
        sql_items_copy[item] = sql_items_copy[item].replace('{pickup_location_code}', pickup_location_code)
        sql_items_copy[item] = sql_items_copy[item].replace('{shipping_location}', pickup_location_code)
        sql_items_copy[item] = sql_items_copy[item].replace('{store_id}', str(store['id']))
        sql_items_copy[item] = sql_items_copy[item].replace('{store_name}', store['name'])
        sql_items_copy[item] = sql_items_copy[item].replace('{protection_code}', protection_code)
        
    item_item_id = next_item_item_id + 1
    return sql_items_copy
def OpenConnection(host):
    cnx = mysql.connector.connect(user='magento-svc', password='m@gent0',
                              host=host,
                              database='ya_sample_store')
    return cnx

def OpenCursor(cnx):
    cur = cnx.cursor()
    return cur

def InsertData(cur, sql_item):
    global total_record_inserted
    global total_orders_inserted
    total_orders_inserted = total_orders_inserted + 1
    for item in sql_item:
        try:            
            cur.execute(sql_item[item])
        except Exception as e:
            print(sql_item[item])
            print(e)
            raise
        total_record_inserted = total_record_inserted + 1


def CommitData(cnx, cur):
    cnx.commit()
    cur.close()
    cnx.close()

def SaveTextToFile(text):
    with open('sql_commands.txt', 'a') as file:                
        file.write(text+'\n')
                

def SaveToFile(sql_item):
    with open('sql_commands.txt', 'a') as file:
                for item in sql_item:
                    sql = sql_item[item]
                    sql = sql[:-1]
                    file.write(sql+'\n')
                    file.write('#'+'\n')
                


def LoadData(host):
    global grid_entity_id
    global grid_increment_id
    global date_grid_entity
    global item_item_id
    cnx = mysql.connector.connect(user='magento-svc', password='m@gent0',
                              host=host,
                              database='ya_sample_store')
    cursor = cnx.cursor()

    query = ("select max(sog.entity_id) as max_entity_id, max(sog.created_at) as max_created_at, CAST(max(sog.increment_id) as char(50)) as max_increment_id from sales_order_grid sog")

    cursor.execute(query)

    grid_entity_id, date_grid_entity, grid_increment_id = cursor.fetchone()

    cursor.close()

    cursor = cnx.cursor()
    query = ("select max(soi.item_id) as max_item_id from sales_order_item soi")

    cursor.execute(query)

    item_item_id = cursor.fetchone()[0]

    

    cursor.close()

    cnx.close()

