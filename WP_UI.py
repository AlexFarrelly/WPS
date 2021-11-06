try:
    from tkinter import * 
    from tkinter import font
    from tkinter import ttk
    from tkinter import filedialog
    import tkinter as tk
    from tkinter.ttk import Progressbar
    from threading import Thread
    from tkcalendar import Calendar, DateEntry
    
    from threading import Thread
    import csv, math, fitz
    from App_Package import *
    from concurrent.futures import ThreadPoolExecutor as TPE 

except:
    raise NotImplementedError("Libarys Not Installed")

class mainPage:
    def __init__(self):
        UI = tk.Tk()
        self.UI = UI
        UI.title("Wastage Predictor")
        width = UI.winfo_screenwidth()
        height = UI.winfo_screenheight()
        UI.geometry("%dx%d" % (width, height))
        selectionFrame(UI), controlFrame(UI), displayFrame(UI), uploadFrame(UI)

    def refresh(self, frame):
        frame.destroy()
        self.__init__(self.UI)

    def show_predicted_values(self):
        self.refresh(displayFrame)
        
    

class selectionFrame(mainPage):
    def __init__(self, UI):
        self.UI = UI
        topLeftFrame = tk.Frame(UI)
        self.topLeftFrame = topLeftFrame
        self.getItems()
        self.createLabels(topLeftFrame)
        self.createButtons(topLeftFrame)
        self.createEntryBoxes(topLeftFrame)
        topLeftFrame.grid(row = 1, column = 0)

    def getItems(self):
        self.itemList = []
        with open("App_Package/saved_data/PastryIndex.csv", "r", newline = "") as pastryFile:
            reader = csv.reader(pastryFile)
            for row in reader:
                value = (str(row).strip("[]")).strip("''")
                self.itemList.append(value)
        global itemList
        itemList = self.itemList
        
    def createButtons(self, topLeftFrame):
        btnFont = font.Font(family="Helvetica",size=15)
        predictButton = tk.Button(topLeftFrame, text = "Predict Wastage", command = lambda: (self.getCheckValues),
                                  font = btnFont, relief = FLAT, activeforeground = "gold", activebackground = "black")
        addButton = tk.Button(topLeftFrame, text = "Add Item", command = self.addItem,
                              font = btnFont, relief = FLAT)
        removeButton = tk.Button(topLeftFrame, text = "Remove Item", command = self.removeItem,
                              font = btnFont, relief = FLAT)
        addButton.grid(row = self.itemListSize + 1, column = 1)
        removeButton.grid(row = self.itemListSize + 1, column = 0)
        predictButton.grid(row = self.itemListSize + 1 , column = 3)


    def createEntryBoxes(self, topLeftFrame):
        self.checkWidgets = []
        for i in range(0, len(self.itemList)):
            self.checkWidgets.append(tk.Entry(topLeftFrame))
            self.checkWidgets[-1].grid(row = i+1, column = 0)
        

    def createLabels(self, topLeftFrame):
        listFont, labelFont = font.Font(family = "Helvetica",size=13), font.Font(family = "Helvetica", size = 11)
        titleLabel = tk.Label(topLeftFrame, text = "How Many Items Are Being Sold Today", font = labelFont).grid(row = 0, column = 0)
        for i in range(0,len(self.itemList)):
            itemLabel = tk.Label(topLeftFrame, text = self.itemList[i],
                                 font = listFont, pady = 5).grid(row = i + 1, column = 1)
        self.itemListSize = len(self.itemList)

    def getCheckValues(self):
        results = []
        for value in self.checkWidgets:
            if value.get() == "":
                results.append(0)
            else:
                results.append(value.get())
        print(results)

    def addItem(self):
        addPopUp = tk.Toplevel()
        popUpFont = font.Font(family = "Helvetica", size = 15)
        Message = tk.Label(addPopUp,text= "Please Enter The Item You Would Like To Add", font = popUpFont).grid(row = 1, column = 1)
        Entry = tk.Entry(addPopUp, width = 30, justify="center")
        Entry.grid(row = 2, column = 1)
        Button = tk.Button(addPopUp,text = "Add Item", font = popUpFont,relief = FLAT,
                           command = lambda: (self.updateDatabase("a", (Entry.get())), self.refresh(addPopUp))).grid(row=3, column = 1)
        

    def updateDatabase(self, _type, item):
        if _type == "a":
            if len(self.itemList) <= 15:
                with open("App_Package/saved_data/PastryIndex.csv", "a", newline = "") as PastryFile:
                    fieldnames = ["Item"]
                    writer = csv.DictWriter(PastryFile, fieldnames = fieldnames)
                    writer.writerow({"Item": item.upper()})
            else:
                ErrorPopup("""You Have Reached The Max Number Of Items In This Section
If You Would Like To Add More Please Remove Any Redundant Items""")
        elif _type == "rb":
            lines = list()
            with open("App_Package/saved_data/PastryIndex.csv", "r", newline = "") as readFile:
                reader = csv.reader(readFile)
                for row in reader:
                    lines.append(row)
                    if row[0] == item:
                        lines.remove(row)
            with open("App_Package/saved_data/PastryIndex.csv", "w", newline = "") as writeFile:
                writer = csv.writer(writeFile)
                writer.writerows(lines)
        self.refresh(self.topLeftFrame)

    def removeItem(self):
        remPopUp = tk.Toplevel()
        popUpFont = font.Font(family = "Helvetica", size = 15)
        Message = tk.Label(remPopUp,text= "Please Select The Item You Would Like To Remove", font = popUpFont).grid(row = 1, column = 1)
        Listbox = tk.Listbox(remPopUp, width = 30, justify = "center")
        for item in self.itemList:
            Listbox.insert("end", item)
        Listbox.grid(row = 2, column = 1)
        Button = tk.Button(remPopUp,text = "Remove Item", font = popUpFont,relief = FLAT, command = lambda: (self.updateDatabase("rb", (Listbox.get(ANCHOR))),
                                                                                                             self.refresh(remPopUp))).grid(row=3, column = 1)

    
