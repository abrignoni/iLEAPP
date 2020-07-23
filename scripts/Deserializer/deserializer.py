#
# Plist Deserializer, from NSKeyedArchive to normal plist 
# Copyright (c) 2018  Yogesh Khatri <yogesh@swiftforensics.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You can get a copy of the complete license here:
#  <http://www.gnu.org/licenses/>.
#
# Script Name  : DeSerializer.py
# Author       : Yogesh Khatri
# Last Updated : June 16 2020
# Purpose      : NSKeyedArchive plists (such as .SFL2 files) are stored as 
#                serialized data, which is machine readable but not human
#                readable. This script will convert NSKeyedArchive binary 
#                plists into normal plists.
# Usage        : deserializer.py input_plist_path
#                Output will be saved in same location with _deserialised.plist 
#                appended to filename.
# Requirements : 
#                Python3.x
#                biplist (Get it with pip3 install biplist)
#                ccl_bplist (Use the one supplied with this script, as it has 
#                            been updated to fix few issues)
#
# Note: This will not work with python 2.xx

import biplist
import scripts.Deserializer.ccl_bplist as ccl_bplist
import datetime
import io
import json
import os
import plistlib
import sys
import traceback

deserializer_version = '1.2'

rec_depth = 0
rec_uids = []

def RecurseSafely(uid, plist, root, object_table):
    '''Returns False if infinite recursion was detected'''
    global rec_uids
    if uid in rec_uids:
        #print(f'Possible INFINITE RECURSION detected - breaking loop! uid={uid} , LIST={str(rec_uids)}')
        #if isinstance(plist, list):
        #    plist.append('ERROR - Infinite Recursion')
        return False
    rec_uids.append(uid)
    recurseCreatePlist(plist, root, object_table)
    rec_uids.pop()
    return True

def recurseCreatePlist(plist, root, object_table):
    global rec_depth
    rec_depth += 1
    
    if rec_depth > 50:
        print('Possible infinite recursion detected!!')
    if isinstance(root, dict):
        for key, value in root.items():
            if key == '$class': 
                continue
            add_this_item = True
            v = None
            if isinstance(value, ccl_bplist.BplistUID):
                v2 = ccl_bplist.NSKeyedArchiver_convert(object_table[value.value], object_table)
                if isinstance(v2, dict):
                    v = {}
                    add_this_item = RecurseSafely(value.value, v, v2, object_table) # recurseCreatePlist(v, v2, object_table)
                elif isinstance(v2, list):
                    v = []
                    add_this_item = RecurseSafely(value.value, v, v2, object_table) # recurseCreatePlist(v, v2, object_table)
                else:
                    v = v2
            elif isinstance(value, list):
                v = []
                recurseCreatePlist(v, value, object_table)
            elif isinstance(value, dict):
                v = {}
                recurseCreatePlist(v, value, object_table)
            else:
                v = value
            # change None to empty string. This is because if an object value is $null, it
            # is most likely going to be a string. This has to be done, else writing a plist back will fail.
            if v == None:
                v = ''
                #if key != 'NS.base': # NS.base is usually UID:0, which is usually None
                #    print('Changing NULL to empty string for key={}'.format(key))
            # Keys must be string, else plist writing will fail!
            if not isinstance(key, str):
                key = str(key)
                #print(f'Converting non-string key {key} to string')
            if add_this_item:
                plist[key] = v
    else: # must be list
        for value in root:
            v = None
            add_this_item = True
            if isinstance(value, ccl_bplist.BplistUID):
                v2 = ccl_bplist.NSKeyedArchiver_convert(object_table[value.value], object_table)
                if isinstance(v2, dict):
                    v = {}
                    add_this_item = RecurseSafely(value.value, v, v2, object_table) # recurseCreatePlist(v, v2, object_table)
                elif isinstance(v2, list):
                    v = []
                    add_this_item = RecurseSafely(value.value, v, v2, object_table) # recurseCreatePlist(v, v2, object_table)
                else:
                    v = v2
            elif isinstance(value, list):
                v = []
                recurseCreatePlist(v, value, object_table)
            elif isinstance(value, dict):
                v = {}
                recurseCreatePlist(v, value, object_table)
            else:
                v = value
            # change None to empty string. This is because if an object value is $null, it
            # is most likely going to be a string. This has to be done, else writing a plist back will fail.
            if v == None:
                v = ''
                #if key != 'NS.base': # NS.base is usually UID:0, which is usually None
                #    print('Changing NULL to empty string for key={}'.format(key))
            if add_this_item:
                plist.append(v)
    rec_depth -= 1
    
