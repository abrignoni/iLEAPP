"""
Copyright (c) 2012-2016, CCL Forensics
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the CCL Forensics nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL CCL FORENSICS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import os
import struct
import datetime

__version__ = "0.21"
__description__ = "Converts Apple binary PList files into a native Python data structure"
__contact__ = "Alex Caithness"

_object_converter = None
def set_object_converter(function):
    """Sets the object converter function to be used when retrieving objects from the bplist.
    default is None (which will return objects in their raw form).
    A built in converter (ccl_bplist.NSKeyedArchiver_common_objects_convertor) which is geared
    toward dealling with common types in NSKeyedArchiver is available which can simplify code greatly
    when dealling with these types of files."""
    if not hasattr(function, "__call__"):
        raise TypeError("function is not a function")
    global _object_converter
    _object_converter = function

class BplistError(Exception):
    pass

class BplistUID:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "UID: {0}".format(self.value)

    def __str__(self):
        return self.__repr__()

def __decode_multibyte_int(b, signed=True):
    if len(b) == 1:
        fmt = ">B" # Always unsigned?
    elif len(b) == 2:
        fmt = ">h"
    elif len(b) == 3:
        if signed:
            return ((b[0] << 16) | struct.unpack(">H", b[1:])[0]) - ((b[0] >> 7) * 2 * 0x800000)
        else:
            return (b[0] << 16) | struct.unpack(">H", b[1:])[0]
    elif len(b) == 4:
        fmt = ">i"
    elif len(b) == 8:
        fmt = ">q"
    elif len(b) == 16:
        # special case for BigIntegers
        high, low = struct.unpack(">QQ", b)
        result = (high << 64) | low
        if high & 0x8000000000000000 and signed:
            result -= 0x100000000000000000000000000000000
        return result
    else:
        raise BplistError("Cannot decode multibyte int of length {0}".format(len(b)))
    
    if signed and len(b) > 1:
        return struct.unpack(fmt.lower(), b)[0]
    else:
        return struct.unpack(fmt.upper(), b)[0]

def __decode_float(b, signed=True):
    if len(b) == 4:
        fmt = ">f"
    elif len(b) == 8:
        fmt = ">d"
    else:
        raise BplistError("Cannot decode float of length {0}".format(len(b)))

    if signed: 
        return struct.unpack(fmt.lower(), b)[0]
    else:
        return struct.unpack(fmt.upper(), b)[0]

def __decode_object(f, offset, collection_offset_size, offset_table):
    # Move to offset and read type
    #print("Decoding object at offset {0}".format(offset))
    f.seek(offset)
    # A little hack to keep the script portable between py2.x and py3k
    if sys.version_info[0] < 3:
        type_byte = ord(f.read(1)[0])
    else:
        type_byte = f.read(1)[0]
    #print("Type byte: {0}".format(hex(type_byte)))
    if type_byte == 0x00: # Null      0000 0000
        return None
    elif type_byte == 0x08: # False   0000 1000
        return False
    elif type_byte == 0x09: # True    0000 1001
        return True
    elif type_byte == 0x0F: # Fill    0000 1111
        raise BplistError("Fill type not currently supported at offset {0}".format(f.tell())) # Not sure what to return really...
    elif type_byte & 0xF0 == 0x10: # Int    0001 xxxx
        int_length = 2 ** (type_byte & 0x0F)
        int_bytes = f.read(int_length)
        return __decode_multibyte_int(int_bytes)
    elif type_byte & 0xF0 == 0x20: # Float   0010 nnnn
        float_length = 2 ** (type_byte & 0x0F)
        float_bytes = f.read(float_length)
        return __decode_float(float_bytes)
    elif type_byte & 0xFF == 0x33: # Date   0011 0011
        date_bytes = f.read(8)
        date_value = __decode_float(date_bytes)
        try:
            result = datetime.datetime(2001,1,1) + datetime.timedelta(seconds = date_value)
        except OverflowError:
            result = datetime.datetime.min
        return result
    elif type_byte & 0xF0 == 0x40: # Data   0100 nnnn
        if type_byte & 0x0F != 0x0F:
            # length in 4 lsb
            data_length = type_byte & 0x0F
        else:
            # A little hack to keep the script portable between py2.x and py3k
            if sys.version_info[0] < 3:
                int_type_byte = ord(f.read(1)[0])
            else:
                int_type_byte = f.read(1)[0]
            if int_type_byte & 0xF0 != 0x10:
                raise BplistError("Long Data field definition not followed by int type at offset {0}".format(f.tell()))
            int_length = 2 ** (int_type_byte & 0x0F)
            int_bytes = f.read(int_length)
            data_length = __decode_multibyte_int(int_bytes, False)
        return f.read(data_length)
    elif type_byte & 0xF0 == 0x50: # ASCII  0101 nnnn
        if type_byte & 0x0F != 0x0F:
            # length in 4 lsb
            ascii_length = type_byte & 0x0F
        else:
            # A little hack to keep the script portable between py2.x and py3k
            if sys.version_info[0] < 3:
                int_type_byte = ord(f.read(1)[0])
            else:
                int_type_byte = f.read(1)[0]
            if int_type_byte & 0xF0 != 0x10:
                raise BplistError("Long ASCII field definition not followed by int type at offset {0}".format(f.tell()))
            int_length = 2 ** (int_type_byte & 0x0F)
            int_bytes = f.read(int_length)
            ascii_length = __decode_multibyte_int(int_bytes, False)
        return f.read(ascii_length).decode("ascii")
    elif type_byte & 0xF0 == 0x60: # UTF-16  0110 nnnn
        if type_byte & 0x0F != 0x0F:
            # length in 4 lsb
            utf16_length = (type_byte & 0x0F) * 2 # Length is characters - 16bit width
        else:
            # A little hack to keep the script portable between py2.x and py3k
            if sys.version_info[0] < 3:
                int_type_byte = ord(f.read(1)[0])
            else:
                int_type_byte = f.read(1)[0]
            if int_type_byte & 0xF0 != 0x10:
                raise BplistError("Long UTF-16 field definition not followed by int type at offset {0}".format(f.tell()))
            int_length = 2 ** (int_type_byte & 0x0F)
            int_bytes = f.read(int_length)
            utf16_length = __decode_multibyte_int(int_bytes, False) * 2
        return f.read(utf16_length).decode("utf_16_be")
    elif type_byte & 0xF0 == 0x80: # UID    1000 nnnn
        uid_length = (type_byte & 0x0F) + 1
        uid_bytes = f.read(uid_length)
        return BplistUID(__decode_multibyte_int(uid_bytes, signed=False))
    elif type_byte & 0xF0 == 0xA0: # Array  1010 nnnn
        if type_byte & 0x0F != 0x0F:
            # length in 4 lsb
            array_count = type_byte & 0x0F
        else:
            # A little hack to keep the script portable between py2.x and py3k
            if sys.version_info[0] < 3:
                int_type_byte = ord(f.read(1)[0])
            else:
                int_type_byte = f.read(1)[0]
            if int_type_byte & 0xF0 != 0x10:
                raise BplistError("Long Array field definition not followed by int type at offset {0}".format(f.tell()))
            int_length = 2 ** (int_type_byte & 0x0F)
            int_bytes = f.read(int_length)
            array_count = __decode_multibyte_int(int_bytes, signed=False)
        array_refs = []
        for i in range(array_count):
            array_refs.append(__decode_multibyte_int(f.read(collection_offset_size), False))
        return [__decode_object(f, offset_table[obj_ref], collection_offset_size, offset_table) for obj_ref in array_refs]
    elif type_byte & 0xF0 == 0xC0: # Set  1010 nnnn
        if type_byte & 0x0F != 0x0F:
            # length in 4 lsb
            set_count = type_byte & 0x0F
        else:
            # A little hack to keep the script portable between py2.x and py3k
            if sys.version_info[0] < 3:
                int_type_byte = ord(f.read(1)[0])
            else:
                int_type_byte = f.read(1)[0]
            if int_type_byte & 0xF0 != 0x10:
                raise BplistError("Long Set field definition not followed by int type at offset {0}".format(f.tell()))
            int_length = 2 ** (int_type_byte & 0x0F)
            int_bytes = f.read(int_length)
            set_count = __decode_multibyte_int(int_bytes, signed=False)
        set_refs = []
        for i in range(set_count):
            set_refs.append(__decode_multibyte_int(f.read(collection_offset_size), False))
        return [__decode_object(f, offset_table[obj_ref], collection_offset_size, offset_table) for obj_ref in set_refs]
    elif type_byte & 0xF0 == 0xD0: # Dict  1011 nnnn
        if type_byte & 0x0F != 0x0F:
            # length in 4 lsb
            dict_count = type_byte & 0x0F
        else:
            # A little hack to keep the script portable between py2.x and py3k
            if sys.version_info[0] < 3:
                int_type_byte = ord(f.read(1)[0])
            else:
                int_type_byte = f.read(1)[0]
            #print("Dictionary length int byte: {0}".format(hex(int_type_byte)))
            if int_type_byte & 0xF0 != 0x10:
                raise BplistError("Long Dict field definition not followed by int type at offset {0}".format(f.tell()))
            int_length = 2 ** (int_type_byte & 0x0F)
            int_bytes = f.read(int_length)
            dict_count = __decode_multibyte_int(int_bytes, signed=False)
        key_refs = []
        #print("Dictionary count: {0}".format(dict_count))
        for i in range(dict_count):
            key_refs.append(__decode_multibyte_int(f.read(collection_offset_size), False))
        value_refs = []
        for i in range(dict_count):
            value_refs.append(__decode_multibyte_int(f.read(collection_offset_size), False))
        
        dict_result = {}
        for i in range(dict_count):
            #print("Key ref: {0}\tVal ref: {1}".format(key_refs[i], value_refs[i]))
            key = __decode_object(f, offset_table[key_refs[i]], collection_offset_size, offset_table)
            val = __decode_object(f, offset_table[value_refs[i]], collection_offset_size, offset_table)
            dict_result[key] = val
        return dict_result


def load(f):
    """
    Reads and converts a file-like object containing a binary property list.
    Takes a file-like object (must support reading and seeking) as an argument
    Returns a data structure representing the data in the property list
    """
    # Check magic number
    if f.read(8) != b"bplist00":
        raise BplistError("Bad file header")

    # Read trailer
    f.seek(-32, os.SEEK_END)
    trailer = f.read(32)
    offset_int_size, collection_offset_size, object_count, top_level_object_index, offest_table_offset = struct.unpack(">6xbbQQQ", trailer)

    # Read offset table
    f.seek(offest_table_offset)
    offset_table = []
    for i in range(object_count):
        offset_table.append(__decode_multibyte_int(f.read(offset_int_size), False))
    
    return __decode_object(f, offset_table[top_level_object_index], collection_offset_size, offset_table)


def NSKeyedArchiver_common_objects_convertor(o):
    """Built in converter function (suitable for submission to set_object_converter()) which automatically
    converts the following common data-types found in NSKeyedArchiver:
    NSDictionary/NSMutableDictionary;
    NSArray/NSMutableArray;
    NSSet/NSMutableSet
    NSString/NSMutableString
    NSDate
    $null strings"""
    # Conversion: NSDictionary
    if is_nsmutabledictionary(o):
        return convert_NSMutableDictionary(o)
    # Conversion: NSArray
    elif is_nsarray(o):
        return convert_NSArray(o)
    elif is_isnsset(o):
        return convert_NSSet(o)
    # Conversion: NSString
    elif is_nsstring(o):
        return convert_NSString(o)
    # Conversion: NSDate
    elif is_nsdate(o):
        return convert_NSDate(o)
    # Conversion: "$null" string
    elif isinstance(o, str) and o == "$null":
        return None
    # Fallback:
    else:
        return o

def NSKeyedArchiver_convert(o, object_table):
    if isinstance(o, list):
        #return NsKeyedArchiverList(o, object_table)
        result = NsKeyedArchiverList(o, object_table)
    elif isinstance(o, dict):
        #return NsKeyedArchiverDictionary(o, object_table)
        result = NsKeyedArchiverDictionary(o, object_table)
    elif isinstance(o, BplistUID):
        #return NSKeyedArchiver_convert(object_table[o.value], object_table)
        result = NSKeyedArchiver_convert(object_table[o.value], object_table)
    else:
        #return o
        result = o

    if _object_converter:
        return _object_converter(result)
    else:
        return result


class NsKeyedArchiverDictionary(dict):
    def __init__(self, original_dict, object_table):
        super(NsKeyedArchiverDictionary, self).__init__(original_dict)
        self.object_table = object_table

    def __getitem__(self, index):
        o = super(NsKeyedArchiverDictionary, self).__getitem__(index)
        return NSKeyedArchiver_convert(o, self.object_table)

    def get(self, key, default=None):
        return self[key] if key in self else default

    def values(self):
        for k in self:
            yield self[k]

    def items(self):
        for k in self:
            yield k, self[k]

class NsKeyedArchiverList(list):
    def __init__(self, original_iterable, object_table):
        super(NsKeyedArchiverList, self).__init__(original_iterable)
        self.object_table = object_table

    def __getitem__(self, index):
        o = super(NsKeyedArchiverList, self).__getitem__(index)
        return NSKeyedArchiver_convert(o, self.object_table)

    def __iter__(self):
        for o in super(NsKeyedArchiverList, self).__iter__():
            yield NSKeyedArchiver_convert(o, self.object_table)
        

def deserialise_NsKeyedArchiver(obj, parse_whole_structure=False):
    """Deserialises an NSKeyedArchiver bplist rebuilding the structure.
       obj should usually be the top-level object returned by the load()
       function."""
    
    # Check that this is an archiver and version we understand
    if not isinstance(obj, dict):
        raise TypeError("obj must be a dict")
    if "$archiver" not in obj or obj["$archiver"] not in ("NSKeyedArchiver", "NRKeyedArchiver"):
        raise ValueError("obj does not contain an '$archiver' key or the '$archiver' is unrecognised")
    if "$version" not in obj or obj["$version"] != 100000:
        raise ValueError("obj does not contain a '$version' key or the '$version' is unrecognised")

    object_table = obj["$objects"]
    if "root" in obj["$top"] and not parse_whole_structure:
        return NSKeyedArchiver_convert(obj["$top"]["root"], object_table)
    else:
        return NSKeyedArchiver_convert(obj["$top"], object_table)
    
# NSMutableDictionary convenience functions
def is_nsmutabledictionary(obj):
    if not isinstance(obj, dict):
        return False
    if "$class" not in obj.keys():
        return False
    if obj["$class"].get("$classname") not in ("NSMutableDictionary", "NSDictionary"):
        return False
    if "NS.keys" not in obj.keys():
        return False
    if "NS.objects" not in obj.keys():
        return False

    return True
    
def convert_NSMutableDictionary(obj):
    """Converts a NSKeyedArchiver serialised NSMutableDictionary into
       a straight dictionary (rather than two lists as it is serialised
       as)"""
    
    # The dictionary is serialised as two lists (one for keys and one
    # for values) which obviously removes all convenience afforded by
    # dictionaries. This function converts this structure to an 
    # actual dictionary so that values can be accessed by key.
    
    if not is_nsmutabledictionary(obj):
        raise ValueError("obj does not have the correct structure for a NSDictionary/NSMutableDictionary serialised to a NSKeyedArchiver")
    keys = obj["NS.keys"]
    vals = obj["NS.objects"]

    # sense check the keys and values:
    if not isinstance(keys, list):
        raise TypeError("The 'NS.keys' value is an unexpected type (expected list; actual: {0}".format(type(keys)))
    if not isinstance(vals, list):
        raise TypeError("The 'NS.objects' value is an unexpected type (expected list; actual: {0}".format(type(vals)))
    if len(keys) != len(vals):
        raise ValueError("The length of the 'NS.keys' list ({0}) is not equal to that of the 'NS.objects ({1})".format(len(keys), len(vals)))

    result = {}
    for i,k in enumerate(keys):
        if k in result:
            raise ValueError("The 'NS.keys' list contains duplicate entries")
        result[k] = vals[i]
    
    return result

# NSArray convenience functions
def is_nsarray(obj):
    if not isinstance(obj, dict):
        return False
    if "$class" not in obj.keys():
        return False
    if obj["$class"].get("$classname") not in ("NSArray", "NSMutableArray"):
        return False
    if "NS.objects" not in obj.keys():
        return False

    return True

def convert_NSArray(obj):
    if not is_nsarray(obj):
        raise ValueError("obj does not have the correct structure for a NSArray/NSMutableArray serialised to a NSKeyedArchiver")

    return obj["NS.objects"]

# NSSet convenience functions
def is_isnsset(obj):
    if not isinstance(obj, dict):
        return False
    if "$class" not in obj.keys():
        return False
    if obj["$class"].get("$classname") not in ("NSSet", "NSMutableSet"):
        return False
    if "NS.objects" not in obj.keys():
        return False

    return True

def convert_NSSet(obj):
    if not is_isnsset(obj):
        raise ValueError("obj does not have the correct structure for a NSSet/NSMutableSet serialised to a NSKeyedArchiver")

    return list(obj["NS.objects"])

# NSString convenience functions
def is_nsstring(obj):
    if not isinstance(obj, dict):
        return False
    if "$class" not in obj.keys():
        return False
    if obj["$class"].get("$classname") not in ("NSString", "NSMutableString"):
        return False
    if "NS.string" not in obj.keys():
        return False
    return True

def convert_NSString(obj):
    if not is_nsstring(obj):
        raise ValueError("obj does not have the correct structure for a NSString/NSMutableString serialised to a NSKeyedArchiver")

    return obj["NS.string"]

# NSDate convenience functions
def is_nsdate(obj):
    if not isinstance(obj, dict):
        return False
    if "$class" not in obj.keys():
        return False
    if obj["$class"].get("$classname") not in ("NSDate"):
        return False
    if "NS.time" not in obj.keys():
        return False

    return True

def convert_NSDate(obj):
    if not is_nsdate(obj):
        raise ValueError("obj does not have the correct structure for a NSDate serialised to a NSKeyedArchiver")

    return datetime.datetime(2001, 1, 1) + datetime.timedelta(seconds=obj["NS.time"])
