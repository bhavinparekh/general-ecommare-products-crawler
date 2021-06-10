# -*- coding: utf-8 -*-
import json
import re
from urllib.parse import urlparse, urljoin

import colorama
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .regex_generator import RegexCreator
# init the colorama module
from ...pymongo_driver import update_data, status_compelete, remove_status_flag, create_status_flag

colorama.init()

GREEN = colorama.Fore.GREEN
YELLOW = colorama.Fore.YELLOW
RED = colorama.Fore.RED
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
regexCreator = RegexCreator()
# initialize the set of links (unique links)
internal_urls = set()
visited_links = set()
titles = set()
external_urls = set()
total_urls_visited = 0
isScriptProduct = False

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
prefs = {"plugins.always_open_pdf_externally": False}
chrome_options.add_experimental_option("prefs", prefs)


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_website_links(url, regex):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc

    try:
        with webdriver.Chrome(executable_path="chromedriver", options=chrome_options) as driver:
            driver.implicitly_wait(10)
            driver.get(url)
            # print(driver.find_elements_by_name('404'))
            soup = BeautifulSoup(driver.page_source, "html.parser")

            for a_tag in soup.findAll("a"):
                href = a_tag.attrs.get("href")
                if href == "" or href is None:
                    # href empty tag
                    continue
                # join the URL if it's relative (not absolute link)
                href = urljoin(url, href)

                # remove URL GET parameters, URL fragments, etc.

                if re.search(regexCreator.denyUrlRegex, href):
                    continue
                if not is_valid(href):
                    # not a valid URL
                    continue
                if href in internal_urls:
                    # already in the set
                    continue
                if href in visited_links:
                    # already in the set
                    continue
                if domain_name not in href:
                    continue

                urls.add(href)
                print(f"{GREEN}[*] Internal link: {href}{RESET}")
                ''' if re.match(regex, href):
                    product = {"url": href}
                    update_data(product)
                '''
                if re.match(regex, href):
                    product = detect_product(href, regex)
                    print(product)
                    if product is not None:
                        update_data(product)

                internal_urls.add(href)
            return urls

    except Exception:
        return None


def detect_product(url, regex):
    with webdriver.Chrome(executable_path="chromedriver", options=chrome_options) as driver:
        driver.implicitly_wait(10)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        if re.match(regex, driver.current_url):
            product = detect_from_script(soup)
            if product and isScriptProduct:
                return product
            else:
                title = detect_title(soup)
                cat = detect_cat(soup)
                try:
                    for i in cat:
                        if i in ["Accueil", 'Home', '', '>', title]:
                            cat.remove(i)
                except Exception:
                    pass
                price, currency = detect_price(soup)
                description = detect_description(soup)
                images = detect_images(soup, url)
                # options = detect_options(soup)
                reference = detect_reference(soup)
                extra = {}
                if reference != '':
                    extra['sku'] = reference
                '''if len(options) != 0:
                    extra['options'] = options'''
                if price != '' and title != '' and price != '0.00':
                    product = {"url": url, "title": title, "categories": cat, "price": price,
                               "currency": currency, "images": images,
                               "description": description, "extra": extra}

                    return product
                else:
                    return None
        else:
            return None


def detect_from_script(soup):
    try:
        for script in soup.findAll("script", attrs={"type": "application/ld+json"}):
            data = json.loads(script.contents[0])
            if data['@type'] == 'Product':
                global isScriptProduct
                isScriptProduct = True
                try:
                    url = data['offers']['url']
                except Exception:
                    try:
                        url = data['url']
                    except Exception:
                        url = None
                try:
                    title = data['name']
                except Exception:
                    try:
                        title = detect_title(soup)
                    except Exception:
                        title = None
                try:
                    categories = [data['category']]
                except Exception:
                    try:
                        categories = [data['offers']['category']]
                    except Exception:
                        try:
                            categories = detect_cat(soup)
                        except Exception:
                            categories = None
                try:
                    price = data['offers']['price']
                except Exception:
                    try:
                        price = data['price']
                    except Exception:
                        try:
                            price, currency = detect_price(soup)
                        except Exception:
                            price = None
                try:
                    currency = data['offers']['priceCurrency']
                except Exception:
                    try:
                        currency = data['priceCurrency']
                    except Exception:
                        currency = None
                try:
                    if type(data['image']) == list:
                        images = data['image']
                    else:
                        images = [data['image']]
                except Exception:
                    try:
                        if type(data['offers']['image']) == list:
                            images = data['offers']['image']
                        else:
                            images = [data['offers']['image']]
                    except Exception:
                        try:
                            images = detect_images(soup)
                        except Exception:
                            images = None
                try:
                    description = data['description']
                except Exception:
                    try:
                        description = detect_description(soup)
                    except Exception:
                        description = None
                try:
                    sku = data['offers']['sku']
                except Exception:
                    try:
                        sku = data['sku']
                    except Exception:
                        try:
                            sku = detect_reference(soup)
                        except Exception:
                            sku = ''
                extra = {}
                '''options = detect_options(soup)
                if options is not None:
                    extra['options'] = options'''
                if sku != '':
                    extra['sku'] = sku
                product = {
                    "url": url,
                    "title": title,
                    "categories": categories,
                    "price": price,
                    "currency": currency,
                    "images": images,
                    "description": description,
                    "extra": extra
                }
                return product
    except Exception:
        return None


