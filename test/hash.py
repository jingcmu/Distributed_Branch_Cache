'''
Created on Apr 10, 2014

@author: Jacky
'''
import hashlib
from sys import argv

def md5_for_file(pathfilename, block_size=2**20):
    """ to get md5 hash for a file """
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
    pathfilename = argv[1]
    print md5_for_file(pathfilename)

test_md5()