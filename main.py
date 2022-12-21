#Load necessary libraries
import random

import pandas as pd
from datetime import timedelta, datetime

from projectCollections import *
from projectFunctions import *
import projectFunctions
from alive_progress import alive_bar
from rich.console import Console
from rich.markdown import Markdown  
from rich.prompt import Prompt
from rich import print
from rich.progress import Progress
from rich.pretty import pprint

import time

WELCOME_SCREEN = """

# **Yandex Magento Orders Generator**

*Welcome to Yandex Magento order generation system in the Magento e-store*

When generating orders, the following fake data is created

1. Names and surnames of people
2. Order dates
3. Addresses and countries
4. ZIP codes of addresses
5. IP addresses
6. Email addresses
7. Geocoordinates 
8. UID order codes
9. Order IDs
10. Orders from different online stores
11. and much more :)

**Copyright: Yandex Cloud Team {current_year}**

***Author: Pavel Karpenko***
"""

WELCOME_SCREEN = WELCOME_SCREEN.replace('{current_year}', datetime.today().strftime('%Y'))

console = Console()
md = Markdown(WELCOME_SCREEN)
console.print(md)

default_host_address = 'localhost'
print(' ')
mysql_host = Prompt.ask("Enter the MySQL Server host address ", default=default_host_address)#str(input('=========== Enter the MySQL Server host address: '))
LoadData(mysql_host)

gen_until_year = datetime.today().strftime('%Y')
gen_until_year = Prompt.ask('Enter the year [bold red](yyyy)[/bold red] by which the orders should be generated.', default=datetime.today().strftime('%Y'))

gen_until_date = gen_until_year + '-12-31'
projectFunctions.date_grid_entity = datetime.strptime(gen_until_year+"-01-01 01:01:01", "%Y-%m-%d %H:%M:%S")
gen_running = True
default_max_daily_orders_count = 230


max_daily_orders_count = Prompt.ask('Enter the maximum number of orders per day', choices=['10', '100', '200', '230'], default=str(default_max_daily_orders_count))
if (max_daily_orders_count == ''):
    print('Will be used default value => ' + str(default_max_daily_orders_count))
    max_daily_orders_count = default_max_daily_orders_count

max_daily_orders_count = int(max_daily_orders_count)


print(' ')

max_daily_order_freq_in_seconds = 20
saveToFile = False
saveToDb = True

if saveToFile == True:
    open('sql_commands.txt', 'w').close()

if (saveToDb == True):
    cnx = OpenConnection(mysql_host)
    cur = OpenCursor(cnx=cnx)
    
    '''
    DeleteData(cur)
    CommitData(cnx=cnx, cur=cur)
    cnx = OpenConnection(mysql_host)
    cur = OpenCursor(cnx=cnx)
    '''

delta = (datetime.strptime(gen_until_date, "%Y-%m-%d").date()) - projectFunctions.date_grid_entity.date()

MAX_ORDERS_COUNT = 40000
COMMIT_EVERY_TRANSACTIONS_COUNT = 10000
order_count = 0
transactions_count = 0

#with alive_bar(delta.days + 1) as bar:
with Progress() as progress:
    task0 = progress.add_task("[red]Deleting old orders...", start=False, total=100)
    
    if (saveToDb == True):
        DeleteData(cur)
        CommitData(cnx=cnx, cur=cur)
        cnx = OpenConnection(mysql_host)
        cur = OpenCursor(cnx=cnx)
    
    
    progress.update(task0, completed=100)
    progress.start_task(task0)    

    task1 = progress.add_task("[cyan]Generating orders...", total=delta.days + 1)
    while (gen_running == True):
        #print('order_count => '+str(order_count))
        progress.update(task1, advance=1)
        if projectFunctions.date_grid_entity.strftime('%Y-%m-%d') == gen_until_date:
            gen_running = False
            if saveToDb == True:
                CommitDataAndClose(cnx=cnx, cur=cur)
                progress.update(task1,completed=delta.days + 1)
        if gen_running == True:            
            projectFunctions.date_grid_entity = projectFunctions.date_grid_entity + pd.DateOffset(days=1, hour=random.randint(0, 20), minute=random.randint(0, 59), second=random.randint(0, 59))
            if saveToFile == True:
                SaveTextToFile('Date Range ========== > projectFunctions.date_grid_entity => '+str(projectFunctions.date_grid_entity))
            datelist = pd.date_range(start=projectFunctions.date_grid_entity, periods=random.randint(1, max_daily_orders_count), freq=str(random.randint(1, max_daily_order_freq_in_seconds))+'S').sort_values().tolist()
            for date_item in datelist:
                sql_item = ParseSql(sql_items=random.choice(sqls),created_at= date_item)
                if saveToFile == True:
                    SaveToFile(sql_item)
                if (saveToDb == True):
                    order_count = order_count + 1
                    if (transactions_count == COMMIT_EVERY_TRANSACTIONS_COUNT):
                        CommitData(cnx=cnx, cur=cur)
                        cur = OpenCursor(cnx=cnx)
                        transactions_count = 0
                    #print('order_count => ' + str(order_count))
                    if (MAX_ORDERS_COUNT >= order_count):
                        InsertData(cur=cur,sql_item=sql_item)
                        transactions_count = transactions_count + 1
                    else:
                        gen_running = False
                        if saveToDb == True:
                            CommitDataAndClose(cnx=cnx, cur=cur)
                            progress.update(task1,completed=delta.days + 1)
                        break
print(' ')
print('Total rows have been inserted: ' + str(projectFunctions.total_record_inserted) + ' rows')
print('Total orders have been created: ' + str(projectFunctions.total_orders_inserted) + ' orders')
print(' ')