def detect_reference(soup):
    reference = ''
    try:
        reference = soup.find(attrs={"class": "sku"}).text.strip()
    except Exception:
        pass
    if reference == '':
        try:
            reference = soup.find(attrs={"id": "sku"}).text.strip()
        except Exception:
            pass
    if reference == '':
        try:
            reference = soup.find(attrs={"itemprop": "sku"}).text.strip()
        except Exception:
            pass
    if reference == '':
        try:
            reference = soup.find(attrs={"id": "pref6zqxIf"}).text.strip()
        except Exception:
            pass
    if reference == '':
        try:
            reference = soup.find(attrs={"id": "product_reference"}).text.strip()
            reference = reference.replace('Référence', '').replace(':', '').replace('Reference', '')
        except Exception:
            pass
    return reference


def detect_options(soup):
    options = []
    try:
        options_row = soup.find_all('option')
        for option in options_row[1:]:
            if "disabled" not in option:
                options.append(option.text.strip())
    except Exception:
        pass
    if len(options) == 0:
        try:
            for option in soup.findAll('div', attrs={"role": "option"}):
                options.append(option.text.strip())
        except Exception:
            pass
    try:
        options = list(dict.fromkeys(options))
    except Exception:
        pass
    return options


def get_cat(html):
    cat = []
    try:
        raw = html.findAll("li")
        for i in raw:
            cat.append(i.text.strip())
    except Exception:
        pass
    if len(cat) == 0:
        try:
            raw = html.findAll("a")
            for i in raw:
                cat.append(i.text.strip())
        except Exception:
            pass

    return cat


def detect_cat(soup):
    cat = ''
    try:
        cat = get_cat(soup.find(attrs={"class": "breadCrumBox"}))

    except Exception:
        pass
    if len(cat) == 0:
        try:
            cat = get_cat(soup.find(attrs={"class": "breadcrumbs"}))

        except Exception:
            pass
    if len(cat) == 0:
        try:
            cat = get_cat(soup.find(attrs={"class": "breadcrumb"}))

        except Exception:
            pass
    if len(cat) == 0:
        try:
            cat = get_cat(soup.find(attrs={"id": "breadcrumb"}))

        except Exception:
            pass
    if len(cat) == 0:
        try:
            cat = get_cat(soup.find(attrs={"class": "catbreadcrumb"}))

        except Exception:
            pass
    if len(cat) == 0:
        try:
            cat = get_cat(soup.find(attrs={"class": "woocommerce-breadcrumb"}))

        except Exception:
            pass
    if len(cat) == 0:
        try:
            cat = get_cat(soup.find(attrs={"class": "yoast-breadcrumb"}))

        except Exception:
            pass
    if len(cat) == 0:
        try:
            cat = get_cat(soup.find(attrs={"class": "single-breadcrumbs"}))

        except Exception:
            pass
    return cat


def get_price(text):
    try:
        price = re.findall(r'(\d[\d.,]*)\b', text)[0].replace(',', '.')
        if text.find('£') != -1:
            return price, 'POUND'
        elif text.find('$') != -1:
            return price, 'USD'
        elif text.find('EUR') != -1:
            return price, 'EUR'
        elif text.find('€') != -1:
            return price, 'EUR'
        elif text.find('₹') != -1:
            return price, 'INR'
        elif text.find('₹') != -1:
            return price, 'INR'
        elif text.find('RS') != -1:
            return price, 'INR'
    except Exception:
        return None


