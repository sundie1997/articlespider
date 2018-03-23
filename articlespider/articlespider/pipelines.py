# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi#adbapi可以将mysqldb里面的一些操作变成异步化的操作
import MySQLdb
import MySQLdb.cursors
import codecs
import json

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item#pipeline可以拦截item并保存到其他地方

class JsonWithEncodingPipeline(object):#继承object
    def __init__(self):#初始化的时候打开json文件
        self.file=codecs.open('article.json','w',encoding="utf-8")#通过codecs方法写入article.json

    def process_item(self, item, spider):
        lines=json.dumps(dict(item),ensure_ascii=False) + "\n"#把item写入json当中，item要转换成dict才能dumps
        self.file.write(lines)#写入article.json当中
        return item

    def spider_closed(self,spider):#当出现spider_closed,关闭这个文件的写入
        self.file.close()

class MysqlPipeline(object):
    #采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', 'root', 'articlespider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, url, create_date, fav_nums,url_object_id)
            VALUES (%s, %s, %s, %s,%s)
        """
        self.cursor.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["fav_nums"],item["url_object_id"]))
        self.conn.commit()

class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):#接收dbpool
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):#定义from_settings直接取settings中定义的值
        dbparms = dict(#传入的参数要和MySQLdb.connect里面的connection下面的参数一致
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)#这是一个连接池，MYSQLdb是adbapi里面的dbapiName，**dbparms是要传入的参数
        return cls(dbpool)#返回一个实例

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常


    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)


    def do_insert(self, cursor,item):
        insert_sql = """
            insert into jobbole_article(title, url, create_date, fav_nums,url_object_id)
            VALUES (%s, %s, %s, %s,%s)
        """
        cursor.execute(insert_sql,
                            (item["title"], item["url"], item["create_date"], item["fav_nums"], item["url_object_id"]))


class JsonExporterPipleline(object):
    #调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()


    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class articleImagePipeline(ImagesPipeline):#继承ImagesPipeline，只用来处理封面图的自定义的pipeline，


    def item_completed(self,results,item,info):#results里面有两个参数，list里面有tuple和dict，dict里面的path是image保存的文件的路径
        if "front_image_url" in item:#知乎等网站可能没有front_image_url
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path

        return item