def ConvertCFUID_to_UID(plist):
    ''' For converting XML plists to binary, UIDs which are represented
        as strings 'CF$UID' must be translated to actual UIDs.
    '''
    if isinstance(plist, dict):
        for k, v in plist.items():
            if isinstance(v, dict):
                num = v.get('CF$UID', None)
                if (num is None) or (not isinstance(num, int)):
                    ConvertCFUID_to_UID(v)
                else:
                    plist[k] = biplist.Uid(num)
            elif isinstance(v, list):
                ConvertCFUID_to_UID(v)
    else: # list
        for index, v in enumerate(plist):
            if isinstance(v, dict):
                num = v.get('CF$UID', None)
                if (num is None) or (not isinstance(num, int)):
                    ConvertCFUID_to_UID(v)
                else:
                    plist[index] = biplist.Uid(num)
            elif isinstance(v, list):
                ConvertCFUID_to_UID(v)

def getRootElementNames(f):
    ''' The top element is usually called "root", but sometimes it is not!
        Hence we retrieve the correct name here. In some plists, there is
        more than one top element, this function will retrieve them all.
    '''
    roots = []
    try:
        plist = biplist.readPlist(f)
        top_element = plist.get('$top', None)
        if top_element:
            roots = [ x for x in top_element.keys() ]
        else:
            print('$top element not found! Not an NSKeyedArchive?')
    except biplist.InvalidPlistException:
        print('Had an exception (error) trying to read plist using biplist')
        traceback.print_exc()
    return roots

def extract_nsa_plist(f):
    '''Return the embedded plist, if this is such a file.
       Sometimes there is a single data blob which then has 
       the NSKeyedArchiver plist in it.
    '''
    try:
        plist = biplist.readPlist(f)
        if isinstance(plist, bytes):
            data = plist
            f.close()
            f = io.BytesIO(data)
    except biplist.InvalidPlistException:
        print('Had an exception (error) trying to read plist using biplist')
        return None
    f.seek(0)

    # Check if file to be returned is an XML plist
    header = f.read(8)
    f.seek(0)
    if header[0:6] != b'bplist': # must be xml
        # Convert xml to binary (else ccl_bplist wont load!)
        try:
            tempfile = io.BytesIO()
            plist = biplist.readPlist(f)
            ConvertCFUID_to_UID(plist)
            biplist.writePlist(plist, tempfile)
            f.close()
            tempfile.seek(0)
            return tempfile
        except biplist.InvalidPlistException:
            print('Had exception (error) trying to read plist using biplist')
            return None
    return f

def process_nsa_plist(input_path, f):
    '''Returns a deserialized plist. Input is NSKeyedArchive'''
    global use_as_library
    try:
        if not use_as_library:
            print('Reading file .. ' + input_path)
        f = extract_nsa_plist(f)
        ccl_bplist.set_object_converter(ccl_bplist.NSKeyedArchiver_common_objects_convertor)
        plist = ccl_bplist.load(f)
        ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=True)

        root_names = getRootElementNames(f)
        top_level = []

        for root_name in root_names:
            root = ns_keyed_archiver_obj[root_name]
            if not use_as_library:
                print('Trying to deserialize binary plist $top = {}'.format(root_name))
            if isinstance(root, dict):
                plist = {}
                recurseCreatePlist(plist, root, ns_keyed_archiver_obj.object_table)
                if root_name.lower() != 'root':
                    plist = { root_name : plist }
            elif isinstance(root, list):
                plist = []
                recurseCreatePlist(plist, root, ns_keyed_archiver_obj.object_table)
                if root_name.lower() != 'root':
                    plist = { root_name : plist }
            else:
                plist = { root_name : root }
            
            if len(root_names) == 1:
                top_level = plist
            else: # > 1
                top_level.append(plist)

    except Exception as ex:
        print('Had an exception (error)')
        traceback.print_exc()

    return top_level

