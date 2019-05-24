import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str, help='File name')
# parser.add_argument('-o', type=str2bool, default=False, help='Output to file')
args = parser.parse_args()

file_path = args.f
with open(file_path, 'r') as f:
    lines = f.readlines()

wrong_count = 0
line_count = 0
for line in lines:
    if line.strip() != "":
        line_count += 1
        context = line.split()
        if context[1] != context[2]:
            wrong_count += 1

print(f'Line count: {line_count}, wrong count: {wrong_count}')


def change(st):
    # Change a str b'\x12\x..' to a Chinese character
    tmp = st[3:-1]
    tmp_hex = ""
    for i in range(len(tmp)):
        if tmp[i] != "\\" and tmp[i] != "x":
            tmp_hex += tmp[i]
    return bytes.fromhex(tmp_hex).decode()


now_term = ""
term = dict()
for line in lines:
    if line.strip() != "":
        char = change(line.split()[0])
        predict_label = line.split()[2]
        if predict_label == "B":
            now_term = char
        if predict_label == "M" and now_term != "":
            now_term += char
        if predict_label == "E" and now_term != "":
            now_term += char
            if now_term in term:
                term[now_term] += 1
            else:
                term[now_term] = 1
        if predict_label == "O":
            now_term == ""
    
print(f'Term count: {len(term)}')


if not os.path.exists("./term/"):
    os.system("mkdir ./term/")

import json
with open(os.path.join('./term/', os.path.basename(file_path)), 'w', encoding='utf-8') as f:
    json.dump(term, f)

