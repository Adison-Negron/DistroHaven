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
        self.query_object = query.query(start_url,api_key)

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

        #browsing
        self.curpage = 1
        
        self.widget_creator()

        

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
        self.bottombar = tk.Frame(self.sidebar, bg=self.sidebar_color)
        self.bottombar.pack(side="bottom", fill="x",pady=(15,15))
        self.tags_frame.pack(side="top", fill="both")
        

        #sidebar buttons
        button_pad = 1
        self.latest_button = tk.Button(self.category_frame, text="Latest", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color)
        self.latest_button.pack(side="left", fill="x",padx=button_pad)
        self.top_button = tk.Button(self.category_frame, text="Top", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color)
        self.top_button.pack(side="left", fill="x",padx=button_pad) 
        self.random_button = tk.Button(self.category_frame, text="Random", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color)
        self.random_button.pack(side="left", fill="x",padx=button_pad)
        self.hot_button = tk.Button(self.category_frame, text="Hot", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color)
        self.hot_button.pack(side="left", fill="x",padx=button_pad)

        #button calls
        self.latest_button.bind("<Button-1>", self.latest_button_click)
        self.top_button.bind("<Button-1>", self.top_button_click)
        self.random_button.bind("<Button-1>", self.random_button_click)
        self.hot_button.bind("<Button-1>", self.hot_button_click)

        #sidebar tag_entry
        self.search_lbl = tk.Label(self.tags_frame, text="Search:", font=(self.font, self.font_size), bg=self.sidebar_color, fg=self.text_color)
        self.search_lbl.pack(side="top", ipady=5,anchor="w")
        self.search_text = tk.Text(self.tags_frame, font=(self.font, self.font_size), bg=self.tag_color, fg=self.text_color,width=24)
        self.search_text.pack(side="top",expand=True, fill="y",ipady=5)

        #enter button
        self.enter_button = tk.Button(self.tags_frame, text="Enter", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color)
        self.enter_button.pack(side="top", fill="x")
        self.enter_button.bind("<Button-1>", self.search_entry_return)

        #change_page buttons
        self.change_page_frame = tk.Frame(self.tags_frame, bg=self.sidebar_color)
        self.change_page_frame.pack(side="bottom", fill="x")

        self.prev_button = tk.Button(self.change_page_frame, text="Prev", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color)
        self.prev_button.pack(side="left", fill="x")
        self.prev_button.bind("<Button-1>", self.prev_button_click)
        self.next_button = tk.Button(self.change_page_frame, text="Next", font=(self.font, self.font_size), bg=self.button_color, fg=self.text_color)
        self.next_button.pack(side="right", fill="x")
        self.next_button.bind("<Button-1>", self.next_button_click)


        #Preview window
        self.preview_frame = customtkinter.CTkScrollableFrame(self.content,fg_color=self.sidebar_color,width=600)


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
    
    def send_query(self,url,search_dat = None):
        self.clear_query()

        if search_dat is not None:
            query = self.query_object.query(url,self.api_key,search_dat=search_dat)
        else:
            query = self.query_object.query(url,self.api_key)
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
        self.send_query(self.navbar_txt.get(),search_dat=search_dat)
        return

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
            if os.path.exists(f"cache/{elm}"):
                continue
            else:
                os.makedirs(f"cache/{elm}")
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
