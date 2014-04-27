'''
Created on Apr 10, 2014

@author: Jacky
'''
import hashlib
from sys import argv

def md5_for_file(pathfilename, block_size=2**20):
    """ to get md5 hash for a file, return a string of md5 """
    md5 = hashlib.md5()
    with open(pathfilename, "rb") as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


#test
def test_md5():
    pathfilename1 = argv[1]
    hash = md5_for_file(pathfilename1)
    #hash2 = md5_for_file(pathfilename2)
    print hash

test_md5()
