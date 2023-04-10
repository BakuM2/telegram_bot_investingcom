# https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt
# taking only positive signed ("+") proxies and save them in to proxies_approved.txt

import re
import os

CWD=os.getcwd()
CWD=CWD.replace(os.sep, '/')

pluses = ['+']
pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

least=[]
lst = []

with open(CWD+'/proxies.txt') as oldfile, \
        open(CWD+'/proxies_approved.txt', 'w') as proxies_approved:
    for line in oldfile:
        if any(sign in line for sign in pluses):
            least.append(line)

    for line in least:
        lst.append(pattern.search(line)[0])
    proxies_approved.write('\n'.join(lst))  # proxies_approved.write(str(lst))


