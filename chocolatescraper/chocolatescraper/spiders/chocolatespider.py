# import scrapy
 
# class ChocolateSpider(scrapy.Spider):

#    # The name of the spider
#    name = 'chocolatespider'

#    # These are the urls that we will start scraping
#    start_urls = ['https://www.chocolate.co.uk/collections/all']

#    def parse(self, response):

#        products = response.css('product-item')
#        for product in products:
#            # Here we put the data returned into the format we want to output for our csv or json file
#            yield{
#                 'name' : product.css('a.product-item-meta__title::text').get(),
#                 'price' : product.css('span.price').get().replace('<span class="price">\n              <span class="visually-hidden">Sale price</span>','').replace('</span>',''),
#                 'url' : product.css('div.product-item-meta a').attrib['href'],
#             }

#        next_page = response.css('[rel="next"] ::attr(href)').get()

#        if next_page is not None:
#            next_page_url = 'https://www.chocolate.co.uk' + next_page
#            yield response.follow(next_page_url, callback=self.parse)
import scrapy
import re


class ChocolateSpider(scrapy.Spider):
    name = "chocolatespider"
    allowed_domains = ["chocolate.co.uk"]
    start_urls = ["https://www.chocolate.co.uk/collections/all"]

    def parse(self, response):
        for product in response.css("product-item"):

            name_raw = product.css('a.product-item-meta__title::text').get()
            name = name_raw.strip() if name_raw else ""

            # ─── Price extraction ───────────────────────────────────────
            price_parts = product.css("span.price ::text").getall()

            # Join all text nodes and normalize whitespace
            raw_price = " ".join(price_parts).strip()

            # Remove known unwanted text (very common Shopify pattern)
            cleaned = re.sub(r"(Sale price|Regular price|Original price|From )\s*", "", raw_price, flags=re.I)

            # Optional: if you see "From " often and want to keep it
            # cleaned = re.sub(r"^\s*From\s+", "From ", cleaned)

            # Final cleanup: collapse multiple spaces, remove leftover newlines
            cleaned = re.sub(r"\s+", " ", cleaned).strip()

            # Fallback
            if not cleaned or cleaned == "£":
                cleaned = "N/A"

            # URL
            url_raw = product.css('a.product-item-meta__title::attr(href)').get()
            url = response.urljoin(url_raw) if url_raw else ""

            yield {
                "name": name,
                "price": cleaned,
                "url": url,
            }

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)