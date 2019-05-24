"""
@author: Qiuyang Yin
@date: 2018/11/24
@use: clean data, create positive and negative samples for term judger based on dictionary itself
    see unit test for more infomation
	
Updated 2019: This file is no longer used. However Traditional2Simplified, construct_character_info, Chinese_filter and construct_fake_terms are useful
"""

import re
import random
# from src.negative_sampling.langconv import Converter
from langconv import Converter
from tqdm import tqdm

class wordinfo(object):
    
    '''
    Record every candidate word information include left neighbors, right neighbors, frequency, PMI
    '''
    
    def __init__(self, text):
        super(wordinfo,self).__init__()
        self.text = text
        self.freq = 0
        self.left = []
        self.right = []
        
    def update_data(self, left, right):
        self.freq += 1
        if left:
            self.left.append(left)
        if right:
            self.right.append(right)
            
def chinese_judge(char):
    if u'\u4e00' <= char <= u'\u9fa5':
        return True
    else:
        return False

def construct_character_info(term_list,full_passage = None):
    
    """
    calculate left and right character list for each character
    - if full_passage is provided, then left and right character list is calculated based on passage;
    otherwise it would be calculated based on "\t".join(term_list)
    - full_passage assumes to be a long character
    """
    
    # initialization
    character_dict = set(''.join(term_list)) # each character
    character_info = {}
    for char in character_dict:
        character_info[char] = wordinfo(char)
    
    if (full_passage is None):
        full_terms = '\t'.join(term_list)
    else:
        full_terms = full_passage
    
    stop_word_set = set("！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏."+
                        '\t'+'\n'+'\r')

    print("calculating left right word information...")
    for i,c in enumerate(tqdm(full_terms)):
        if (c not in character_dict):
            continue
        if (i==0 or i == len(full_terms)-1 or chinese_judge(c)==False or (c in stop_word_set)):
            continue
        before = full_terms[i-1]
        after = full_terms[i+1]
        if (chinese_judge(before)==False or (before in stop_word_set)):
            before = None
        if (chinese_judge(after)==False or (after in stop_word_set)):
            after = None
        character_info[c].update_data(before,after)
    
    return(character_info)
    
    
def Traditional2Simplified(sentences): 
    '''
    将sentence中的繁体字转为简体字
    :param sentence: 待转换的句子
    :return: 将句子中繁体字转换为简体字之后的句子
    ''' 
    
    ans = []
    for s in tqdm(sentences):
        ans.append(Converter('zh-hans').convert(s))
    return ans


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

