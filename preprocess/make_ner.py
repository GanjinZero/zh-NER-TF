# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 19:45:22 2018

@author: DavidYQY, GanjinZero
@use: construct true and fake terms with forward and backward characters in a full passage
@input: 
- xiangya_dir, true medical terms
- context_split_dir, a file contains the splited sentense(each row is a sentense)
"""

from construct_samples_old import Chinese_filter, Traditional2Simplified
from tqdm import tqdm
import jieba
import os
import random
import re
import itertools
import sys
import string
import time
import numpy as np
import argparse


data_path = '../dictionary/'
xiangya_dir = data_path + 'XiangYaDict.txt'
jieba_dict_path = data_path + 'jieba_dict.txt'

#context_dir = "/home/veritas/Code/GanjinZero/Data/context.txt"
#context_dir = "/media/ganjinzero/Code/medical_term_judger/data/context.txt"
#context_dir = data_path + 'context.txt'
#context_dir = 'test_passage.txt'

def judge_term_punc(term):
    
    """
    judge whether a word contains stop words
    
    @note: for now only punctuation is blocked from fake term. If you want to add more constraints, 
    you can add more elements to stop_word_set (eg, numbers, alphabets, etc)
    """
    if (len(term)<1):
        return False
    
    stop_word_set = set( \
            '＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏'+ \
            '！？｡。 ' + \
            '\t'+'\n'+'\r'+string.punctuation)
    for i in range(len(term)):
        if term[i] in stop_word_set:
            return True
    return False
        
if __name__=="__main__": 
    
    parser = argparse.ArgumentParser(description='Make Ner Train File')
    parser.add_argument('--f', type=str, help='file path')
    args = parser.parse_args()
    
    print("导入词典...")
    full_dict = set()
    with open(xiangya_dir, 'r', encoding="utf-8") as xy:
        terms = xy.readlines()
        terms = [t.split(",") for t in terms]
        terms = list(itertools.chain.from_iterable(terms))
        terms = [re.sub(r"\(.*\)|\[.*\]","",t.strip()) for t in terms]
        terms = Chinese_filter(terms)
        #terms = Traditional2Simplified(terms)
    full_dict.update(terms)
    print("导入词典完成！...一共有%d个词\n"%len(full_dict))
    
    # Load jieba dict
    """
    jieba_dict = set()
    with open(jieba_dict_path, 'r', encoding="utf-8") as jieba_file:
        terms = jieba_file.readlines()
        terms = [t.split(" ")[0] for t in terms]
        terms = Chinese_filter(terms)
        terms = Traditional2Simplified(terms)
    jieba_dict.update(terms)
    """

    context_dir = args.f
    print("正在打开病历...")
    with open(context_dir, encoding="UTF-8") as f:
        todos = f.read()
    """
    todos.replace("\n\r", " ")
    todos.replace("\n"," ")
    todos.replace("\r"," ")
    """
     
    """
    #(我跑demo时去掉了，袁总跑的时候可以去掉注释，这样会多5分钟，但是去掉所有繁体字)
    print("将病历繁体字翻译成简体字...")
    todos = Traditional2Simplified(todos)
    print("病历转换繁体字完成！\n")
    """
    
    print("正在jieba加载字典...")
    for t in tqdm(full_dict):
        jieba.add_word(t) 
    print("字典加载完毕！")
    
    print("正在分词，构造NER样本..., Output")
    sentense = re.sub("[\n\r\t ]+", " ", todos) #与其在最后加一个，不如一开始就把所有\n都干掉
    t1 = time.time()
    print("正在分词...(jieba固有速度就是这么慢)")
    seg_list = jieba.lcut(sentense, cut_all=False)
    print("jieba分词结束！共过去%d 秒"%(time.time()-t1))

    file_name = os.path.abspath(args.f)[0:-4]
    with open(file_name + '_ner.txt', 'w', encoding='utf-8') as f:
        for i in range(len(seg_list)):
            if seg_list[i].strip() == "":
                f.write(" " + os.linesep)
                continue
            if seg_list[i] in full_dict:
                if len(seg_list[i])==1:
                    f.write(seg_list[i] + " O" + os.linesep)
                else:
                    f.write(seg_list[i][0] + " B" + os.linesep)
                    for j in range((len(seg_list[i])-2)):
                        f.write(seg_list[i][j+1] + " M" + os.linesep)
                    f.write(seg_list[i][-1] + " E" + os.linesep)
            else:
                for j in range(len(seg_list[i])):
                    f.write(seg_list[i][j] + " O" + os.linesep)