class uploadFrame(mainPage):
    def __init__(self, UI):
        #code for pdf display re-purposed off tkPDFViewer
        self.UI = UI
        bottomLeftFrame = tk.Frame()
        self.bottomLeftFrame = bottomLeftFrame
        self.img_object_li = []
        self.create_scrollbar()
        self.create_buttons()
        self.pdf_view()
        self.bottomLeftFrame.after(250,self.start_pack)
        bottomLeftFrame.grid(row = 2, column = 0)
        bottomLeftFrame.mainloop()

    def pdf_view(self):
        self.percentage_view = 0
        self.percentage_load = StringVar()
        self.display_msg = Label(textvariable=self.percentage_load)
        self.loading = Progressbar(self.bottomLeftFrame,orient= HORIZONTAL,length=100,mode='determinate')
        self.loading.pack(side = TOP,fill=X)
        self.text = Text(self.bottomLeftFrame,yscrollcommand=self.scrollBar.set,width= 80,height= 25)
        self.text.pack(side="left")
        self.scrollBar.config(command = self.text.yview)

    def add_img(self):
        try:
            precentage_dicide = 0
            open_pdf = fitz.open(self.file)
            for page in open_pdf:
                pix = page.getPixmap()
                pix1 = fitz.Pixmap(pix,0) if pix.alpha else pix
                img = pix1.getImageData("ppm")
                timg = PhotoImage(data = img)
                self.img_object_li.append(timg)
                precentage_dicide = precentage_dicide + 1
                self.percentage_view = (float(precentage_dicide)/float(len(open_pdf))*float(100))
                self.loading['value'] = self.percentage_view
                self.percentage_load.set(f"Please wait!, your pdf is loading {int(math.floor(self.percentage_view))}%")
            self.loading.pack_forget()
            self.display_msg.pack_forget()
            for i in self.img_object_li:
                self.text.image_create(END,image=i)
                self.text.insert(END,"\n\n")
            self.text.configure(state="disabled")
        except:
            pass

    def start_pack(self):
        t1 = Thread(target=self.add_img())
        t1.start()

    def create_scrollbar(self):
        self.scrollBar = Scrollbar(self.bottomLeftFrame,orient="vertical")
        self.scrollBar.pack(fill="y",side="right")

    def create_buttons(self):
        btnFont = font.Font(family = "Helvetica",size = 15)
        try:
            if self.pdf_picked == True:
                right_pdf_btn = tk.Button(self.bottomLeftFrame, text = "Right Pdf", bg = "green", font = btnFont, command = self.upload_pdf)
                wrong_pdf_btn = tk.Button(self.bottomLeftFrame, text = "Wrong Pdf",  bg = "red", font = btnFont, command = self.open_pdf)
                right_pdf_btn.pack(side = "bottom", fill = "x")
                wrong_pdf_btn.pack(side = "bottom", fill = "x")
            else:
                arg
        except:
            addPdf = tk.Button(self.bottomLeftFrame, text = "Upload Colin Data", relief = FLAT, font = btnFont, command = self.open_pdf)
            addPdf.pack(side = "bottom")
            
    def open_pdf(self):
        pdf_path = filedialog.askopenfilename()
        pdf_path_list = list(pdf_path)
        if len(pdf_path) > 0 and pdf_path_list[(len(pdf_path)-3):] == ["p","d","f"]:
            self.file = pdf_path
            self.pdf_picked = True
            self.refresh(self.bottomLeftFrame)
        else:
            ErrorPopup("Please Select A Pdf")

    def upload_pdf(self):
        pdfProcessor.gatherColinData(self.file)
        self.file, self.pdf_picked = None, False
        self.refresh(self.bottomLeftFrame)

    
        

        
