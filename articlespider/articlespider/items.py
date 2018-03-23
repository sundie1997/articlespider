# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import re
import datetime
import scrapy
from scrapy.loader import ItemLoader#自定义的ArticleItemLoader需要继承ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join#MapCompose对数据进行预处理,TakeFirst提取数组中的第一个数据


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def date_convert(value):#date格式转换
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()

    return create_date


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


def return_value(value):#front_image_url调用，小技巧，不太懂
    return value


def remove_comment_tags(value):
    #去掉tag中提取的评论
    if "评论" in value:
        return ""
    else:
        return value


class ArticleItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()#此函数用来取数组中的第一个数据，但是是str类型

class JobBolearticleItem(scrapy.Item):
    title=scrapy.Field()
    create_date=scrapy.Field(
        input_processor=MapCompose(date_convert),
    )
    url=scrapy.Field()
    url_object_id=scrapy.Field()#对url_object_id进行md5处理，让url变成一个长度固定的，唯一的值
    praise_nums=scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comments_nums=scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums=scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    content=scrapy.Field()
    tags=scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),#去掉tags中出现的评论
        output_processor=Join(",")#使用join把字符串连接起来，原理同最开始的写法
    )
    front_image_url=scrapy.Field(
        output_processor=MapCompose(return_value)#保证front_image_url里面的参数格式是list,,配置image pipeline之后，front_image_url传入必须是list形式
    )
    front_image_path=scrapy.Field()#方便之后scrapy下载图片，提取articleImagePipeline里面的results里面的path

