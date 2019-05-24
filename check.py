import json
import argparse
import os
import itertools
import re


parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str, help='File name')
args = parser.parse_args()


file_path = args.f
with open(file_path, 'r', encoding='utf-8') as f:
    term = json.load(f)

min_freq = 5
remove_list = []
for key, value in term.items():
    if value <= min_freq:
        remove_list.append(key)

for key in remove_list:
    term.pop(key)

print(f'Min_freq = {min_freq}, term remove = {len(remove_list)}, term = {len(term)}')

term_xy = dict()
term_oov = dict()


def Chinese_filter(sentenses):
    """ 
    @comment: 之前用for循环写的... 我觉得正则快一些。
    @input: list(or set) of sentenses,
    @output: keep sentenses whose charaters are all Chinese (len>=2)
    """
    p = re.compile(r'^[\u4E00-\u9FA5]+$')
    include = []
    for sentense in sentenses:
        sentense = sentense.strip()
        if (len(sentense)>=2 and (re.match(p,sentense) is not None)):
            include.append(sentense)
    return(include)


full_dict = set()
xiangya_dir = './dictionary/XiangYaDict.txt'
with open(xiangya_dir, 'r', encoding="utf-8") as xy:
    terms = xy.readlines()
    terms = [t.split(",") for t in terms]
    terms = list(itertools.chain.from_iterable(terms))
    terms = [re.sub(r"\(.*\)|\[.*\]","",t.strip()) for t in terms]
    terms = Chinese_filter(terms)
full_dict.update(terms)


for key, value in term.items():
    if key in full_dict:
        term_xy[key] = value
    else:
        term_oov[key] = value

print(f'Term in xy: {len(term_xy)}, term oov: {len(term_oov)}')

with open(file_path + "_oov", 'w', encoding='utf-8') as f:
    json.dump(term_oov, f)

print(term_oov)