class controlFrame(mainPage):
    def __init__(self, UI):
        listFont, self.labelFont = font.Font(family = "Helvetica",size=13), font.Font(family = "Helvetica", size = 11)
        self.bottomRightFrame = tk.Frame(UI)
        self.UI = UI
        self.createButtons()
        self.createDropTable()
        self.createEntryboxs()
        self.createCalendar()
        self.bottomRightFrame.grid(row = 2, column = 1, pady = 100)

    def Del_Waste_placeholder(self, event):
        self.wastedEntry.delete(0, END)

    def Del_PutOut_placeholder(self, event):
        self.putOutEntry.delete(0, END) 

    def createButtons(self):
        btnFont = font.Font(family = "Helvetica",size = 15)
        addData = tk.Button(self.bottomRightFrame, text = "Add Data", font = btnFont, relief = FLAT,
                             command = self.addData)
        refreshPage = tk.Button(self.bottomRightFrame, text = "Refresh Page", font = btnFont, relief = FLAT,
                             command = lambda: self.refresh(self.bottomRightFrame))
        todayButton = tk.Button(self.bottomRightFrame, text = "Today", font = btnFont, relief = FLAT, fg = "blue",
                                command = lambda: (self.dateSelect.destroy(), self.createCalendar()))
        todayButton.grid(row = 2, column = 2)
        addData.grid(row = 10, column = 3)
        refreshPage.grid(row = 10, column = 2)
        
    def createEntryboxs(self):
        EntryFont = font.Font(family = "Helvetica",size=13)
        wasteText, putOutText = StringVar(), StringVar()
        wasteText.set("How Many Were Wasted"), putOutText.set("How Many Were Put Out")
        self.wastedEntry = tk.Entry(self.bottomRightFrame,
                                    textvariable = wasteText, width = 25, font = EntryFont)
        self.wastedEntry.bind("<Button>", self.Del_Waste_placeholder)
        self.wastedEntry.grid(row = 1, column = 1)
        self.putOutEntry = tk.Entry(self.bottomRightFrame, 
                                    textvariable = putOutText, width = 25, font = EntryFont)
        self.putOutEntry.bind("<Button>", self.Del_PutOut_placeholder)
        self.putOutEntry.grid(row = 1, column = 2)

    def createDropTable(self):
        variable = StringVar(self.bottomRightFrame)
        variable.set(itemList[0]) 
        self.itemOption = ttk.Combobox(self.bottomRightFrame, value = itemList, font = self.labelFont)
        self.itemOption.set("Please Select A Item")
        self.itemOption.grid(row = 0, column = 0)

    def createCalendar(self):
        self.dateSelect = DateEntry(self.bottomRightFrame, width = 35, bg = "dark blue", fg = "white", date_pattern = "yyyy-mm-dd")
        self.dateSelect.grid(row = 2, column = 1)
        

    def addData(self):
        try:
            valueForToday = False
            with open("App_Package/saved_data/wastage_data.csv", "r", newline="") as csvfile:
                reader = csv.reader(csvfile)
                for i in reader:
                    if i[0] == self.dateSelect.get():
                        if i[1] == self.itemOption.get():
                            ErrorPopup("value already created for today")
                            valueForToday = True
                if valueForToday == False:
                    with open("App_Package/saved_data/wastage_data.csv", "a", newline="") as csvfile:
                        fieldnames = ["Date","Pastry","Waste", "Put Out"]
                        writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
                        writer.writerow({"Date": self.dateSelect.get(),
                                         "Pastry": self.itemOption.get(),
                                         "Waste": self.wastedEntry.get(),
                                         "Put Out": self.putOutEntry.get()})
            self.refresh(self.bottomRightFrame)
        except:
            with open("App_Package/saved_data/wastage_data.csv", "w+", newline="") as csvfile:
                fieldnames = ["Date","Pastry","Waste", "Put Out"]
                writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
                writer.writerow({"Date": self.dateSelect.get(),
                                 "Pastry": self.itemOption.get(),
                                 "Waste": self.wastedEntry.get(),
                                 "Put Out": self.putOutEntry.get()})
            self.refresh(self.bottomRightFrame)
            

            