def detect_price(soup):
    price = ''
    currency = ''
    try:
        price, currency = get_price(soup.find(attrs={"class": "PBSalesPrice"}).text.strip())
    except Exception:
        pass
    if price == '':
        try:
            price = soup.find(attrs={"itemprop": "price"}).attrs.get('content')
            try:
                currency = soup.find(attrs={"itemprop": "priceCurrency"}).attrs.get('content')
            except Exception:
                pass
            if price == None:
                price = ''
        except Exception:
            pass
    if price == '':
        try:
            if re.search(r'\d+', soup.find(attrs={"itemprop": "price"}).text.strip()):
                price, currency = get_price(soup.find(attrs={"itemprop": "price"}).text.strip())
        except Exception:
            pass
    if price == '':
        try:
            if re.search(r'\d+', soup.find(attrs={"class": "wcfad-main-price"}).text.strip()):
                price, currency = get_price(soup.find(attrs={"class": "wcfad-main-price"}).text.strip())
        except Exception:
            pass
    if price == '':
        try:
            if re.search(r'\d+', soup.find(attrs={"class": "price"}).text.strip()):
                price, currency = get_price(soup.find(attrs={"class": "price"}).text.strip())
        except Exception:
            pass
    if price == '':
        try:
            price, currency = get_price(soup.find(attrs={"class": "field-commerce-price"}).text.strip())
        except Exception:
            pass
    if price == '':
        try:
            price, currency = get_price(soup.find(attrs={"id": "product-price"}).text.strip())
        except Exception:
            pass
    if price == '':
        try:
            price, currency = get_price(soup.find(attrs={"class": "tw-price"}).text.strip())
        except Exception:
            pass
    if price == '':
        try:
            price, currency = get_price(soup.find(attrs={"class": "ttc"}).text.strip())
        except Exception:
            pass
    return price, currency


def detect_title(soup):
    title = ''

    try:
        title = soup.find("h1", attrs={"itemprop": "name"}).text.strip()
    except Exception:
        pass
    if title == '':
        try:
            title = soup.find("h1", attrs={"class": "product-page-title"}).text.strip()
        except Exception:
            pass
    if title == '':
        try:
            title = soup.find("h4", attrs={"itemprop": "name"}).text.strip()
        except Exception:
            pass
    if title == '':
        try:
            title = soup.find("h2", attrs={"itemprop": "name"}).text.strip()
        except Exception:
            pass
    if title == '':
        try:
            title = soup.find("h1", attrs={"class": "PBItemTitle"}).text.strip()
        except Exception:
            pass
    if title == '':
        try:
            title = soup.find("h1", attrs={"class": "product_title"}).text.strip()
        except Exception:
            pass
    if title == '':
        try:
            title = soup.find("span", attrs={"itemprop": "name"}).text.strip()
        except Exception:
            pass
    if title == '':
        try:
            title = soup.find("h1").text.strip()
        except Exception:
            pass

    return title


def detect_description(soup):
    description = ''

    if description == '':
        try:
            description = soup.find("div", attrs={"itemprop": "description"}).text.strip()
            if re.search('\(lire la suite\)', description):
                try:
                    description = soup.find("section", {"class": "page-product-box"}).text.strip()
                except Exception:
                    pass
        except Exception:
            pass
    if description == '':
        try:
            description = soup.find("div", attrs={"class": "product-single__description"}).text.strip()
        except Exception:
            pass
    if description == '':
        try:
            description = soup.find("div", attrs={
                "class": "et_pb_tab clearfix et_pb_active_content et-pb-active-slide"}).text.strip()
        except Exception:
            pass
    if description == '':
        try:
            description = soup.find("div", attrs={"id": "description"}).text.strip()
            if re.search('\(lire la suite\)', description):
                try:
                    description = soup.find("section", attrs={"class": "page-product-box"}).text.strip()
                except Exception:
                    pass
        except Exception:
            pass
    if description == '':
        try:
            description = soup.find("div", attrs={"class": "field-body"}).text.strip()
        except Exception:
            pass
    if description == '':
        try:
            description = soup.find("div", attrs={"class": "description"}).text.strip()
            if re.search('\(lire la suite\)', description):
                try:
                    description = soup.find("section", attrs={"class": "page-product-box"}).text.strip()
                except Exception:
                    pass
        except Exception:
            pass
    if description == '':
        try:
            description = soup.find("span", attrs={"itemprop": "description"}).text.strip()
            if re.search('\(lire la suite\)', description):
                try:
                    description = soup.find("section", attrs={"class": "page-product-box"}).text.strip()
                except Exception:
                    pass
        except Exception:
            pass
    if description == '':
        try:
            description = soup.find("div", attrs={"class": "product-description"}).text.strip()
        except Exception:
            pass
    if description == '':
        try:
            description = soup.find("div", attrs={"id": "short_description_block"}).text.strip()
        except Exception:
            pass
    if description == '':
        try:
            description = soup.find("div", attrs={"class": "product-desc"}).text.strip()
        except Exception:
            pass
    if description == '':
        try:
            description = soup.find("div", attrs={"class": "field-name-field-fp-description"}).text.strip()
        except Exception:
            pass
    if description == '':
        try:
            description = soup.find("div", attrs={"class": "ptext"}).text.strip()
        except Exception:
            pass
    if description == '':
        try:
            description = soup.find("div", attrs={"class": "product-short-description"}).text.strip()
        except Exception:
            pass
    return description


