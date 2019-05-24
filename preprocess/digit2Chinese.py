"""
@ DavidYQY
你好622袁正 -> 你好六二二袁正
# this is a test python file for YQY. Haven't put into pratical use
"""

_chineseDigit = {
    'Lower': {
        '0': '零',
        '1': '一',
        '2': '二',
        '3': '三',
        '4': '四',
        '5': '五',
        '6': '六',
        '7': '七',
        '8': '八',
        '9': '九',
        '.': '点'},

    'Upper': {
        '0': '零',
        '1': '壹',
        '2': '贰',
        '3': '叁',
        '4': '肆',
        '5': '伍',
        '6': '陆',
        '7': '柒',
        '8': '捌',
        '9': '玖'
    }
}
    
def dight2Chinese(sentenses):
    temp = []
    for s in sentenses:
        for key in _chineseDigit['Lower']:
            s = s.replace(key,_chineseDigit['Lower'][key])
        temp.append(s)
    return temp


if __name__ == '__main__':
    # ap = argparse.ArgumentParser()
    # ap.add_argument('-n', '--number', type=int, default=0)
    # ap.add_argument('-l', '--lower', type=bool, default=True)
    #
    # args = vars(ap.parse_args())
    #
    # converter1(args)
    number = ['你好622袁正','lby622.0520牛逼']
    print(dight2Chinese(number))