def get_json_writeable_plist(in_plist, out_plist):
    if isinstance(in_plist, list):
        for item in in_plist:
            if isinstance(item, list):
                i = []
                out_plist.append(i)
                get_json_writeable_plist(item, i)
            elif isinstance(item, dict):
                i = {}
                out_plist.append(i)
                get_json_writeable_plist(item, i)
            elif isinstance(item, bytes):
                out_plist.append(item.hex())
            else:
                out_plist.append(str(item))
    else: #dict
        for k, v in in_plist.items():
            if isinstance(v, list):
                i = []
                out_plist[k] = i
                get_json_writeable_plist(v, i)
            elif isinstance(v, dict):
                i = {}
                out_plist[k] = i
                get_json_writeable_plist(v, i)
            elif isinstance(v, bytes):
                out_plist[k] = v.hex()
            else:
                out_plist[k] = str(v)

def write_plist_to_json_file(deserialised_plist, output_path):
    try:
        print('Writing out .. ' + output_path)
        out_file = open(output_path, 'w')
        try:
            json_plist = {} if isinstance(deserialised_plist, dict) else []
            get_json_writeable_plist(deserialised_plist, json_plist)
            json.dump(json_plist, out_file)
            out_file.close()
            return True
        except (TypeError, ValueError) as ex:
            print('json error - ' + str(ex))
    except OSError as ex:
        print('Error opening file for writing: Error={} Path={}'.format(output_path, str(ex)))
    return False

def write_plist_to_file(deserialised_plist, output_path):
    #Using plistLib to write plist
    out_file = None
    try:
        print('Writing out .. ' + output_path)
        out_file = open(output_path, 'wb')
        try:
            plistlib.dump(deserialised_plist, out_file, fmt=plistlib.FMT_BINARY)
            out_file.close()
            return True
        except (TypeError, OverflowError, OSError) as ex:
            out_file.close()
            print('Had an exception (error)')
            traceback.print_exc()
    except OSError as ex:
        print('Error opening file for writing: Error={} Path={}'.format(output_path, str(ex)))
    # Try using biplist
    try:
        print('Writing out (using biplist) .. ' + output_path)
        biplist.writePlist(deserialised_plist, output_path)
        return True
    except (biplist.InvalidPlistException, biplist.NotBinaryPlistException, OSError) as ex:
        print('Had an exception (error)')
        traceback.print_exc()

usage = '\r\nDeserializer version {0}  (c) Yogesh Khatri 2018-2020 \r\n'\
        'This script converts an NSKeyedArchive plist into a normal deserialized one.\r\n\r\n'\
        '  Usage  : {1} [-j] input_plist_path \r\n'\
        '  Example: {1} C:\\test\\com.apple.preview.sfl2 \r\n'\
        '           {1} -j  C:\\test\\screentime.plist \r\n\r\n'\
        'The -j option will create a json file as output. \r\n'\
        'If successful, the resulting plist or json file will be created in the same folder \r\n'\
        'and will have _deserialized appended to its name.\r\n'

use_as_library = True

def main():
    global usage
    global use_as_library
    global deserializer_version
    use_as_library = False
    json_output = False

    if sys.argv[0].lower().endswith('.exe'):
        deserializer_launcher = 'deserializer.exe'
    else:
        deserializer_launcher = 'python deserializer.py'

    usage = usage.format(deserializer_version, deserializer_launcher)
    argc = len(sys.argv)
    if argc < 2 or sys.argv[1].lower() == '-h':
        print(usage)
        return
    elif argc >= 3: # check for -j option
        if sys.argv[1].lower() == '-j':
            json_output = True
        else:
            print(f'Invalid option "{sys.argv[1]}" The only valid option is "-j"')
            print(usage)
        input_path = sys.argv[2]
    else:
        input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f'Error, input file "{input_path}" does not exist! Check file path!\r\n')
        print(usage)
        return

    # All OK, process the file now
    try:
        f = open(input_path, 'rb')
        if f:
            deserialised_plist = process_nsa_plist(input_path, f)
            f.close()
            output_path_plist = input_path + '_deserialized.plist'
            output_path_json  = input_path + '_deserialized.json'
            if json_output:
                output_success = write_plist_to_json_file(deserialised_plist, output_path_json)
            else:
                output_success = write_plist_to_file(deserialised_plist, output_path_plist)
            if output_success:
                print('Done !')
            else:
                print('Conversion Failed ! Please send the offending plist my way to\n yogesh@swiftforensics.com')
        else:
            print('Had an error :(  No output!! Please send the offending plist my way to\n yogesh@swiftforensics.com')
    except Exception as ex:
        print('Had an exception (error)')
        traceback.print_exc()
    
if __name__ == "__main__":
    main()     