class displayFrame(mainPage):
    def __init__(self, UI):
        self.rightFrame = tk.Frame(UI)
        self.get_data()
        self.createLabels()
        self.rightFrame.grid(row = 1, column = 1)

    def get_data(self):
        self.wasteData = []
        for i in range(len(itemList)):
            self.wasteData.append("?")

    def createLabels(self):
        listFont, labelFont, titleFont = font.Font(family = "Helvetica",size=13, underline = True, weight = "bold"), font.Font(family = "Helvetica", size = 11, weight = "bold"), font.Font(family = "Helvetica", size = 15, weight = "bold", underline = True)
        titleLabel = tk.Label(self.rightFrame, text = "How Many Items Will Be Wasted", font = titleFont).grid(row = 0, column = 2)
        for i in range(0,len(self.wasteData)):
            itemLabel = tk.Label(self.rightFrame, text = (itemList[i] + ":"),
                                 font = listFont, pady = 5).grid(row = i + 1, column = 1)
            itemValue = tk.Label(self.rightFrame, text = (self.wasteData[i]),
                                 font = labelFont, pady = 5).grid(row = i + 1, column = 2)
        
class ErrorPopup:
    def __init__(self, ErrorMessage):
        ErrorWindow = tk.Toplevel()
        ErrorWindow.title("Error")
        labelfont = font.Font(family = "Helvetica", size = 15, weight = "bold", underline = True)
        Btnfont = font.Font(family = "Helvetica", size = 11)
        Message = tk.Label(ErrorWindow,text= ErrorMessage, font = labelfont, pady = 10, padx= 10).grid(row = 1, column = 1)
        Button = tk.Button(ErrorWindow, text = "Okay", font = Btnfont, relief = FLAT,
                           command = lambda: ErrorWindow.destroy()).grid(row=3, column = 1)

def train_data_set():
    train_network = Network
    train_network.TrainingData()

def get_weather_data(location):
    try:
        report = weatherReport
        report.getLocationWeather(location)
    except:
        raise("Connect to internet")

def startup_threads():
    weather_thread = Thread(target = get_weather_data, args = ("Felixstowe",))
    train_thread = Thread(target = train_data_set)
    weather_thread.start()
    weather_thread.join()
    train_thread.start()

if __name__ == "__main__":
    startup_threads()
    mainPage()

