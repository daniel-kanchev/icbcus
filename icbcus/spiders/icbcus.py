import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from icbcus.items import Article


class IcbcusSpider(scrapy.Spider):
    name = 'icbcus'
    start_urls = ['https://www.icbc-us.com/ICBC/%E6%B5%B7%E5%A4%96%E5%88%86%E8%A1%8C/%E5%B7%A5%E9%93%B6%E7%BE%8E%E5%9B%BD%E7%BD%91%E7%AB%99/EN/AboutUs/News/default.htm']

    def parse(self, response):
        links = response.xpath('//a[@class="data-collecting-sign textlsb"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('(//a[@class="textlsb"])[last()]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="subtitleclass"]/span//text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@id="InfoPickFromFieldControl"]/text()').get()
        if date:
            date = date.strip()[-11:-1]

        content = response.xpath('//td[@id="mypagehtmlcontent"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
