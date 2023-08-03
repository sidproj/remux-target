import os
import subprocess
from pprint import pprint

# pwd = subprocess.check_output("pwd",shell=True,text=True)
# os.chdir("../../..")

# pwd = subprocess.check_output("pwd",shell=True,text=True)
# print(pwd)
# pwd = pwd[:-1]


# size = os.path.getsize(pwd)
# print(size)


dir1 = "/home/ubuntu/Desktop/Daiict"

os.chdir(dir1)

print(os.getcwd())

command = "cd Java"

print(command.split("cd"))

os.chdir(command.split("cd")[1].replace("'","").strip())
#
print(os.getcwd())