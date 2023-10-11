import os
import plistlib
import pgpy
import html
import json
import ccl_bplist
import sqlite3
import hashlib
import random
import magic
from base64 import b64encode, b64decode
from datetime import datetime
from io import BytesIO
from Crypto.Cipher import AES
from pathlib import Path
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, media_to_html

def get_protonMail(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []

    p = Path(__file__).parents[1]
    
    my_path = Path(p).joinpath('keychain')
  
    #platform = is_platform_windows()
    #if platform:
    #  my_path = my_path.replace('/', '\\')
    
    if len(os.listdir(my_path)) == 1:
      logfunc("No keychain provided")
      return
  
    else:
      file = os.listdir(my_path)
      for x in file:
        if x.endswith('plist'):
          keychain_plist_path = Path(my_path).joinpath(x)
    
    for file_found in files_found:
      if 'group.ch.protonmail.protonmail.plist' in file_found:
        plist_name = file_found
      if file_found.endswith('ProtonMail.sqlite'):
        db_name = file_found

    with open(keychain_plist_path,'rb') as f :
      plist = plistlib.load(f)
      
    keychainVal={}
    if type(plist) == list:
      for dd in plist:
        if type(dd) == dict:        
          if 'svce' in dd:
            if 'protonmail' in str(dd['svce']) :
              #print(dd)
              keychainVal[dd['acct']]=dd['v_Data']
    else:
      for d in plist:
        for dd in plist[d]:
          if type(dd) == dict:        
            if 'svce' in dd:
              if 'protonmail' in str(dd['svce']):
                #print(dd)
                keychainVal[dd['acct']]=dd['v_Data']
    try:
      mainKey = keychainVal[b'NoneProtection']
    except:
      logfunc("No Protonmail data in the key chain")
      return
    IVsize = 16
    
    def decryptWithMainKey(encrypted):
      iv = encrypted[:IVsize]
      cipher = AES.new(mainKey, AES.MODE_CTR, initial_value=iv, nonce=b'')
      return cipher.decrypt(encrypted[IVsize:])
    
    with open(plist_name,'rb') as p :
      prefplist = plistlib.load(p)
      
      
    enc_val = prefplist.get('authKeychainStoreKeyProtectedWithMainKey', 'empty')
    if enc_val != 'empty':
      pass
    elif keychainVal[b'authKeychainStoreKeyProtectedWithMainKey']:
      enc_val = keychainVal[b'authKeychainStoreKeyProtectedWithMainKey']
    else:
      logfunc('Decryption key not found in the keychain or the application plist.')
      return
  
    dec_val = decryptWithMainKey(enc_val)
    
    keychainStorePlist1 = ccl_bplist.load(BytesIO(dec_val))
    keychainStorePlist = ccl_bplist.load(BytesIO(keychainStorePlist1[0]))
    keychainStore = ccl_bplist.deserialise_NsKeyedArchiver(keychainStorePlist, parse_whole_structure=True)
    privateKeyCoderKey = keychainStore['root']['NS.objects'][0]['privateKeyCoderKey']
    
    key, _ = pgpy.PGPKey.from_blob(privateKeyCoderKey)
    pwdKey = keychainStore['root']['NS.objects'][0]['AuthCredential.Password']
    
    def decrypt_message(encm):
      if('-----BEGIN PGP MESSAGE-----') in encm:
        with key.unlock(pwdKey):
          assert key.is_unlocked
          message_from_blob = pgpy.PGPMessage.from_blob(encm)
          decm = key.decrypt(message_from_blob).message
          #print(decm)
          return html.unescape(decm.encode('cp1252', errors='ignore').decode('utf8', errors='ignore'))
      else:
        return encm
    
    def decrypt_attachment(proton_path, out_path, key, pwdKey, keyPacket, encfilename, decfilename):
      att = None
      for r, _, f in os.walk(proton_path):
        for file in f:
          if encfilename in file:
            att=os.path.join(r,file)
            break
      if att:
        with key.unlock(pwdKey):
          assert key.is_unlocked
          with open(att, 'rb') as attfh:
            buf = b64decode(keyPacket)
            buf += attfh.read()
            att_from_blob = pgpy.PGPMessage.from_blob(buf)
            decatt = key.decrypt(att_from_blob).message
            itemnum = str(random.random())
            with open(os.path.join(out_path,itemnum+decfilename),'wb') as outatt:
              outatt.write(decatt)
            return os.path.join(out_path,itemnum+decfilename)
      
      return None
      
    db = open_sqlite_db_readonly(db_name)
    cursor = db.cursor()
    cursor.execute('''SELECT
    ZMESSAGE.ZTIME,
    ZMESSAGE.ZBODY,
    ZMESSAGE.ZMIMETYPE,
    ZMESSAGE.ZTOLIST,
    ZMESSAGE.ZREPLYTOS,
    ZMESSAGE.ZSENDER,
    ZMESSAGE.ZTITLE,
    ZMESSAGE.ZISENCRYPTED,
    ZMESSAGE.ZNUMATTACHMENTS,
    ZATTACHMENT.ZFILESIZE,
    ZATTACHMENT.ZFILENAME,
    ZATTACHMENT.ZMIMETYPE,
    ZATTACHMENT.ZHEADERINFO,
    ZATTACHMENT.ZLOCALURL,
    ZATTACHMENT.ZKEYPACKET
    FROM ZMESSAGE
    LEFT JOIN ZATTACHMENT ON ZMESSAGE.Z_PK = ZATTACHMENT.ZMESSAGE
              ''')
    
    all_rows = cursor.fetchall()
    data_list = []	
    if len(all_rows) > 0:
      for row in all_rows:
        aggregatorto = ''
        aggregatorfor = ''
        
        time = row[0]
        decryptedtime = datetime.fromtimestamp(time+978307200)
        
        decryptedbody = decrypt_message(row[1])
        
        mime = row[2]
        
        to = json.loads(plistlib.loads(decryptWithMainKey(row[3]))[0])
        for r in to:
          address = r['Address']
          name = r['Name']
          aggregatorto = f"{address} {name}"
          
        try: 
          replyto = json.loads(plistlib.loads(decryptWithMainKey(row[4]))[0])
          for r in replyto:
            address = r['Address']
            name = r['Name']
            aggregatorfor = f"{address} {name}"
        except:
          aggregatorfor = ''
        
        try:
          sender = json.loads(plistlib.loads(decryptWithMainKey(row[5]))[0])
          name = sender['Name']
          address = sender['Address']
          sender_info = f'{address} {name}'
        except:
          sender_info = '<Not Decoded>'
        
        title = plistlib.loads(decryptWithMainKey(row[6]))[0]
        
        isencrypted = row[7]
        
        ZNUMATTACHMENTS = row[8]
        
        ZFILESIZE = row[9]
        
        try:
          ZFILENAME = plistlib.loads(decryptWithMainKey(row[10]))[0]
        except:
          ZFILENAME = ""
          
        try:
          AMIMETYPE = plistlib.loads(decryptWithMainKey(row[11]))[0]
        except:
          AMIMETYPE = ""
        
        if row[12]:
          zheaderinfo = decryptWithMainKey(row[12])
        
        attpath = ''
        if row[13]:
          encfilename = plistlib.loads(row[13])['$objects'][2].split('/')[-1]
          guidi = plistlib.loads(row[13])['$objects'][2].split('/')[-4]
          out_path = report_folder
        
          for match in files_found:
            if f'/Data/Application/{guidi}/tmp/attachments' in match:
              proton_path = match.split('/attachments')[0]
              break
            elif f'\\Data\\Application\\{guidi}\\tmp\\attachments' in match:
              proton_path = match.split('\\attachments')[0]
          
          attpath = decrypt_attachment(proton_path, out_path, key, pwdKey, row[14], encfilename, ZFILENAME)
          
          mimetype = magic.from_file(attpath, mime = True)
          
          if 'video' in mimetype:
            attpath = f'<video width="320" height="240" controls="controls"><source src="{attpath}" type="video/mp4">Your browser does not support the video tag.</video>'
          elif 'image' in mimetype:
            attpath = f'<img src="{attpath}"width="300"></img>'
          else:
            attpath = f'<a href="{attpath}"> Link to {mimetype} </>'
        
        data_list.append((decryptedtime, sender_info, aggregatorto, aggregatorfor, title, decryptedbody, mime, isencrypted, ZFILESIZE, attpath, ZFILENAME, AMIMETYPE))
        
        encfilename = ''
        
    if len(data_list) > 0:
      report = ArtifactHtmlReport('Proton Mail - Decrypted Emails')
      report.start_artifact_report(report_folder, 'Proton Mail - Decrypted Emails')
      report.add_script()
      data_headers = ('Timestamp', 'Sender', 'To', 'Reply To', 'Title', 'Body', 'Mime', 'Is encrypted?', 'File Size','Attachment','Decrypted Attachment Filename', 'Type')
      report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Sender', 'To', 'Reply To', 'Body', 'File Name', 'Type','Attachment'])
      report.end_artifact_report()

      tsvname = 'Proton Mail - Decrypted Emails'
      tsv(report_folder, data_headers, data_list, tsvname)
  
      tlactivity = 'Proton Mail - Decrypted Emails'
      timeline(report_folder, tlactivity, data_list, data_headers)

    else:
      logfunc('No Proton Mail - Decrypted Emails')

__artifacts__ = {
    "protonMail": (
        "Proton Mail",
        ('*/group.ch.protonmail.protonmail.plist','*/ProtonMail.sqlite*','*/Containers/Data/Application/*/tmp/*'),
        get_protonMail)
}