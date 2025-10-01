__artifacts_v2__ = {
    "get_cashAppB": {
        "name": "Cash App",
        "description": "",
        "author": "Alexis Brignoni",
        "creation_date": "2025-08-24",
        "last_update_date": "2025-08-24",
        "requirements": "none",
        "category": "Banking",
        "notes": "",
        "paths": ('*/Environments/Production/Accounts/*/*-internal.cashappapi.com.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "dollar-sign",
    }
}

import blackboxprotobuf
import json
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, convert_unix_ts_to_utc

@artifact_processor
def get_cashAppB(context):
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            
            query = """
            SELECT
            ZDISPLAYDATE,
            ZCUSTOMERTOKEN,
            ZSYNCCUSTOMER,
            ZSYNCPAYMENT
            FROM ZCUSTOMER
            JOIN ZPAYMENT
                ON ZCUSTOMER.ZCUSTOMERTOKEN = ZPAYMENT.ZREMOTECUSTOMERID;
            """
            results = get_sqlite_db_records(file_found, query)
        
            for row in results:
                timestamp = convert_unix_ts_to_utc(row[0])
                customertoken = row[1]
                protocustomer, types = blackboxprotobuf.decode_message(row[2])
                protopayment, types = blackboxprotobuf.decode_message(row[3])
        
                payment = (protopayment['1'].get('16'))
                if payment is not None:
                    payment = payment.decode()
                    payment = json.loads(payment)
                    amount = payment.get('amount')
                    howmuch = amount['amount']
                    currency = amount['currency_code']
                    note = payment.get('note')
                    role = (payment.get('role'))
                    
                    #Estan bajo instrument
                    if payment.get('instrument') is not None:
                        cardbrand = (payment['instrument'].get('card_brand'))
                        suffix = (payment['instrument'].get('suffix'))
                        displayname = (payment['instrument'].get('display_name'))
                        
                    displayinstrument = (payment.get('display_instrument'))
                    instrumenttype = (payment.get('instrument_type'))
                    transactionid = (payment.get('transaction_id'))
                    state = (payment.get('state'))
                    
                    createdat = (payment.get('created_at'))
                    if createdat is not None:
                        createdat = convert_unix_ts_to_utc(createdat)
                        
                    capturedat = (payment.get('captured_at'))
                    if capturedat is not None:
                        capturedat = convert_unix_ts_to_utc(capturedat)
                        
                    reachedcustomerat = (payment.get('reached_customer_at'))
                    if reachedcustomerat is not None:
                        reachedcustomerat = convert_unix_ts_to_utc(reachedcustomerat)
                        
                    paidoutat = (payment.get('paid_out_at'))
                    if paidoutat is not None:
                        paidoutat = convert_unix_ts_to_utc(paidoutat)
                        
                    depositedat = (payment.get('deposited_at'))
                    if depositedat is not None:
                        depositedat = convert_unix_ts_to_utc(depositedat)
                        
                    displaydate = (payment.get('display_date'))
                    if displaydate is not None:
                        displaydate = convert_unix_ts_to_utc(displaydate)
                        
                url = protocustomer['1'].get('5')
                if url is not None:
                    url = url.decode()
                    
                name = (protocustomer['1'].get('3'))
                if name is not None:
                    name = name.decode()
                    
                username = (protocustomer['1'].get('8'))
                if username is not None:
                    username = username.decode()
                    
                extrainfo = (protocustomer['1'].get('15'))
                if extrainfo is not None:
                    extrainfo = extrainfo.decode()
                    extrainfo = json.loads(extrainfo)
                    
                    id = (extrainfo['id'])
                    fullname = (extrainfo['full_name'])
                    region = (extrainfo.get('region'))
                    dunits = (extrainfo.get('display_units'))
                    
                data_list.append((timestamp,createdat,capturedat,reachedcustomerat,paidoutat,depositedat,displaydate,customertoken,name,username,id,fullname,role,howmuch,currency,note,region,dunits,url,cardbrand,suffix,displayname,displayinstrument,instrumenttype,transactionid,state, file_found))
        
    data_headers = (('Timestamp', 'datetime'), ('Created At', 'datetime'),('Captured At', 'datetime'),
                    ('Reached Customer At', 'datetime'),('Paid Out At', 'datetime'),('Deposited At', 'datetime'),('Display Date', 'datetime'), 
                    'Customer Token','Name','Username','ID','Full Name','Role','Amount',
                    'Currency','Note','Region','Units','URL','Card Brand','Suffix','Display Name','Display Instrument',
                    'Instrument Type','Transaction ID','State', 'Source File')
    return data_headers,data_list, ''
    
    