import requests
import json
import urllib
import re

class query:
    def __init__(self,url,api_key):
        self.url = url
        self.api_key = api_key
        self.logical_operators = ["and_","not_",'@']

    def query(self,url,api_key=None,search_dat = None,category_dat = None):
        if search_dat is not None:
            url = 'https://wallhaven.cc/api/v1/search?'
            url = self.url_tag_parser(url,search_dat)

        if category_dat is not None:
            url = self.add_search_settings(url,category_dat)

        if api_key and "apikey=" not in url and api_key!="":
            url = f"{url}&apikey={api_key}"

        response = self.get_data(url)
        response_data = json.loads(response.text)  # Parse the JSON string into a Python dictionary
        data = self.parse_data(response_data)
        return (url,data) 
    
    def page_search(self,url):
        if self.api_key == "" and "page=" not in url:
            url=f"{url}&page=2"
            
        elif "page=" not in url:
            apikey_pos = url.find("&apikey=")
            url = f"{url[:apikey_pos]}&page=2{url[apikey_pos:]}"
        response = self.get_data(url)
        response_data = json.loads(response.text)  # Parse the JSON string into a Python dictionary
        data = self.parse_data(response_data)
        return (url,data) 

    def add_search_settings(self, url, category_dat):
        for elm in category_dat:
            match elm:
                case "category":
                    if "categories=" not in url:
                        code = f"{category_dat.get(elm)[0]}{category_dat.get(elm)[1]}{category_dat.get(elm)[2]}"
                        url = f"{url}&categories={code}"
                    else:
                        url_category_pos = url.find("categories=") + 11  # 11 accounts for the length of "categories="
                        url_category_code = url[url_category_pos:url_category_pos + 3]
                        code = f"{category_dat.get(elm)[0]}{category_dat.get(elm)[1]}{category_dat.get(elm)[2]}"
                        if url_category_code != code:
                            # Replace the existing code with the new one
                            url = re.sub(r'categories=[^&]*', f'categories={code}', url)

                case "purity":
                    if "purity=" not in url:
                        code = f"{category_dat.get(elm)[0]}{category_dat.get(elm)[1]}{category_dat.get(elm)[2]}"
                        url = f"{url}&purity={code}"
                    else:
                        url_purity_pos = url.find("purity=") + 7  # 7 accounts for the length of "purity="
                        url_purity_code = url[url_purity_pos:url_purity_pos + 3]
                        code = f"{category_dat.get(elm)[0]}{category_dat.get(elm)[1]}{category_dat.get(elm)[2]}"
                        if url_purity_code != code:
                            # Replace the existing purity code
                            url = re.sub(r'purity=[^&]*', f'purity={code}', url)

                case "order":
                    if "sorting=" not in url:
                        if category_dat[elm] == "toplist":
                            url = f"{url}&topRange={category_dat['range']}"
                        url = f"{url}&sorting={category_dat[elm]}"
                    else:
                        if category_dat[elm] == "toplist":
                            url_toprange_match = re.search(r'topRange=([^&]*)', url)
                            if url_toprange_match:
                                url_toprange = url_toprange_match.group(1)
                                if url_toprange != category_dat['range']:
                                    url = re.sub(r'topRange=[^&]*', f'topRange={category_dat["range"]}', url)
                            else:
                                url = f"{url}&topRange={category_dat['range']}"
                                url = re.sub(r'sorting=[^&]*', f'sorting={category_dat[elm]}', url)
                                #add toplist as a new sorting

                        else:
                            sorting_match = re.search(r'sorting=([^&]*)', url)
                            if sorting_match:
                                url_sorting_code = sorting_match.group(1)
                                if url_sorting_code != category_dat[elm]:
                                    # Replace the sorting value
                                    url = re.sub(r'sorting=[^&]*', f'sorting={category_dat[elm]}', url)
                            else:
                                url = f"{url}&sorting={category_dat[elm]}"

                case "sort":
                    if "order=" not in url:
                        url = f"{url}&order={category_dat[elm]}"
                    else:
                        url = re.sub(r'order=[^&]*', f'order={category_dat[elm]}', url)

        return url
    

    def url_tag_parser(self,url,search_dat):
        search_dat = search_dat.replace("\n"," ")
        search_dat = search_dat.split(' ')
        tag = "q="
        specifiers = ""
        for elm in search_dat:
            if elm[:4] in self.logical_operators:
                specifiers = self.add_logical_operators(elm,specifiers)
            else:
                if len(tag)==2:
                    tag = f"{tag}{elm}"
                elif elm == "":
                    continue
                else:
                    tag = f"{tag}%20{elm}"

        url = f"{url}{tag}{specifiers}"

        return url

    def add_logical_operators(self,logical_operator,string):
        match logical_operator[:4]:
            case "and_":
                string = f"{string}%20+{logical_operator[4:]}"
            case "not_":
                string = f"{string}%20-{logical_operator[4:]}"
            case "@":
                string = f"{string}%20@{logical_operator[1:]}"

        return string
                
    def get_data(self,url):
        # Perform a GET request to the URL and return the response
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            return response
        else:
            raise Exception(f"Failed to fetch data. Status code: {response.status_code}")

    def get_thumbnail(self,url,out_path):

        filename = url.split('/')[-1]
        r = requests.get(url, allow_redirects=True)
        open(f"{out_path}", 'wb').write(r.content)

        return

    def parse_data(self,data):
        parsed_data = {


        }

        for elm in data['data']:
            parsed_data[elm['id']] = elm

        return parsed_data