def construct_fake_terms(terms, num = 0 ,
                        shuffle_ratio = 0.0, inside_ratio = 0.0,
                        outside_ratio = 0.5, full_passage = None, full_dict =None):
    """
    @input: true terms(could be list or set), num (terms to construct,default is 1:1)
     - shuffle_ratio (ratio to shuffle)
     - inside_ratio  (ratio to add more words inside)
     - outside_ratio (ratio to add more words outside each word) 
     - deleted_ratio (ratio to delete charcater from word)= 1-shuffle_ratio-inside_ratio-outside_ratio
     - full_passgae: if provided, left/right character would be obtained via passage rather than terms
     - full_dict: if provided, when judging whether to output, it is compared in full_dict rather than terms
    @output: fake terms
    """
    if num == 0:
        num = len(terms)
    s_num = int(shuffle_ratio * num)
    i_num = int(inside_ratio * num)
    o_num = int(outside_ratio * num)
    d_num = num - s_num - i_num - o_num
    
    if (d_num<0 or d_num>num):
        print("ratio given is not valid!")
        return
    
    char_dict = construct_character_info(terms,full_passage)
    word_dict = char_dict.keys()

    if (full_dict is None):
        s_terms = set(terms)
    else:
        s_terms = set(full_dict)
    l_terms = list(terms)
    
    # shuffle
    print("Creating shuffled terms...")
    shuffled_terms = []
    small = random.choices(l_terms,k=s_num*2) # sample with replacement
    for s in small:
        shuffled = ''.join(random.sample(s,len(s)))
        if (shuffled not in s_terms):
            shuffled_terms.append(shuffled)
        if (len(shuffled_terms) >= s_num):
            break
    
    # add words inside(for now only one character is inserted)
    print("Creating insided terms...")
    insided_terms = []
    small = random.choices(l_terms,k=i_num*2)
    for s in small:
        index = random.randint(1,len(s)-1)
        w = random.sample(word_dict, k=1)[0]
        insided = s[:index] + w + s[index:]
        if (insided not in s_terms):
            insided_terms.append(insided)
        if (len(insided_terms) >= i_num):
            break
    
    # add words outside(for now only one character is inserted)
    print("Creating outsided terms...")
    outsided_terms = []
    small = random.choices(l_terms,k=o_num*2)
    for s in small:
        r = random.random()
        if (r>0.5): # add to front
            if (len(char_dict[s[0]].left)==0):# 没有
                w = random.sample(word_dict, k=1)[0]
            else:
                w = random.sample(char_dict[s[0]].left, k=1)[0]
            outsided = w + s
        else:
            if (len(char_dict[s[len(s)-1]].right)==0):
                w = random.sample(word_dict, k=1)[0]
            else:
                w = random.sample(char_dict[s[len(s)-1]].right,k=1)[0]
            outsided = s + w
        if (outsided not in s_terms):
            outsided_terms.append(outsided)
        if (len(outsided_terms) >= o_num):
            break
    
    # delete character randomly by position
    """
    print("Creating deleted terms...")
    deleted_terms = []
    small = random.choices(l_terms, k=d_num * 2)
    for s in small:
        index = random.randint(0, len(s)-1)
        deleted = s[:index]+s[(index+1):]
        if (deleted not in s_terms):
            deleted_terms.append(deleted)
        if (len(deleted_terms) >= d_num):
            break
    """
        
    # delete character head or end
    print("Creating deleted terms...")
    deleted_terms = []
    l2_terms = [x for x in l_terms if len(x)>=3] # 删掉的时候只删除大于等于3个字的咯
    small = random.choices(l2_terms, k=d_num * 2)
    for s in small:
        u = random.random()
        if u > 0.5:
            deleted = s[0:-1]
        else:
            deleted = s[1:]
        if (deleted not in s_terms):
            deleted_terms.append(deleted)
        if (len(deleted_terms) >= d_num):
            break

    fake_terms = shuffled_terms+ insided_terms + outsided_terms + deleted_terms
    random.shuffle(fake_terms)
    fake_terms = [term for term in fake_terms if len(term) >= 2]
    return(fake_terms)
    
if __name__=="__main__": 
    
    """
    # unit test on Traditional2Simplified
    traditional_sentence = ['憂郁的臺灣烏龜', '周杰倫']
    simplified_sentence = Traditional2Simplified(traditional_sentence) 
    print(simplified_sentence) # should be [忧郁的台湾乌龟,周杰伦]
    
    # unit test on Chinese_filter
    input_sentenses = ["尹秋阳","尹秋阳1","袁正牛逼aaaa","俞sir","boyao李","我.凉了","？真的凉了_"]
    print(Chinese_filter(input_sentenses)) # should be ['尹秋阳']
    
    # unit test on construct_fake_terms
    terms = ["12","234","345","4567","5678","67","89","9012","23","3456"]
    print(construct_fake_terms(set(terms)))

    # unit test on construct_character_info
    char_dict = construct_character_info(terms)
    print(char_dict["2"].left) # ['1','1']
    print("Unit Test Done")
    """
    
    data_path = "..\\..\\data\\"
    # overall
    print("\nLoading XiangYaDict")
    with open(data_path+"XiangYaDict.txt", 'r', encoding="utf-8") as xy:
        terms = xy.readlines()
        terms = [t.strip() for t in terms]
    
    print("Filtering Chinese terms")
    terms = Chinese_filter(terms)
    
    print("Translating traditional Chinese to Simplified Chinese")
    terms = Traditional2Simplified(terms)
    
    print("Constructing fake terms")
    fake_terms = construct_fake_terms(terms)
    
    print("Outputing...")
    with open(data_path+'true_terms.txt', 'w', encoding="utf-8") as f:
        for item in terms:
            f.write("%s\n" % item)
    with open(data_path+'fake_terms.txt', 'w', encoding="utf-8") as f:
        for item in fake_terms:
            f.write("%s\n" % item)