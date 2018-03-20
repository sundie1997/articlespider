#这个utils （python package）里面用来存放常用的函数

import hashlib#md5里面的url需要引进hashlib函数


#定义一个md5函数
def get_md5(url):
    if isinstance(url,str):
        url=url.encode("utf-8")#判断url是否为unicode，如果是，转成encode
    m=hashlib.md5()
    m.update(url)
    return m.hexdigest()

if __name__=="__main__":
    print (get_md5("http://jobbole.com".encode("utf-8")))#python3里面的字符都是unicode格式的，而hashlib不支持unicode，所以要转成encode


