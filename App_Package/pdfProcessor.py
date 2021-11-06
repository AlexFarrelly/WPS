from PyPDF2 import PdfFileReader
import csv

class gatherColinData:
    def __init__(self, file):
        self.pdf = PdfFileReader(file)
        self.write_data()
        self.process_data()
        self.save_data()

    def write_data(self):
        with open("App_Package/saved_data/pdfData.txt", "w") as f:
            for page_num in range(self.pdf.numPages):
                if page_num < 3:
                    pass
                else:
                    pageObj = self.pdf.getPage(page_num)

                    try: 
                        txt = pageObj.extractText()
                    except:
                        pass
                    else:
                        f.write("Page {0}\n".format(page_num+1))
                        f.write("".center(100, "-"))
                        f.write(txt)

    def process_data(self):
        with open("App_Package/saved_data/pdfData.txt", "rt") as f:
            contents = list(f.read())            
        f.close()
        for i in range(len(contents)):
            if contents[i] == "H" and contents[i+1] == "o":
                start = i
        list_string = (contents[start:])
        string = "".join([str(char) for char in list_string])
        charStr, charList = "", []
        for char in string:
            if char == """
""":
                charList.append(charStr)
                charStr = ""
            else:
                charStr = charStr + char

        for char in charList:
            self.charList = charList
            if char == "8. Store Opening Times":
                index = charList.index(char)
                charList = charList[:index]
        daily_start = charList.index("08")
        daily_end = charList.index("Last 4 Week Average") - daily_start
        average_start = (charList[daily_end + daily_start:])
        self.average_data = average_start[average_start.index("08"):]
        self.daily_data = charList[daily_start:][:daily_end]
        daily_time_list = []
        average_time_list = []
        
        for i in range(1, 11):
            daily_time_list.append(self.daily_data[1:][:11])
            average_time_list.append(self.average_data[1:][:10])
            if i == 1:
                self.average_data = self.average_data[30:]
                self.daily_data = self.daily_data[30:]
            else:
                self.average_data = self.average_data[31:]
                self.daily_data = self.daily_data[31:]
                
        daily_totals = self.daily_data[self.daily_data.index("Total")+1:][:10]
        average_totals = self.average_data[self.average_data.index("Total")+1:][:10]
        daily_totals_processed, self.daily_weights = [], []
        average_totals_processed, self.average_weights = [], []

        for num in daily_totals:
            number = list(num)
            new_number = ""
            for digit in number:
                if digit == ",":
                    pass
                else:
                    new_number = new_number + digit
            daily_totals_processed.append(int(new_number))
            
        for i in range(len(daily_totals_processed)):
            total = int(daily_totals_processed[i])
            for time in daily_time_list:
                time_weight = int(time[i]) / total
                self.daily_weights.append(time_weight)

        for num in average_totals:
            number = list(num)
            new_number = ""
            for digit in number:
                if digit == ",":
                    pass
                else:
                    new_number = new_number + digit
            average_totals_processed.append(int(new_number))

            
        for i in range(len(average_totals_processed)):
            total = int(average_totals_processed[i])
            for time in average_time_list:
                time_weight = int(time[i]) / total
                self.average_weights.append(time_weight)


    def save_data(self):
        date_list = []
        month_dict = {"Jan": "01","Feb": "02","Mar": "03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov": "11", "Dec": "12"}
        for i in range(7):
            date = self.charList[(self.charList.index("Hourly Sales by Day") + 1)]
            day = int((date.split(" "))[0]) + i
            month = month_dict[date.split(" ")[1]]
            year = date.split(" ")[2]
            date = [year, "-", month, "-", day]
            date_list.append("".join([str(char) for char in date]))
        try:
            valueForToday = False
            with open("App_Package/saved_data/weather_weights.csv", "r", newline="") as csvfile:
                index = -1
                reader = csv.reader(csvfile)
                for index in range(7):
                    for i in reader:
                        if i[1] == date_list[index]:
                            valueForToday = True
                            break
            if valueForToday == False:
                with open("App_Package/saved_data/weather_weights.csv", "a", newline="") as csvfile:
                    fieldnames = ["Type","Date","Weights"]
                    for index in range(7):
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow({"Type": "Daily",
                                         "Date": date_list[index],
                                         "Weights": self.daily_weights[:10]})
                        self.daily_weights = self.daily_weights[10:]
                    for index in range(7):
                        writer.writerow({"Type": "Average",
                                         "Date": date_list[index],
                                         "Weights": self.average_weights[:10]})
                        self.average_weights = self.average_weights[10:]

        except:
            with open("App_Package/saved_data/weather_weights.csv", "w+", newline="") as csvfile:
                fieldnames = ["Type","Date","Weights"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            self.save_data()

        
        



