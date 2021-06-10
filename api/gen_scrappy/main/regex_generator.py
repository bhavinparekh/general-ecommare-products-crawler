# -*- coding: utf-8 -*-
import re
from urllib.parse import urlparse


class RegexCreator():
    def __init__(self):
        # the denyUrlRegex use to avoid unnecessary url which match given regex
        self.denyUrlRegex = '\?f%5.*|\?__|/redirect/|\.name|\.desc|\.price|\.asc|\.position|login|register|contact|password|user|' \
                            '\?add-to-cart|\?cat=|\?tressage=|\?coussinage=|\?utilisation=|\?color=|\?p_collection=|' \
                            '\?matiere_filtre=|\?pattern=|\?taille=|\?marking=|\?price=|\?gamme=|\?sales_percent=|\?type_produit=' \
                            '|\?ligne_filtre=|\?sleeves=|\?bow_tie=|\?couleur_filtre=|\?coupe=|\?collar=|\?q=|\?sort=|\?src=|/fr/fr/fr/|\.jpg|&|#|\[|\?nosto=' \
                            '|index|content|facebook|twitter|whatsapp|/fr/|/en/|mon-compte|\.pdf|/send/|\.zip|/\?add_to_wishlist='

    def getRegex(self, url):
        # Remove some denyUrlRegex which exist in url
        if re.match('(^[^&]+$|^[^index]+$)', url):
            pass
        else:
            self.denyUrlRegex = self.denyUrlRegex.replace('|&', '').replace('|index', '')
        if re.match('(^[^#]+$)', url):
            pass
        else:
            self.denyUrlRegex = self.denyUrlRegex.replace('|#', '')
        # remove https from the url and split url using /
        product_link = url
        clean_url = product_link.replace("https://", '').replace("http://", '')
        url_level = clean_url.split('/')
        last_slash = False
        try:
            url_level.remove('')
            last_slash = True
        except Exception:
            pass
        regex = product_link.split('/')[0]
        regex = regex + "//" + urlparse(product_link).netloc + '/'
        # size flag use for detect the url levels size
        size_flag = 0
        # create each level regex
        for level in url_level:
            size_flag += 1
            if urlparse(product_link).netloc == level:
                continue
            # match if level is fr,en,p and product
            if re.match('^fr$', level):
                regex = regex + 'fr/'
                self.denyUrlRegex = self.denyUrlRegex.replace('|/fr/|', '|')
            elif re.match('^en$', level):
                regex = regex + 'en/'
                self.denyUrlRegex = self.denyUrlRegex.replace('|/en/|', '|')
            elif re.match('(^[p]+$)', level):
                regex = regex + 'p/'
            elif re.match('(^product+s?$)', level):
                regex = regex + 'product+s?/'
            elif re.match('(^[^\?]|[-a-zA-Z0-9_%àâçéèêëîïôûùüÿñæœ .À-Ÿ#])+\.html$', level):
                regex = regex + '(^[^\?]|[-a-zA-Z0-9_%àâçéèêëîïôûùüÿñæœ .À-Ÿ#])+\.html$/'
            # match if its not a last level of url
            elif re.match('(^[^\?]|[-a-zA-Z0-9_%àâçéèêëîïôûùüÿñæœ .À-Ÿ#])+$', level) and size_flag < len(url_level):
                regex = regex + '(^[^\?]|[-a-zA-Z0-9_%àâçéèêëîïôûùüÿñæœ .À-Ÿ#])+?/'
            # match if its a last level of url
            elif re.match('(^[^\?]|[-a-zA-Z0-9_%àâçéèêëîïôûùüÿñæœ .À-Ÿ#])+$', level) and size_flag >= len(url_level):
                regex = regex + '(^[^\?]|[-a-zA-Z0-9_%àâçéèêëîïôûùüÿñæœ .À-Ÿ#])+?/' if last_slash else regex + '(^[^\?]|[-a-zA-Z0-9_%àâçéèêëîïôûùüÿñæœ .À-Ÿ#])+?$/'
            # its use for if ? exist in url
            elif re.match('([^\?]*)', level) and size_flag < len(url_level):
                queryString = level.split('=')
                queryvalue = queryString[0].split('?')
                qt = (queryvalue[0] if queryvalue[0] == '' else '([^\/]+)') + '\?' + queryvalue[1]
                regex = regex + qt + '=([^\/]+)/'
            elif re.match('([^\?]*)', level) and size_flag >= len(url_level):
                queryString = level.split('=')
                queryvalue = queryString[0].split('?')
                qt = (queryvalue[0] if queryvalue[0] == '' else '([^\/]+)') + '\?' + queryvalue[1]
                regex = regex + qt + '=([^\/]+)/' if last_slash else regex + qt + '=([^\/]+$)/'
        # its use for detect url last slash
        if last_slash:
            regex = (regex + '$')
        else:
            regex = regex[:-1]
        print(regex)
        return regex
