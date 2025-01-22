#import windowmanager
import windowmanager
import PIL
import json
import os



#Resolution
default_res = "1500x800"


#Default setup
title = "Distrohaven"
theme = "dark"
font = "Arial"
font_size = 12
debug = False
api_key = ""
default_site = "https://wallhaven.cc/api/v1/search"
thumbnail_size = "small"
threads = 4     
grid_width = 4
resize_factor = 150
preview_width = 500
navbar_color = "#1F2232"    
preview_color = "#23262F"
sidebar_color = "#23262F"
content_color = "#1A1E23"
text_color = "#FDE8E9"
button_color = "#5B616C"
tag_color = "#1D202B"


config_lst = {

    "title": title, "resolution": default_res, 
              "theme": theme, "debug":debug, "font":font, "font_size":font_size,
              "navbar_color": navbar_color, "sidebar_color": sidebar_color, "content_color": content_color, 
              "text_color": text_color,"button_color": button_color,"tag_color": tag_color, 'preview_color':preview_color,
              "start_url": default_site,"api_key":api_key,"thumbnail_size":thumbnail_size,"threads":threads,
              "grid_width":grid_width,"resize_factor":resize_factor,'preview_width':preview_width
              }


def create_config():

    print("There was an error loading the config, creating a new one")
    with open("config.json", "w") as f:
        json.dump(config_lst, f)
        f.close()

if __name__ == "__main__":

    #Load setup
    config_dir = "config.json"
    if os.path.exists(config_dir):
        with open("config.json", "r") as cnf:
            setup = json.load(cnf)
            cnf.close()


    #apply settings
        loaded_config = list(config_lst.keys())
        if len(setup) == len(config_lst):
            for index in range(len(setup)):
                key = loaded_config[index]
                config_lst[key] = setup[key]
            
        else:
            create_config()
            print(f"error type: {"Config len mismatch"}")

    else:
        create_config()
        print(f"error type: {"FileNotFoundError"}")


    if os.path.exists("cache"):
        pass
    else:
        os.mkdir("cache")

    #Creating window
    wm = windowmanager.WindowManager(name=config_lst["title"],resolution=config_lst["resolution"],
                                     theme=config_lst["theme"], font=config_lst["font"],font_size=config_lst["font_size"],navbar_color=config_lst["navbar_color"],
                                     sidebar_color=config_lst["sidebar_color"],content_color=config_lst["content_color"],text_color=config_lst["text_color"],
                                     button_color=config_lst["button_color"],tag_color=config_lst["tag_color"],preview_color=config_lst["preview_color"],start_url=config_lst["start_url"],
                                     api_key=config_lst["api_key"],thumbnail_size=config_lst["thumbnail_size"],threads=config_lst["threads"],grid_width=config_lst["grid_width"],
                                     resize_factor=config_lst["resize_factor"],preview_width=config_lst["preview_width"])
    wm.get_window().mainloop()