def detect_images(soup, url):
    images = []
    regex_img = r"\.jpeg|\.jpg|\.JPG|\.JPEG"

    try:
        data = soup.findAll(attrs={"itemprop": "image"})
        for i in data:
            if i.attrs.get('src'):
                images.append(i.attrs.get('src'))
            elif i.attrs.get('href'):
                if re.search(regex_img, i.attrs.get('href')):
                    images.append(i.attrs.get('href'))
            elif i.text:
                if re.search(regex_img, i.text()):
                    images.append(i.text())
            else:
                if i.attrs.get('content') is not None and re.search(regex_img, i.attrs.get('content')):
                    images.append(i.attrs.get('content'))
    except Exception:
        pass
    if len(images) == 0:
        try:
            raw = soup.find(attrs={"class": "p-summary__image"})
            data = raw.findAll('img')
            for img in data:
                if img.attrs.get('src') is not None:
                    images.append(img.attrs.get('src'))
        except Exception:
            pass

    if len(images) == 0:
        try:
            data = soup.findAll('a')
            for a in data:
                img = a.attrs.get('href')
                if img is not None and re.search(regex_img, img) and not re.search(
                        'pinterest.com/', img):
                    images.append(img)
        except Exception:
            pass

    if len(images) == 0:
        try:
            data = soup.findAll('img')
            for img in data:
                if img.attrs.get("style"):
                    if img.attrs.get('src') is not None and re.search(regex_img,
                                                                      img.attrs.get('src')) and not re.search(
                        'pinterest.com/', img.attrs.get('src')):
                        images.append(img.attrs.get('src'))
        except Exception:
            pass

    if len(images) == 0:
        try:
            raw = soup.find(attrs={"class": "product-img"})
            data = raw.findAll('img')
            for img in data:
                if img.attrs.get('src') != None and re.search(regex_img,
                                                              img.attrs.get('src')) and not re.search(
                    '/cms/|/vi/|themes|small_default/', img.attrs.get('src')):
                    images.append(img.attrs.get('src'))
        except Exception:
            pass
    if len(images) == 0:
        try:
            raw = soup.find(attrs={"class": "fp_pictures_pictures"})
            data = raw.findAll('img')
            for img in data:
                if img.attrs.get('src') != None and re.search(regex_img,
                                                              img.attrs.get('src')) and not re.search(
                    '/cms/|/vi/|themes|small_default/', img.attrs.get('src')):
                    images.append(img.attrs.get('src'))
        except Exception:
            pass
    if len(images) == 0:
        try:
            img = soup.find(attrs={"class": "lazyautosizes lazyloaded"})
            images.append(img.attrs.get('src'))
        except Exception:
            pass
    if len(images) == 0:
        try:
            raw = soup.find(attrs={"class": "l-pdp_primary_content-images"})
            data = raw.findAll('img')
            for img in data:
                if img.attrs.get('src') != None and re.search(regex_img,
                                                              img.attrs.get('src')) and not re.search(
                    '/cms/|/vi/|themes|small_default/', img.attrs.get('src')):
                    images.append(img.attrs.get('src'))
        except Exception:
            pass

    if len(images) != 0:
        for img in images:
            if re.search('http', img) or img in images:
                pass
            else:
                images.remove(img)
                images.append(urljoin(url, img))
        images = list(set(images))
    return images


def crawl(url, max_urls, regex):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1

    links = get_all_website_links(url, regex)
    if links is not None:
        for link in links:
            if link in visited_links:
                print(link, 'visited')
                continue
            if total_urls_visited > max_urls:
                break

            crawl(link, max_urls=max_urls, regex=regex)


def start_scrap(url):
    url = url
    remove_status_flag(url)
    create_status_flag(url, "in-progress")
    regex = regexCreator.getRegex(url)
    max_urls = 200000

    crawl(url, max_urls=max_urls, regex=regex)

    print("[+] Total Internal links:", len(internal_urls))
    print("[+] Total External links:", len(external_urls))
    print("[+] Total URLs:", len(external_urls) + len(internal_urls))
    create_status_flag(url, "complete")


# start_scrap('https://www.ladrogueriedecharlotte.com/cadeau-mystere-rouge-c2x33501154')
