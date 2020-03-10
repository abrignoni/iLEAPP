import os
import plistlib

from common import logfunc
from contrib.utils import silence_and_log
from settings import *


def conndevices(filefound):
    with open(filefound[0], "rb") as f:
        data = f.read()

    logfunc(f"Connected devices function executing")
    outpath = os.path.join(reportfolderbase, "Devices Connected/")
    os.mkdir(outpath)
    nl = "\n"

    userComps = ""

    logfunc("Data being interpreted for FRPD is of type: " + str(type(data)))
    x = type(data)
    byteArr = bytearray(data)
    userByteArr = bytearray()

    magicOffset = byteArr.find(b"\x01\x01\x80\x00\x00")
    magic = byteArr[magicOffset : magicOffset + 5]

    flag = 0

    if magic == b"\x01\x01\x80\x00\x00":
        logfunc(
            "Found magic bytes in iTunes Prefs FRPD... Finding Usernames and Desktop names now"
        )
        f = open(outpath + "DevicesConnected.html", "w")
        f.write("<html>")
        f.write(f"Artifact name and path: {filefound[0]}<br>")
        f.write(f"Usernames and Computer names:<br><br>")
        for x in range(int(magicOffset + 92), len(data)):
            if (data[x]) == 0:
                x = int(magicOffset) + 157
                if userByteArr.decode() == "":
                    continue
                else:
                    if flag == 0:
                        userComps += userByteArr.decode() + " - "
                        flag = 1
                    else:
                        userComps += userByteArr.decode() + "\n"
                        flag = 0
                    userByteArr = bytearray()
                    continue
            else:
                char = data[x]
                userByteArr.append(char)

        logfunc(f"{userComps}{nl}")
        f.write(f"{userComps}<br>")
    f.write(f"</html>")
    f.close()
    logfunc(f"Connected devices function completed. ")
