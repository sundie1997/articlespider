# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.loader import ItemLoader
from scrapy.http import Request#把Request里面的url交给scrapy
from urllib import parse#url可能出现无域名的情况，这时候引用函数parse
from articlespider.items import JobBolearticleItem,ArticleItemLoader
from articlespider.utils.common import get_md5

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        # 把post_url里面的url给Request,回调函数，把detail里面的self传递回来
        # yiled关键字把Request交给scrapy进行下载
        post_nodes=response.css("#archive .floated-thumb .post-thumb a")#提取文章列表的url后交给scrapy进行下载并进行解析
        for post_node in post_nodes:
            image_url=post_node.css("img::attr(src)").extract_first("")
            post_url=post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": parse.urljoin(response.url, image_url)},
                              callback=self.parse_detail)

        #提取“下一页”节点并交给scrapy进行下载
        next_urls=response.css(".next.page-numbers::attr(href)").extract()[0]#next 和 page-numbers是两个class,这样表示这个节点有next和page
        if next_urls:
            yield Request(url=parse.urljoin(response.url,next_urls),callback=self.parse)

    def parse_detail(self,response):
        article_item=JobBolearticleItem()
        #提取文章的具体字段
        '''
        re_selector=response.xpath('//*[@id="post-113722"]/div[1]/h1/text()')
        re_selector1=response.xpath('//div[@class="entry-header"]/h1/text()')
        title=response.xpath('//div[@class="entry-header"]/h1/text()').extract_first("")
        create_date= response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip().replace("·","").strip()
        praise_nums=response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract()[0]

        fav_nums=response.xpath("//span[contains(@class,'bookmark-btn')]/text()").extract()[0]
        match_re=re.match(".*?(\d+).*",fav_nums)#正则表达式匹配
        if match_re:
            fav_nums=int(match_re.group(1))
        else:
            fav_nums=0

        comments_nums = response.xpath("//a[@href='#article-comment']/span/text()").extract()[0]
        match_re = re.match(".*?(\d+).*", comments_nums)
        if match_re:
            comments_nums = int(match_re.group(1))
        else:
            comments_nums=0

        content=response.xpath("//div[@class='entry']").extract()[0]#取全文内容
        create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        tag_list=response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        tag_list=[element for element in tag_list if not element.strip().endswith("评论")]  # 去重“评论”
        tags=",".join(tag_list)
        '''
        '''
        #通过css选择器提取字段
        front_image_url=response.meta.get("front_image_url","")#文章封面图
        title=response.css(".entry-header h1::text").extract()[0]#::text  伪类选择器
        create_date=response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·","").strip()
        praise_nums=response.css(".vote-post-up h10::text").extract()[0]

        fav_nums=response.css("span.bookmark-btn::text").extract()[0]
        match_re = re.match(".*?(\d+).*", fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums=0
        comments_nums= response.css("a[href='#article-comment'] span::text").extract()[0]
        match_re = re.match(".*?(\d+).*", comments_nums)
        if match_re:
            comments_nums = int(match_re.group(1))
        else:
            comments_nums=0
        content=response.css("div.entry").extract()[0]
        tag_list=response.css("p.entry-meta-hide-on-mobile a::text").extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]  # 去重“评论”
        tags = ",".join(tag_list)

        #items传值填充
        article_item["title"]=title
        try:
             create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        except Exception as e:
             create_date = datetime.datetime.now().date()
        article_item["create_date"]=create_date
        article_item["url"]=response.url
        article_item["praise_nums"]=praise_nums
        article_item["fav_nums"]=fav_nums
        article_item["comments_nums"]=comments_nums
        article_item["content"]=content
        article_item["tags"]=tags
        article_item["front_image_url"]=[front_image_url]
        article_item["url_object_id"]=get_md5(response.url)
        '''
        #通过Item Loader加载item
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        item_loader=ArticleItemLoader(item=JobBolearticleItem(),response=response)#这里的ItemLoader要换成自定义的ArticleItemLoader
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comments_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")

        article_item = item_loader.load_item()

        yield article_item

