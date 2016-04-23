#! python 3
# coding=UTF-8

"""
Lautaloader. Distributed via https://github.com/lautaloader/lloader/
Do not redistribute.
MIT license holds where applicable.
For free non-commercial, non-harmful use only.
User is responsible for content downloaded with the help of this program.
Ylilauta is responsible for content on their website.
User has read the licensing terms and agreed to them by using this program.
Have fun.
"""

# TODO: youtube links generate 2x "ignored" at once
# TODO: stuff could be done with regular expressions

from tkinter import (Button, Checkbutton, DISABLED, E, Entry, END, FALSE,
                     filedialog, IntVar, Label, LabelFrame, NORMAL,
                     Radiobutton, StringVar, Tk, W)
import os
import requests
import bs4
import random
import configparser
from urllib.parse import urlparse

config = configparser.ConfigParser()


class Main:
    def __init__(self, master):  # we will define everything in the UI below
        self.master = master
        self.master.wm_title("Lautaloader v.1.00")  # title of window
        self.master.resizable(width=FALSE, height=FALSE)  # window is not resizable
        self.master.geometry('420x230')  # resolution of the window in pixels

        self.r_selection = IntVar()  # these are radiobuttons and checkbuttons
        self.c1_selection = IntVar()
        self.c2_selection = IntVar()
        self.c1_selection.set(0)  # checkbuttons will be off at launch
        self.c2_selection.set(0)
        self.r_selection.set(1)  # we need one radiobutton selected at start

        self.status_text = StringVar()  # status text is visible at the bottom of GUI
        self.status_text.set('Ready to work')  # we can (and will) set the status text like this
        self.save_folder = ''  # we will save into this folder
        self.filenames = []  # this is our folder filenames list
        self.url_text = StringVar()
        self.num_pics = 0
        self.num_mp4 = 0
        self.num_mp3 = 0
        self.num_ign = 0
        self.image_url = ''
        self.name_of_file = ''
        self.res = ''
        self.imagefile = ''
        self.filesize = ''
        self.maxfilesize = 25.0  # in MB. Known issue: mp4 not returning file size.
        self.imagewritten = False
        self.read_timeout = 1.0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
            'Referer': '',
            'DNT': '1',
            'Accept-Language': 'fi-FI,fi;q=0.8,en-US;q=0.6,en;q=0.4',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

        self.lf = LabelFrame(master, text=' Get ')
        self.lf.grid(row=1, column=1, rowspan=4)

        self.lf2 = LabelFrame(master, text=' Options ')
        self.lf2.grid(row=1, column=2)

        self.R1 = Radiobutton(self.lf, text="All", variable=self.r_selection, value=1)
        self.R1.grid(row=1, column=1, sticky=W)

        self.R2 = Radiobutton(self.lf, text="only img", variable=self.r_selection, value=2)
        self.R2.grid(row=2, column=1, sticky=W)

        self.R3 = Radiobutton(self.lf, text="only mp4", variable=self.r_selection, value=3)
        self.R3.grid(row=3, column=1, sticky=W)

        self.R4 = Radiobutton(self.lf, text="only mp3", variable=self.r_selection, value=4)
        self.R4.grid(row=4, column=1, sticky=W)

        self.C1 = Checkbutton(self.lf2, text="Create new filenames", variable=self.c1_selection,
                              state=NORMAL, onvalue=1, offvalue=0)
        self.C1.grid(row=1, column=2, sticky=W)

        self.C2 = Checkbutton(self.lf2, text="Overwrite if found", variable=self.c2_selection,
                              state=NORMAL, onvalue=1, offvalue=0)
        self.C2.grid(row=2, column=2, sticky=W)

        self.folder_label = Label(master, text="Folder: ")
        self.folder_label.grid(row=5, sticky=E)

        self.url_label = Label(root, text="URL: ")
        self.url_label.grid(row=6, sticky=E)

        self.folder_entry = Entry(master, textvariable=self.save_folder, state="readonly", width=50)
        self.folder_entry.grid(row=5, column=1, columnspan=2)

        self.url_entry = Entry(master, textvariable=self.url_text, width=50)
        self.url_entry.grid(row=6, column=1, columnspan=2)

        self.selectbutton = Button(master, text="Select..", state=NORMAL, command=self.get_folder)
        self.selectbutton.grid(row=5, column=3, sticky=W)

        self.openfolderbutton = Button(master, text="Open folder", state=DISABLED, command=self.openfolder)
        self.openfolderbutton.grid(row=3, column=2, sticky=W, padx=22)

        self.urlbutton = Button(master, text="Download", state=DISABLED, command=self.logic)
        self.urlbutton.grid(row=6, column=3, sticky=W)

        self.status = Label(master, textvariable=self.status_text, wraplength=350)
        self.status.grid(row=8, sticky=W, columnspan=3)

        self.manage_config()

        if self.save_folder != '':  # if save folder is not empty, we probably have a valid folder
            self.urlbutton['state'] = 'normal'   # so we can enable urlbutton already
            self.openfolderbutton['state'] = 'normal'  # and we can also enable open folder button

    def manage_config(self):
        if not os.path.isfile(os.path.expanduser("~\\documents\\lloader_cfg.ini")):
            with open((os.path.expanduser("~\\documents\\lloader_cfg.ini")), 'w') as cfgfile:
                config.add_section('basic_config')  # cfg file not exists so we make it
                config.set('basic_config', 'save_folder', self.save_folder)
                config.write(cfgfile)
        else:
            try:
                config.read(os.path.expanduser('~\\documents\\lloader_cfg.ini'))
                self.folder_entry['state'] = 'normal'  # make the folder field writable
                self.folder_entry.delete(0, END)
                self.save_folder = config.get('basic_config', 'save_folder')  # get save folder from file
                self.folder_entry.insert(0, self.save_folder)  # write to folder field
                self.folder_entry['state'] = 'readonly'  # make it read-only again

            except (IOError, OSError) as e:
                print(e)
            except configparser.MissingSectionHeaderError:  # correct section not found from file
                os.remove(os.path.expanduser("~\\documents\\lloader_cfg.ini"))
                self.manage_config()  # delete file and try to create it from start

    def get_folder(self):
        dir_opt = options = {}  # define options for get folder function
        options['initialdir'] = self.save_folder
        options['mustexist'] = False
        options['parent'] = self.master
        options['title'] = 'Choose a directory'

        self.save_folder = filedialog.askdirectory(**dir_opt)  # actual function to get the folder name
        with open((os.path.expanduser("~\\documents\\lloader_cfg.ini")), 'w') as cfgfile:
            config.set('basic_config', 'save_folder', self.save_folder)
            config.write(cfgfile)  # write new save folder to config file

        self.folder_entry['state'] = 'normal'  # make the folder field writable
        self.folder_entry.delete(0, END)
        self.folder_entry.insert(0, self.save_folder)  # update folder field
        self.folder_entry['state'] = 'readonly'  # make it read-only again

        self.clear_savefolder_list()

        self.openfolderbutton['state'] = 'normal'  # we can now press the open folder and url buttons
        self.urlbutton['state'] = 'normal'  # because we have defined a save folder

    def openfolder(self):
        os.startfile(self.save_folder)  # opens the save folder

    def clear_savefolder_list(self):
        del self.filenames[:]  # clears the list of files in a folder
        self.filenames.append(next(os.walk(self.save_folder))[2])  # adds every file in folder to list

    def check_for_url(self):
        parse = urlparse(self.url_texti.lower())  # checks if url is ylilauta
        if (parse.netloc.startswith("www.ylilauta.org") or
                parse.netloc.startswith("ylilauta.org")):
            return True
        else:
            return False

    def is_image(self):
        if (self.image_url.lower().endswith(".jpg") or
                self.image_url.lower().endswith(".jpeg") or
                self.image_url.lower().endswith(".png")):  # link seems to be image
            return True
        else:
            return False

    def is_mp4(self):
        if self.image_url.lower().endswith(".mp4"):  # link ends in mp4 so its mp4
            return True
        else:
            return False

    def is_mp3(self):
        if self.image_url.lower().endswith(".mp3"):  #link ends in mp3 so its mp3
            return True
        else:
            return False

    def we_want_it_anyway(self):
        if self.c2_selection.get() == 1:  # checkbutton2 is selected so we want all files
            return True
        else:
            return False

    def getting_both(self):
        if self.r_selection.get() == 1:  # first radio button is selected so dl both
            return True
        else:
            return False

    def getting_img(self):
        if self.r_selection.get() == 2:  # second radio button is selected so dl images only
            return True
        else:
            return False

    def getting_mp4(self):
        if self.r_selection.get() == 3:  # third radio button is selected so dl mp4 only
            return True
        else:
            return False

    def getting_mp3(self):
        if self.r_selection.get() == 4:  # fourth radio button is selected so we get mp3 only
            return True
        else:
            return False

    def rename_file(self):
        get_filetype = os.path.splitext(os.path.basename(self.image_url))[1]  # get filetype
        new_file_name_start = ''

        for i in range(0, 15):
            new_file_name_start += str(random.randint(0, 9))  # create random string of numbers

        self.name_of_file = (new_file_name_start + get_filetype)  # create the whole new name

    def write_file(self):
        self.res = requests.get(self.image_url)
        self.res.raise_for_status()
        try:
            with open(os.path.join(self.save_folder,
                                   self.name_of_file), 'wb') as self.imagefile:
                for chunk in self.res.iter_content(100000):
                    self.imagefile.write(chunk)
            self.imagewritten = True
        except IOError as e:
            print(e)
            self.status_text.set('File error %s' % e)
            self.master.update()

        self.status_text.set('Downloading %s' % self.name_of_file)
        print('Downloading %s' % self.name_of_file)
        self.master.update()

    def file_get_logic(self):
        self.clear_savefolder_list()  # need to update this list between files
        self.imagewritten = False  # need to change this here because if same thread has same pictures
        if self.c1_selection.get() == 1:  # if want new random name
                self.rename_file()
        else:
            self.name_of_file = os.path.basename(self.image_url)  # using default filename

        if self.name_of_file in self.filenames[0]:  # file exists
            if self.c2_selection.get() == 1:  # we want to overwrite
                self.write_file()
            else:
                self.num_ign += 1  # ignored a file

        elif self.name_of_file not in self.filenames[0]:  # file does not exist in folder
            self.write_file()  # so we take it in

        self.master.update()

    def connect_logic(self):
        try:
            self.res = requests.get(self.url_texti, headers=self.headers,
                                    timeout=(10.0, self.read_timeout))
            self.res.raise_for_status()
        except (requests.exceptions.ReadTimeout, requests.exceptions.HTTPError) as e:
            print(e)
            self.status_text.set("Network error %s" % self.res.status_code)
            self.master.update()

    def get_file_size(self):
            self.filesize = int(requests.head(self.image_url).headers['Content-Length'])
            self.filesize = ((self.filesize / 1024) / 1024)  # convert
            if self.filesize <= self.maxfilesize:
                return True
            else:
                return False

    def logic(self):
        self.clear_savefolder_list()
        self.num_pics = 0  # make these 0 because we just called the function
        self.num_mp4 = 0
        self.num_mp3 = 0
        self.num_ign = 0
        self.imagewritten = False
        self.url_texti = ''
        done = False

        if self.url_text != '':
            self.url_texti = (self.url_text.get())  # if url text is not empty we will set it to variable

        if self.check_for_url() is False or not self.url_text:  # if url is wrong or empty
            self.status_text.set('URL not supported')

        while not done and self.check_for_url() is True:
            self.urlbutton['state'] = 'disabled'  # disable buttons so they cant be pressed while run
            self.selectbutton['state'] = 'disabled'  # we will enable them again in the end
            self.R1['state'] = 'disabled'
            self.R2['state'] = 'disabled'
            self.R3['state'] = 'disabled'
            self.R4['state'] = 'disabled'
            self.C1['state'] = 'disabled'
            self.C2['state'] = 'disabled'
            self.url_entry['state'] = 'readonly'

            self.status_text.set(("%s" % self.url_texti))

            self.connect_logic()

            soup = bs4.BeautifulSoup(self.res.text, 'html.parser')  # create soup

            for imglink in soup.select(".filecontainer figcaption a"):
                try:
                    self.image_url = 'http:' + imglink.get('href')
                    print(self.image_url)
                except requests.exceptions.InvalidSchema as e:
                    print("Skipping Naamapalmu or Youtube, ", e)
                if (self.is_image() and self.get_file_size() and
                        (self.getting_img() or
                            self.getting_both())):  # if we found an image
                    self.file_get_logic()
                    if self.imagewritten:
                        self.num_pics += 1

                elif (self.is_mp4() and self.get_file_size() and
                        (self.getting_mp4() or
                            self.getting_both())):  # we found mp4
                    self.file_get_logic()
                    if self.imagewritten:
                        self.num_mp4 += 1

                elif (self.is_mp3() and self.get_file_size() and
                        (self.getting_mp3() or
                            self.getting_both())):  # we found mp3
                    self.file_get_logic()
                    if self.imagewritten:
                        self.num_mp3 += 1

                else:
                    print("ignored: ", self.image_url)
                    self.num_ign += 1  # file was too big or something went wrong and we ignored it

            self.status_text.set('Downloaded %s images, %s mp4, %s mp3. %s ignored' % (self.num_pics,
                                                                                       self.num_mp4,
                                                                                       self.num_mp3,
                                                                                       self.num_ign))
            self.urlbutton['state'] = 'normal'
            self.url_entry['state'] = 'normal'
            self.selectbutton['state'] = 'normal'
            self.R1['state'] = 'normal'
            self.R2['state'] = 'normal'
            self.R3['state'] = 'normal'
            self.R4['state'] = 'normal'
            self.C1['state'] = 'normal'
            self.C2['state'] = 'normal'  # we have enabled all buttons to be used again
            print("DONE")

            break

root = Tk()
Main(root)
root.mainloop()
