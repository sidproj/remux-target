import os
import subprocess

pwd = subprocess.check_output("pwd",shell=True,text=True)
os.chdir("../../..")

pwd = subprocess.check_output("pwd",shell=True,text=True)
print(pwd)
pwd = pwd[:-1]
data = os.scandir(pwd)

for item in data:
    print(item.inode(),item.is_dir(),item.is_file(),item.stat())