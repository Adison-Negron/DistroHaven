import tkinter as tk
import query
import os
import shutil
import threading
import json
from queue import Queue
from PIL import Image, ImageTk
from tkinter import ttk
import customtkinter
from tkinter.filedialog import askdirectory
import webbrowser
from tkinter import messagebox

class WindowManager:
    def __init__(self,name,resolution,theme,font,font_size,navbar_color,sidebar_color,
                 content_color,text_color,button_color,start_url,api_key,tag_color,
                 thumbnail_size,threads,grid_width,resize_factor,preview_color,preview_width):
        self.root = tk.Tk()
        self.name = name
        self.root.title(self.name)
        self.resolution = resolution
        self.theme = theme
        self.root.geometry(self.resolution)
        # self.root.resizable(False, False)

        self.font = font
        self.font_size = font_size
        self.resize_factor = resize_factor
        self.api_key = api_key

        self.query_results = []
        self.start_url = start_url
        self.query_object = query.query(self.start_url,api_key)

        self.thumbnail_size = thumbnail_size
        self.thumbnails_dict = {}
        self.thread_num = threads
        self.thread_list = []
        self.content_images_id = []
        self.content_image_ref = {}
        self.image_references = []


        #Image preview
        self.image_in_preview = []
        self.preview_width = preview_width

        #Category variables
        self.general_switch = customtkinter.StringVar(value=1)
        self.people_switch = customtkinter.StringVar(value=1)
        self.anime_switch = customtkinter.StringVar(value=1)

        #Purity
        self.sfw_switch = customtkinter.StringVar(value=1)
        self.sketchy_switch = customtkinter.StringVar(value=1)
        self.nsfw_switch = customtkinter.StringVar(value=1)


        #Grid
        self.grid_width = grid_width
        self.cur_row = 0
        self.cur_col = 0

        #Navbar

        self.navbar_txt = tk.StringVar()
        self.navbar_txt.set(start_url)

        #Colors
        self.navbar_color = navbar_color
        self.sidebar_color = sidebar_color
        self.content_color = content_color
        self.text_color = text_color
        self.button_color =button_color
        self.tag_color = tag_color
        self.preview_color = preview_color

        self.configs = {
            "navbar_color": self.navbar_color,
            "sidebar_color": self.sidebar_color,
            "content_color": self.content_color,
            "button_color": self.button_color,
            "text_color": self.text_color,
            "tag_color": self.tag_color,
            "preview_color": self.preview_color,
            "font": self.font,
            "font_size": self.font_size

        }

        #browsing
        self.curpage = 1
        
        self.widget_creator()

        #global binds
        self.root.bind("<Left>", self.prev_button_click)
        self.root.bind("<Right>", self.next_button_click)


        self.iconimage = tk.PhotoImage(file="assets/Distrohaven.png")
        self.root.iconphoto(False, self.iconimage)

        

    def widget_creator(self):
        # Frames
        self.navbar = tk.Frame(self.root, height=100, bg=self.navbar_color)
        self.sidebar = tk.Frame(self.root, width=200, bg=self.sidebar_color)
        self.content = tk.Frame(self.root, bg=self.content_color)

        # Layout
        self.navbar.pack(side="top", fill="x")
        self.sidebar.pack(side="left", fill="y")
        self.content.pack(side="left", fill="both", expand=True)


        #Navbar
        self.navbar_entry = tk.Entry(self.navbar,textvariable=self.navbar_txt, font=(self.font, self.font_size), bg=self.navbar_color, fg=self.text_color,width=self.get_window_x())
        self.navbar_entry.pack(side="left", fill="x")
        self.navbar_entry.bind("<Return>", self.navbar_entry_return)
    


        #Content 
        self.content_Frame = customtkinter.CTkScrollableFrame(self.content,fg_color=self.content_color,width=650)
        self.content_Frame.pack(side="left",anchor="w", fill="y", expand=True)

        

        #sidebar
        self.category_frame = tk.Frame(self.sidebar, bg=self.sidebar_color)
        self.tags_frame = tk.Frame(self.sidebar, bg=self.sidebar_color)
        self.category_frame.pack(side="top", fill="x",pady=(5,20))

        self.tags_frame.pack(side="top", fill="both")
        

        #sidebar buttons
        button_pad = 2
        self.latest_button = tk.Button(self.category_frame, text="Latest", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color)
        self.latest_button.pack(side="left", fill="x",padx=button_pad)
        self.top_button = tk.Button(self.category_frame, text="Top", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color,width=7)
        self.top_button.pack(side="left", fill="x",padx=button_pad) 
        self.random_button = tk.Button(self.category_frame, text="Random", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color)
        self.random_button.pack(side="left", fill="x",padx=button_pad)
        self.hot_button = tk.Button(self.category_frame, text="Hot", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color,width=7)
        self.hot_button.pack(side="left", fill="x",padx=button_pad)

        #button calls
        self.latest_button.bind("<Button-1>", self.latest_button_click)
        self.top_button.bind("<Button-1>", self.top_button_click)
        self.random_button.bind("<Button-1>", self.random_button_click)
        self.hot_button.bind("<Button-1>", self.hot_button_click)


        #Category buttons
        self.category_switch_frame = tk.Frame(self.tags_frame, bg=self.sidebar_color)
        self.category_switch_frame.pack(side="top", fill="x")
        self.generalbutton = customtkinter.CTkSwitch(self.category_switch_frame, text="General",font=(self.font, self.font_size),
                                                      bg_color=self.tag_color,fg_color=self.tag_color,variable=self.general_switch, onvalue='1', offvalue='0',state="enabled")
        self.animebutton = customtkinter.CTkSwitch(self.category_switch_frame, text="Anime",font=(self.font, self.font_size),
                                                      bg_color=self.tag_color,fg_color=self.tag_color,variable=self.anime_switch, onvalue='1', offvalue='0',state="enabled")
        self.people_button = customtkinter.CTkSwitch(self.category_switch_frame, text="People",font=(self.font, self.font_size),
                                                      bg_color=self.tag_color,fg_color=self.tag_color,variable=self.people_switch, onvalue='1', offvalue='0',state="enabled")
        
        self.generalbutton.pack(side="left", fill="x",padx=button_pad)
        self.animebutton.pack(side="left", fill="x",padx=button_pad)
        self.people_button.pack(side="left", fill="x",padx=button_pad)


        #Purity buttons
        self.purity_switch_frame = tk.Frame(self.tags_frame, bg=self.sidebar_color)
        self.purity_switch_frame.pack(side="top", fill="x",pady=(5,0))
        self.sfwbutton = customtkinter.CTkSwitch(self.purity_switch_frame, text="SFW",font=(self.font, self.font_size),
                                                      bg_color=self.tag_color,fg_color=self.tag_color,variable=self.sfw_switch, onvalue='1', offvalue='0',state="enabled")  
        self.sketchybutton = customtkinter.CTkSwitch(self.purity_switch_frame, text="Sketchy",font=(self.font, self.font_size),
                                                      bg_color=self.tag_color,fg_color=self.tag_color,variable=self.sketchy_switch, onvalue='1', offvalue='0',state="enabled")
        self.nsfwbutton = customtkinter.CTkSwitch(self.purity_switch_frame, text="NSFW",font=(self.font, self.font_size),
                                                      bg_color=self.tag_color,fg_color=self.tag_color,variable=self.nsfw_switch, onvalue='1', offvalue='0',state="enabled")
        
        #order selector
        self.order_combo_frame = tk.Frame(self.tags_frame, bg=self.sidebar_color)
        self.order_combo_frame.pack(side="top", fill="x",pady=(5,0))
        self.order_combobox = customtkinter.CTkComboBox(self.order_combo_frame, values=["relevance","random","date_added","views","favorites","toplist","hot"],
                                                        font=(self.font, self.font_size),width=100,bg_color=self.tag_color,fg_color=self.tag_color,command=self.order_changed)
        self.order_combobox.set("relevance")


        self.sort_combobox = customtkinter.CTkComboBox(self.order_combo_frame, values=["asc","desc"],
                                                        font=(self.font, self.font_size),width=100,bg_color=self.tag_color,fg_color=self.tag_color)
        self.sort_combobox.set("desc")
        
        self.order_combobox.pack(side="left", fill="x",padx=button_pad)
        self.sort_combobox.pack(side="top", fill="x",padx=button_pad)

        #toplist range 1d 3d 1w 1m 3m 6m 1y

        self.toplist_range_combobox = customtkinter.CTkComboBox(self.tags_frame, values=["1d","3d","1w","1m","3m","6m","1y"],
                                                        font=(self.font, self.font_size),width=100,bg_color=self.tag_color,fg_color=self.tag_color,state="disabled")
        self.toplist_range_combobox.set("1d")

        self.toplist_range_combobox.pack(side="top", fill="x",padx=button_pad,pady=(5,0))


        
        self.sfwbutton.pack(side="left", fill="x",padx=button_pad)
        self.sketchybutton.pack(side="left", fill="x",padx=button_pad)
        self.nsfwbutton.pack(side="left", fill="x",padx=button_pad)

        #reload button 
        self.reload_button = customtkinter.CTkButton(self.tags_frame, text="Reload", font=(self.font, self.font_size),command=self.reload_categories,fg_color=self.button_color)
        self.reload_button.pack(side="top", fill="x",pady=(5,0))

        #sidebar tag_entry
        self.search_lbl = tk.Label(self.tags_frame, text="Search:", font=(self.font, self.font_size), bg=self.sidebar_color, fg=self.text_color)
        self.search_lbl.pack(side="top", ipady=5,anchor="w")
        self.search_text = tk.Text(self.tags_frame, font=(self.font, self.font_size), bg=self.tag_color, fg=self.text_color,width=34)
        self.search_text.pack(side="top",expand=True, fill="y",ipady=5)

        #enter button
        self.enter_button = tk.Button(self.tags_frame, text="Enter", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color)
        self.enter_button.pack(side="top", fill="x")
        self.enter_button.bind("<Button-1>", self.search_entry_return)

        #change_page buttons
        self.change_page_frame = tk.Frame(self.tags_frame, bg=self.sidebar_color)
        self.change_page_frame.pack(side="bottom", fill="x",pady=(5,0))

        self.prev_button = tk.Button(self.change_page_frame, text="Prev", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color,height=5)
        self.prev_button.pack(side="left", fill="both",expand=True)
        self.prev_button.bind("<Button-1>", self.prev_button_click)
        self.next_button = tk.Button(self.change_page_frame, text="Next", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color,height=5)
        self.next_button.pack(side="left", fill="both",expand=True)
        self.next_button.bind("<Button-1>", self.next_button_click)


        #Preview window
        self.preview_frame = customtkinter.CTkScrollableFrame(self.content,fg_color=self.sidebar_color,width=600)

        self.settings_frame = customtkinter.CTkFrame(self.content,fg_color=self.sidebar_color)
        self.settings_frame.pack(side="bottom", fill="x",pady=(5,0))
        self.settings_button = customtkinter.CTkButton(self.settings_frame, text="Settings", font=(self.font, self.font_size),fg_color=self.button_color,command=self.open_settings)
        self.settings_button.pack(side="right", fill="x",padx=button_pad)
    
    def update_colors(self):
        # Update the colors of the widgets
        self.navbar.config(bg=self.navbar_color)
        self.sidebar.config(bg=self.sidebar_color)
        self.content.config(bg=self.content_color)
        self.navbar_entry.config(bg=self.navbar_color, fg=self.text_color)
        self.content_Frame.configure(fg_color=self.content_color)
        self.category_frame.config(bg=self.sidebar_color)
        self.tags_frame.config(bg=self.sidebar_color)
        self.reload_button.configure(fg_color=self.button_color)
        self.search_lbl.config(bg=self.sidebar_color, fg=self.text_color)
        self.enter_button.config(bg=self.button_color, fg=self.text_color)
        self.prev_button.config(bg=self.button_color, fg=self.text_color)
        self.next_button.config(bg=self.button_color, fg=self.text_color)
        self.settings_button.configure(fg_color=self.button_color)
        
        # Update the switches' colors
        for switch in [self.generalbutton, self.animebutton, self.people_button, self.sfwbutton, self.sketchybutton, self.nsfwbutton]:
            switch.configure(bg_color=self.tag_color, fg_color=self.tag_color)

    def open_settings(self, event=None):
        self.content_settings_widgets = []
        self.settings_window = customtkinter.CTkToplevel(self.root)
        self.settings_window.geometry("500x500")
        self.settings_window.title("Settings")
        self.settings_window.resizable(False, False)
        self.settings_window.config(bg=self.sidebar_color)
        self.settings_window.grab_set()


        #Left frame
        self.settings_left_frame = customtkinter.CTkFrame(self.settings_window,fg_color=self.sidebar_color,width=5)
        self.settings_left_frame.pack(side="left", fill="y")

        #Right frame
        self.settings_right_frame = customtkinter.CTkFrame(self.settings_window,fg_color=self.content_color,width=500)
        self.settings_right_frame.pack(side="left", fill="y")

        #Left Buttons
        self.settings_Appearance = customtkinter.CTkButton(self.settings_left_frame, text="Appearance", font=(self.font, self.font_size),fg_color=self.button_color,command=self.open_settings_appearance)
        self.settings_Appearance.pack(side="top", fill="x",pady=(5,0))

        self.Wallhaven_button = customtkinter.CTkButton(self.settings_left_frame, text="Wallhaven", font=(self.font, self.font_size),fg_color=self.button_color,command=self.open_settings_wallhaven)
        self.Wallhaven_button.pack(side="top", fill="x",pady=(5,0))

        self.about_button = customtkinter.CTkButton(self.settings_left_frame, text="Help/About", font=(self.font, self.font_size),fg_color=self.button_color,command=self.open_settings_about)
        self.about_button.pack(side="top", fill="x",pady=(5,0))

    def open_settings_about(self, event=None):
        self.close_content_widgets()

        about_frame = customtkinter.CTkFrame(self.settings_right_frame,fg_color=self.content_color,width=500)
        about_frame.pack(side="top", fill="x",pady=(5,0))

        About_txt = "Distrohaven is an app to browse and save images\n next updates will add commands to: \n 1. edit/set wallpaper through commands\n\n To include/exlude tags in search use: \n and_<tag> \n not_<tag>"

        about_label = customtkinter.CTkLabel(about_frame, text=f"{About_txt}", font=(self.font, self.font_size))
        about_label.pack(side="top", fill="x",pady=(5,0),padx=10,ipadx=20)

        self.content_settings_widgets.append(about_label)
        self.content_settings_widgets.append(about_frame)

        
    def close_content_widgets(self, event=None):
        for widget in self.content_settings_widgets:
            widget.destroy()




    def open_settings_wallhaven(self, event=None):
        def create_setting_row(frame, label_text, default_value):
            """
            Helper function to create a settings row with a label and entry.
            """
            row_frame = customtkinter.CTkFrame(frame, fg_color=self.content_color, width=500)
            row_frame.pack(side="top", pady=(5, 0), padx=5)
            
            label = customtkinter.CTkLabel(row_frame, text=label_text, font=(self.font, self.font_size))
            label.pack(side="left")
            
            entry = customtkinter.CTkEntry(row_frame, font=(self.font, self.font_size))
            entry.pack(side="left",fill="x")
            entry.insert(0, default_value)
            self.content_settings_widgets.extend([row_frame, label, entry])
            
            return row_frame, label, entry

        self.close_content_widgets()

        # Define setting labels and corresponding default values
        settings = [
            ("API Key: ", self.api_key),
            ("Number of Threads: ", self.thread_num)
        ]

        # Dictionary to store the entry widgets
        self.setting_entries = {}

        # Create rows dynamically
        for setting in settings:
            _, _, entry1 = create_setting_row(self.settings_right_frame, setting[0], setting[1])
            # Store entries in the dictionary with the label as the key
            setting_name = setting[0].split(":")[0].strip()
            self.setting_entries[setting_name] = entry1

        # Save Button
        def save_wallhaven_settings():
            # Update the api_key and thread_num variables
            self.api_key = self.setting_entries["API Key"].get()
            self.thread_num = int(self.setting_entries["Number of Threads"].get())
            print(f"API Key: {self.api_key}")
            print(f"Number of Threads: {self.thread_num}")

            self.nsfwbutton.configure(state="normal")
            self.sketchybutton.configure(state="normal")
            self.nsfw_switch.set(1)
            self.sketchy_switch.set(1)
            messagebox.showinfo("Saved settings", "Note: If API Key is wrong you will not get any NSWF or Sketchy results at all.\n If during search you get no results, check your API Key and try again.")
            self.save_wallhaven()
            # Add any additional actions for saving here (e.g., saving to a file or applying changes)

        save_button = customtkinter.CTkButton(
            self.settings_right_frame, 
            text="Save", 
            font=(self.font, self.font_size), 
            command=save_wallhaven_settings,
            fg_color=self.button_color
        )
        save_button.pack(side="bottom", anchor="se",pady=10, padx=10)
        self.content_settings_widgets.append(save_button)
        




    def open_settings_appearance(self, event=None):
        def create_setting_row(frame, label_text, default_value, is_double_entry=False, second_default_value=None):
            """
            Helper function to create a settings row with a label and entry.
            Allows for double-entry rows if specified.
            """
            row_frame = customtkinter.CTkFrame(frame, fg_color=self.content_color, width=500)
            row_frame.pack(side="top", pady=(5, 0), padx=5)
            
            label = customtkinter.CTkLabel(row_frame, text=label_text, font=(self.font, self.font_size))
            label.pack(side="left")
            
            entry1 = customtkinter.CTkEntry(row_frame, font=(self.font, self.font_size))
            entry1.pack(side="left")
            entry1.insert(0, default_value)
            self.content_settings_widgets.extend([row_frame, label, entry1])

            if is_double_entry:
                entry2 = customtkinter.CTkEntry(row_frame, font=(self.font, self.font_size))
                entry2.pack(side="left", padx=(5, 0))
                if second_default_value is not None:
                    entry2.insert(0, second_default_value)
                self.content_settings_widgets.append(entry2)
                return row_frame, label, entry1, entry2

            return row_frame, label, entry1

        self.close_content_widgets()

        # Define setting labels and corresponding default values
        settings = [
            ("Window Size: ", self.resolution),
            ("Font Size: ", self.font, self.font_size),  # Add second value for double-entry rows
            ("Navbar Color: ", self.navbar_color),
            ("Sidebar Color: ", self.sidebar_color),
            ("Content Color: ", self.content_color),
            ("Text Color: ", self.text_color),
            ("Button Color: ", self.button_color),
            ("Tag Color: ", self.tag_color),
            ("Preview Color: ", self.preview_color),
        ]

        # Dictionary to store the entry widgets
        self.setting_entries = {}

        # Create rows dynamically
        for setting in settings:
            if setting[0] == "Font Size: ":
                # Create double-entry row for font and font size
                _, _, font_entry, font_size_entry = create_setting_row(
                    self.settings_right_frame, setting[0], setting[1], is_double_entry=True, second_default_value=setting[2]
                )
                # Store entries in the dictionary
                self.setting_entries["Font"] = font_entry
                self.setting_entries["Font Size"] = font_size_entry
            else:
                _, _, entry1 = create_setting_row(self.settings_right_frame, setting[0], setting[1])
                # Store entries in the dictionary with the label as the key
                setting_name = setting[0].split(":")[0].strip()
                self.setting_entries[setting_name] = entry1

        # Add Save Button at the Bottom
        save_button = customtkinter.CTkButton(
            self.settings_right_frame, 
            text="Save", 
            font=(self.font, self.font_size), 
            command=self.save_config,
            fg_color=self.button_color
        )
        save_button.pack(side="bottom",anchor="se", pady=10, padx=10)
        self.content_settings_widgets.append(save_button)

    def get_setting_widget(self, setting_name):
        """
        Get the value of a setting by its name.
        """
        entry_widget = self.setting_entries.get(setting_name)
        if entry_widget:
            return entry_widget
        return None
    

    def save_wallhaven(self):
        config = {
            "title": "Distrohaven",
            "resolution": self.resolution,
            "theme": self.theme,
            "debug": False,
            "font": self.font,
            "font_size": self.font_size,
            "navbar_color": self.navbar_color,
            "sidebar_color": self.sidebar_color,
            "content_color": self.content_color,
            "text_color": self.text_color,
            "button_color": self.button_color,
            "tag_color": self.tag_color,
            "preview_color": self.preview_color,
            "start_url": self.start_url,
            "api_key": self.api_key,
            "thumbnail_size": self.thumbnail_size,
            "threads": self.thread_num,
            "grid_width": self.grid_width,
            "resize_factor": self.resize_factor,
            "preview_width": self.preview_width,
        }

        # Define the path to save the configuration file
        config_path = "config.json"  # Adjust the path if needed

        try:
            # Write the configuration dictionary to the JSON file
            with open(config_path, "w") as config_file:
                json.dump(config, config_file, indent=4)
            print("Wallhaven configuration saved successfully!")
        except Exception as e:
            print(f"Failed to save Wallhaven configuration: {e}")



    def save_config(self):
        """
        Save the current settings of the application to a JSON file.
        """
        #Save values from entries

        #Check for proper values
        if not self.get_setting_widget("Font Size").get().isdigit():
            messagebox.showerror("Error", "Font Size must be a number")
            return
        
        #Check all the colors match required length and have a # at start
        if any(len(color) != 7 or color[0] != "#" for color in [self.get_setting_widget("Navbar Color").get(),
                                                               self.get_setting_widget("Sidebar Color").get(),
                                                               self.get_setting_widget("Content Color").get(),
                                                               self.get_setting_widget("Text Color").get(),
                                                               self.get_setting_widget("Button Color").get(),
                                                               self.get_setting_widget("Tag Color").get(),
                                                               self.get_setting_widget("Preview Color").get()]):
            messagebox.showerror("Error", "All colors must be in the format #RRGGBB")
            return
        

        self.resolution =self.get_setting_widget("Window Size").get()
        self.font = self.get_setting_widget("Font").get()
        self.font_size = int(self.get_setting_widget("Font Size").get())
        self.navbar_color = self.get_setting_widget("Navbar Color").get()
        self.sidebar_color = self.get_setting_widget("Sidebar Color").get()
        self.content_color = self.get_setting_widget("Content Color").get()
        self.text_color = self.get_setting_widget("Text Color").get()
        self.button_color = self.get_setting_widget("Button Color").get()
        self.tag_color = self.get_setting_widget("Tag Color").get()
        self.preview_color = self.get_setting_widget("Preview Color").get()

        # Create a dictionary with the current configuration
        config = {
            "title": "Distrohaven",
            "resolution": self.resolution,
            "theme": self.theme,
            "debug": False,
            "font": self.font,
            "font_size": self.font_size,
            "navbar_color": self.navbar_color,
            "sidebar_color": self.sidebar_color,
            "content_color": self.content_color,
            "text_color": self.text_color,
            "button_color": self.button_color,
            "tag_color": self.tag_color,
            "preview_color": self.preview_color,
            "start_url": self.start_url,
            "api_key": self.api_key,
            "thumbnail_size": self.thumbnail_size,
            "threads": self.thread_num,
            "grid_width": self.grid_width,
            "resize_factor": self.resize_factor,
            "preview_width": self.preview_width,
        }

        # Define the path to save the configuration file
        config_path = "config.json"  # Adjust the path if needed

        try:
            # Write the configuration dictionary to the JSON file
            with open(config_path, "w") as config_file:
                json.dump(config, config_file, indent=4)
            print("Configuration saved successfully!")
            self.update_colors()
        except Exception as e:
            print(f"Failed to save configuration: {e}")
    def reload_categories(self, event=None):
        category_data = self.get_category_data()
        self.send_query(self.navbar_txt.get(),category_dat=category_data)
        return

    def order_changed(self, event):
        if event == "toplist":
            self.toplist_range_combobox.configure(state="normal")
        else:
            self.toplist_range_combobox.configure(state="disabled")
            self.toplist_range_combobox.set("1d")

        return




    def prev_button_click(self, event):
        try:            
            numberpos = self.navbar_txt.get().find("page=")
            if numberpos == -1:
                self.send_page_query(self.navbar_txt.get())
            else:
                numberpos = self.navbar_txt.get().find("page=")+5
            apikeypos = self.navbar_txt.get().find("&apikey=")
            if apikeypos == -1:
                self.curpage = int(self.navbar_txt.get()[numberpos:])
            
            else:

                self.curpage = int(self.navbar_txt.get()[numberpos:apikeypos])
            if self.curpage == 1:
                return
            self.navbar_txt.set(self.navbar_txt.get().replace(f"page={self.curpage}",f"page={self.curpage-1}"))
            self.send_page_query(self.navbar_txt.get())
            self.curpage -= 1

            return
        except:
            print("error with previous page")
            return
        
    def next_button_click(self, event):
        try:
            numberpos = self.navbar_txt.get().find("page=")
            if numberpos == -1:
                self.send_page_query(self.navbar_txt.get())
            else:
                numberpos = self.navbar_txt.get().find("page=")+5
            apikeypos = self.navbar_txt.get().find("&apikey=")
            if apikeypos == -1:
                self.curpage = int(self.navbar_txt.get()[numberpos:])
            
            else:

                self.curpage = int(self.navbar_txt.get()[numberpos:apikeypos])
            
            self.navbar_txt.set(self.navbar_txt.get().replace(f"page={self.curpage}",f"page={self.curpage+1}"))
            self.send_page_query(self.navbar_txt.get())
            self.curpage += 1
            return
        
        except:
            return        

    def clear_query(self):
        self.query_results = []
        return

    #button calls
    def latest_button_click(self, event):
        url = "https://wallhaven.cc/api/v1/search?/latest?page=1"
        self.send_query(url)
        return
    
    def top_button_click(self, event):
        url = "https://wallhaven.cc/api/v1/search?sorting=toplist&page=1"
        self.send_query(url)
        return
    
    def random_button_click(self, event):
        url = "https://wallhaven.cc/api/v1/search?sorting=random&page=1"
        self.send_query(url)
        return
    
    def hot_button_click(self, event):
        url = "https://wallhaven.cc/api/v1/search?sorting=hot&page=1"
        self.send_query(url)
        return
    
    def api_check(self):
        if self.api_key == "":
            self.nsfw_switch.set(0)
            self.nsfwbutton.configure(state="disabled")
            self.sketchy_switch.set(0)
            self.sketchybutton.configure(state="disabled")

            messagebox.showwarning("Warning", "No API key provided. Disabling NSFW and Sketchy options. Go to settings, Wallhaven and enter API key to enable them.")
        return
    
    def send_query(self,url,search_dat = None,category_dat = None):
        self.api_check()
        self.clear_query()
        
        if search_dat is not None:
            query = self.query_object.query(url,self.api_key,search_dat=search_dat,category_dat=category_dat)


        else:
            self.get_category_data()
            query = self.query_object.query(url,self.api_key,category_dat=category_dat)
        self.query_results = query
        self.navbar_txt.set(self.query_results[0])
        print(self.query_results[0])
        self.display_query()
        return query
    
    def send_page_query(self,url):
        self.clear_query()
        query = self.query_object.page_search(url)
        self.query_results = query
        self.navbar_txt.set(self.query_results[0])
        self.display_query()
        print(self.query_results[0])
        return

    def attach_image(self,image_path,resolution,elm_id):
        
        image = Image.open(image_path)
        resolution = resolution.split("x")
        new_width = int(self.resize_factor)
        new_height = int(self.resize_factor)
        # image = image.resize((new_width,new_height),resample=Image.Resampling.LANCZOS)
        
        # image = ImageTk.PhotoImage(image)

        customimage = customtkinter.CTkImage(dark_image=image, light_image=image, size=(new_width,new_height))
        customlabel = customtkinter.CTkLabel(self.content_Frame,text=f"{elm_id}",image=customimage,
                                             font=(self.font, 1),bg_color=self.content_color,
                                             fg_color=self.text_color,anchor='s',justify='left'
                                             )
        customlabel.grid(row=self.cur_row, column=self.cur_col, padx=5, pady=5)
        customlabel.bind("<Button-1>", self.on_image_click)
        self.image_references.append(customlabel.get_tkinter_label())

        # Keep a reference to the label for clearing it afterwards

        self.cur_col += 1
        if self.cur_col >= self.grid_width:
            self.cur_col = 0
            self.cur_row += 1

        self.image_references.append(customlabel)
        return 
    
    def on_image_click(self, event):
        label = event.widget
        label_id = label['text']
        print(label_id)

        if len(self.image_in_preview)>0:
            if os.path.exists(self.image_in_preview[1]):
                self.preview_label.destroy()
                self.resolution_label.destroy()
                self.preview_image_filesize.destroy()
                self.preview_image_category.destroy()
                self.preview_button_frame.destroy()
                self.savebutton.destroy()
                self.visit_site_button.destroy()

                # os.remove(self.image_in_preview[1])
                
            self.image_in_preview = []

        self.preview_frame.pack(side="left",anchor="w", fill="both", expand=True)

        selected_image_info = self.query_results[1].get(label_id)
        preview_image_name = selected_image_info['path'].split('/')[-1]
        preview_image_location = f"cache/{label_id}/{preview_image_name}"
        preview_image_path = selected_image_info['path']
        preview_ratio = float(selected_image_info['ratio'])
        preview_thread = threading.Thread(self.query_object.get_thumbnail(preview_image_path,preview_image_location), args=(10,))
        preview_thread.start()
        preview_thread.join()
        self.image_in_preview = (preview_thread,preview_image_location)

        
        new_size = (self.preview_width,int(self.preview_width/preview_ratio))
        tkinter_image = customtkinter.CTkImage(light_image=Image.open(preview_image_location), dark_image=Image.open(preview_image_location),size=new_size)
        self.preview_label = customtkinter.CTkLabel(self.preview_frame,image=tkinter_image,text="")
        self.preview_label.pack(side="top")

        self.resolution_label = customtkinter.CTkLabel(self.preview_frame,text=f"Resolution: {selected_image_info['resolution']}",font=(self.font, self.font_size),width=100)
        self.resolution_label.pack(side="top")

        self.preview_image_filesize = customtkinter.CTkLabel(self.preview_frame,text=f"File Size: {selected_image_info['file_size'] } bytes",font=(self.font, self.font_size),width=100)
        self.preview_image_filesize.pack(side="top")

        self.preview_image_category = customtkinter.CTkLabel(self.preview_frame,text=f"Category: {selected_image_info['category']}",font=(self.font, self.font_size),width=100)
        self.preview_image_category.pack(side="top")

 
        self.preview_button_frame = tk.Frame(self.preview_frame,bg=self.content_color)
        self.preview_button_frame.pack(side="top")
        self.savebutton = customtkinter.CTkButton(self.preview_button_frame,text="Save",font=(self.font, self.font_size),width=100,fg_color=self.button_color)
        self.savebutton.pack(side="left",padx=(0,5))
        self.savebutton.bind("<Button-1>", lambda event: self.save_button_click(event,preview_image_location,preview_image_name))

        self.visit_site_button = customtkinter.CTkButton(self.preview_button_frame,text="Visit Site",font=(self.font, self.font_size),width=100,fg_color=self.button_color)
        self.visit_site_button.pack(side="left")
        self.visit_site_button.bind("<Button-1>", lambda event: self.visit_site_button_click(event,selected_image_info['url']))
        return
    

    def visit_site_button_click(self, event,url):
        webbrowser.open(url)
        return
    def save_button_click(self, event,img_location,img_name):
        directory = askdirectory()
        shutil.copyfile(img_location,directory+"/"+img_name)
        return 


    def clear_content(self):
        return 1
    

    def get_window_x(self):
        return self.root.winfo_reqwidth()
    def get_window_y(self):
        return self.root.winfo_reqheight()

    def search_entry_return(self, event):
        search_dat = self.search_text.get("1.0",tk.END)
        self.category_dat = self.get_category_data()
        self.send_query(self.navbar_txt.get(),search_dat=search_dat,category_dat=self.category_dat)
        return
    
    def get_category_data(self):
        self.category_dat = {}
        self.category_dat['category'] = [int(self.general_switch.get()),int(self.anime_switch.get()),int(self.people_switch.get())]
        self.category_dat['purity'] = [int(self.sfw_switch.get()),int(self.sketchy_switch.get()),int(self.nsfw_switch.get())]
        self.category_dat['order'] = self.order_combobox.get()
        self.category_dat['sort'] = self.sort_combobox.get()
        self.category_dat['range'] = self.toplist_range_combobox.get()

        
        return self.category_dat

    def navbar_entry_return(self, event):
        self.send_query(self.navbar_txt.get())
        return

    def update_navbar_text(self, text):
        self.navbar_txt.set(text)
        return

    def get_window(self):
        self.navbar_entry.config(width=self.get_window_x())
        return self.root
    
    def redraw(self):
        self.root.update()
    
    def wipe_cache(self):
        if os.path.exists("cache"):
            try:
                shutil.rmtree("cache")
                os.mkdir("cache")
            except:
                pass


        if len(self.image_references) > 0:
            for elm in self.image_references:
                elm.destroy()

        #reset grid
        self.cur_row = 0
        self.cur_col = 0

        for label in self.image_references:
            label.destroy()
        return

    def display_query(self):
        self.thumbnails_dict = {}
        self.thread_list = []
        self.queue = Queue()  # Create a queue for the image URLs and their names
        self.wipe_cache()

        # Prepare the cache directories and populate the thumbnails dictionary
        for elm in self.query_results[1]:
            
            os.makedirs(f"cache/{elm}") if not os.path.exists(f"cache/{elm}") else None
            img_details = self.query_results[1][elm]
            thumbnail_link = img_details['thumbs'][self.thumbnail_size]
            thumbnail_id = img_details['id']
            thumbnail_name = thumbnail_link.split('/')[-1]
            thumbnail_resolution = img_details['resolution']
            self.thumbnails_dict[thumbnail_id] = [thumbnail_link, thumbnail_name,thumbnail_resolution]

        # Add the URLs and names to the queue
        for thumbnail_id in self.thumbnails_dict:
            thumbnail_url = self.thumbnails_dict[thumbnail_id][0]
            thumbnail_name = self.thumbnails_dict[thumbnail_id][1]
            thumbnail_folder = thumbnail_name[:-4]
            thumbnail_output = f"cache/{thumbnail_folder}/{thumbnail_name}"
            self.thumbnails_dict[thumbnail_id] = [thumbnail_url, thumbnail_name,thumbnail_output,thumbnail_resolution]
            self.queue.put((thumbnail_url, thumbnail_output))

        # Worker function for downloading thumbnails
        def worker():
            while not self.queue.empty():
                try:
                    # Get a URL and name from the queue
                    thumbnail_url, thumbnail_path = self.queue.get_nowait()
                    # Call the query object's method to download the thumbnail
                    self.query_object.get_thumbnail(thumbnail_url, thumbnail_path)
                except Exception as e:
                    print(f"Error downloading thumbnail: {e}")
                finally:
                    # Signal that the task is done
                    self.queue.task_done()

        # Create and start threads
        for _ in range(self.thread_num):
            thread = threading.Thread(target=worker)
            self.thread_list.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in self.thread_list:
            thread.join()

        self.clear_content()
        # Display the thumbnails on the GUI
        for elm in self.thumbnails_dict:
            resolution = self.thumbnails_dict[elm][3]
            absolute_path = os.path.abspath(self.thumbnails_dict[elm][2])
            self.attach_image(absolute_path,resolution,elm_id= elm)

        return
    


class GUIchild(tk.Frame):
    def __init__(self, parent,name):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.name = name
        self.root.title(self.name)

    def redraw(self):
        self.root.update()

    def get_child(self):
        return self
