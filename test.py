import os 
import subprocess as sp
import json

# temp = os.system("aws configure list-profiles")
temp = sp.check_output("aws configure list-profiles", shell=True)
temp = temp.decode("utf-8")
print(type(temp))
temp = list(temp.split())
print(temp)
print(type(temp))