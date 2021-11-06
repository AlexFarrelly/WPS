try:
    import numpy as np
    import csv, os, pickle, threading, pandas as pd
    
except ModuleNotFoundError:
    import subprocess
    import sys
    for package in ["numpy", "csv", "os", "pickle", "threading", "pandas"]:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    

finally:
    class Network:
        def __init__(self, pastry_key, date_key, input_list, output_list, gen):
            self.layers = []
            self.PastryType = pastry_key
            self.Date = date_key
            self.createLayers()
            self.train(input_list, output_list, gen)
            
        def createLayers(self):
            self.layers.append(self.FullyConnectedLayer(80,40, self.PastryType, self.Date))
            self.layers.append(self.FullyConnectedLayer(40,20, self.PastryType, self.Date))
            self.layers.append(self.FullyConnectedLayer(20,10, self.PastryType, self.Date))
            self.layers.append(self.FullyConnectedLayer(10,5, self.PastryType, self.Date))
            self.layers.append(self.FullyConnectedLayer(5,2, self.PastryType, self.Date))
            self.layers.append(self.FullyConnectedLayer(2,1, self.PastryType, self.Date))
            self.layers.append(self.ActivationLayer())

        def updateWeightValues(self):
            try:
                try:
                    updated_data = list()
                    readweightData = open("App_Package/saved_data/weight_data.txt", "rb")
                    df = pd.read_pickle(readweightData)
                    df = df.drop(df[(df.Pastry == self.PastryType) & (df.Date == self.Date)].index)
                    readweightData.close()
                    os.remove("saved_data/weight_data.txt")
                            
                except Exception as e:
                    df = pd.DataFrame()
                    
                finally:
                    weightData = open("App_Package/saved_data/weight_data.txt", "ab")
                    data = ({"Pastry": self.PastryType,
                                     "Date": self.Date,
                                     "inputLayer": self.layers[0].weights,
                                     "HiddenLayer1": self.layers[1].weights,
                                     "HiddenLayer2": self.layers[2].weights,
                                     "HiddenLayer3": self.layers[3].weights,
                                     "HiddenLayer4": self.layers[4].weights,
                                     "HiddenLayer5": self.layers[5].weights})
                    df = df.append(data, ignore_index=True)
                    df.to_pickle(weightData)
                    weightData.close()
            except Exception as e:
                print(e)
                self.updateWeightValues()
                
        def updateBiasValue(self):
            try:
                try:
                    updated_data = list()
                    read_bias_data = open("App_Package/saved_data/bias_data.txt", "rb")
                    df = pd.read_pickle(read_bias_data)
                    df = df.drop(df[(df.Pastry == self.PastryType) & (df.Date == self.Date)].index)
                    read_bias_data.close()
                    os.remove("saved_data/bias_data.txt")
                            
                except Exception as e:
                    df = pd.DataFrame()
                    
                finally:
                    bias_data = open("App_Package/saved_data/bias_data.txt", "ab")
                    data = ({"Pastry": self.PastryType,
                                     "Date": self.Date,
                                     "inputLayer": self.layers[0].bias,
                                     "HiddenLayer1": self.layers[1].bias,
                                     "HiddenLayer2": self.layers[2].bias,
                                     "HiddenLayer3": self.layers[3].bias,
                                     "HiddenLayer4": self.layers[4].bias,
                                     "HiddenLayer5": self.layers[5].bias})
                    df = df.append(data, ignore_index=True)
                    df.to_pickle(bias_data)
                    bias_data.close()
            except Exception as e:
                print(e)
                self.updateBiasValue()
            
        def train(self, inputTrainData, outputTrainData, gen):
            samples = len(inputTrainData)
            for i in range(gen):
                err = 0
                for value in range(samples):
                    output = inputTrainData[value]
                    for layer in self.layers:
                        output = layer.forward_propergation(output)
                    err += np.mean(np.power(outputTrainData[value]-output, 2))
                    error = 2*(outputTrainData[value] - output)/(outputTrainData[value]).size
                    for layer in reversed(self.layers):
                        error = layer.backward_propergation(error, .1)
                err /= samples
                print("generation %d/%d error = %f" % (i+1, gen, err) , self.PastryType, self.Date)
                
            self.updateWeightValues()
            self.updateBiasValue()

        def predict(self, input_data):
            result = []
            for value in range(len(input_data)):
                output = input_data[value]
                for layer in self.layers:
                    output = layer.forward_propergation(output)
                result.append(output)
            return result

        class FullyConnectedLayer():
            def __init__(self, input_size, output_size, pastry_type, date):
                self.PastryType = pastry_type
                self.Date = date
                self.weights = self.__gatherWeightValues(input_size, output_size)
                self.bias = self.__gatherBiasValues(output_size, input_size)
            
            def __gatherWeightValues(self, input_size, output_size):
                try:
                    df = pd.read_pickle("App_Package/saved_data/weight_data.txt")
                    data = df.loc[df[(df.Pastry == self.PastryType) & (df.Date == self.Date)].index]
                    data = data.dropna()
                    if input_size == 80:
                        array = self.check_has_nan((data["inputLayer"].to_numpy()[0]))
                        return array
                    elif input_size == 40:
                        array = self.check_has_nan((data["HiddenLayer1"].to_numpy()[0]))
                        return array
                    elif input_size == 20:
                        array = self.check_has_nan((data["HiddenLayer2"].to_numpy()[0]))
                        return array
                    elif input_size == 10:
                        array = self.check_has_nan(data["HiddenLayer3"].to_numpy()[0])
                        return array
                    elif input_size == 5:
                        array = self.check_has_nan((data["HiddenLayer4"].to_numpy()[0]))
                        return array
                    else:
                        array = self.check_has_nan((data["HiddenLayer5"].to_numpy()[0]))
                        return array
                        
                except Exception as e:
                    print(e)
                    return np.random.rand(input_size, output_size) - 0.5


            def __gatherBiasValues(self, output_size, input_size):
                try:
                    df = pd.read_pickle("App_Package/saved_data/bias_data.txt")
                    data = df.loc[df[(df.Pastry == self.PastryType) & (df.Date == self.Date)].index]
                    if input_size == 80:
                        array = data["inputLayer"].to_numpy()[0]
                        return array
                    elif input_size == 40:
                        array = data["HiddenLayer1"].to_numpy()[0]
                        return array
                    elif input_size == 20:
                        array = data["HiddenLayer2"].to_numpy()[0]
                        return array
                    elif input_size == 10:
                        array = data["HiddenLayer3"].to_numpy()[0]
                        return array
                    elif input_size == 5:
                        array = data["HiddenLayer4"].to_numpy()[0]
                        return array
                    else:
                        array = data["HiddenLayer5"].to_numpy()[0]
                        return array
                                      
                except Exception as e:
                    print(e)
                    return np.random.rand(1, output_size) - 0.5

            def check_has_nan(self, array):
                array_check = np.sum(array)
                check = np.isnan(array_check)
                if check:
                    array = np.nan_to_num(array, copy = True, nan = (np.nanmean(array, dtype=np.float64)))
                    print(array.shape)
                return array

            def forward_propergation(self, input_data):
                self.input = input_data
                self.output = np.dot(self.input, self.weights) + self.bias
                return self.output

            def backward_propergation(self, output_error, learning_rate):
                input_error = np.dot(output_error, self.weights.T)
                weights_error = np.dot(self.input.T, output_error)
                self.weights = self.weights - (0.1 * weights_error)
                self.bias = self.bias - (learning_rate * output_error)
                return input_error


        class ActivationLayer():
            def forward_propergation(self, input_data):
                self.input = input_data
                self.output = np.tanh(self.input)
                return self.output

            def backward_propergation(self, output_error, learning_rate):
                return (- np.tanh(self.input)**2) * output_error


    class TrainingData:
        def __init__(self):
            self.gather_pastry_data()
            self.gather_waste_data()
            self.gather_day_weight()
            self.gather_weather_data()
            self.gather_weight_dates()
            self.create_train_dataset()

        def gather_pastry_data(self):
            self.pastry_types = []
            with open("App_Package/saved_data/PastryIndex.csv", "r", newline = "") as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    self.pastry_types.append(row)

        def gather_day_weight(self):
            self.weather_weight_data = []
            with open("App_Package/saved_data/weather_weights.csv", "r", newline="") as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    found = False
                    if row[0] == "Daily":
                        for date in self.dates:
                            if row[1] == date:
                                found = True
                                input_data = []
                                for index in range(10):
                                    if index == 0:
                                        input_data.append(row[1])
                                        input_data.append(float(((row[2].split(","))[index]).replace("[", "")))
                                    elif index == 9: input_data.append(float(((row[2].split(","))[index]).replace("]", "")))
                                    else: input_data.append(float(((row[2].split(","))[index])))
                                self.weather_weight_data.append(input_data)
                        if found == False:
                            self.dates.remove(date)
            

        def gather_weather_data(self):
            self.weather_data = []
            with open("App_Package/saved_data/weatherData.csv", "r", newline="") as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    for date in self.dates:
                        if row[0] == date:
                            data = row
                            self.weather_data.append(data)
                            break

        def gather_waste_data(self):
            self.waste_data, self.dates = [], []
            with open("App_Package/saved_data/wastage_data.csv", "r", newline="") as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    for pastry in self.pastry_types:
                        if row[1] == (((str(pastry)).replace("[", "")).replace("]", "").replace("'", "")):
                            self.waste_data.append(row)
            for data in self.waste_data:
                self.dates.append(data[0])

        def gather_weight_dates(self):
            self.weight_dates = []
            with open("App_Package/saved_data/weather_weights.csv", "r", newline="") as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    self.weight_dates.append(row[1])


        
        def create_train_dataset(self):
            #gathering all of the data=====================================================================
            training_data, input_data = [], []
            old_date = None
            for weather_data in self.weather_data:
                date = weather_data[0]
                if int(weather_data[2]) > 7 and int(weather_data[2]) < 18:
                    if date != old_date: 
                        training_data.append(input_data)
                        old_date, input_data = date, []
                        input_data.append(weather_data)
                    else: input_data.append(weather_data)
            training_data = training_data[1:]
            
            old_date = None
            for weight_data in self.weather_weight_data:
                for data in training_data:
                    if weight_data[0] == data[0][0] and weight_data[0] != old_date:
                        data.append(weight_data)
                        old_date = weight_data[0]
                        break
            #adding the data together=====================================================================      
            processed_input_data = []
            for data in training_data:
                input_data = [[]]
                for each in data:
                    try:
                        exception = int(each[1])
                        each = each[1:]
                        for weight in each:
                            input_data[0].append(float(weight) / 100)
                    except:
                        each = each[3:]
                        for weather in each:
                            input_data[0].append(float(weather) / 100)
                processed_input_data.append(input_data)

            #adding waste and key data====================================================================
            output_list, input_list = [],[]
            index, count = 0, 0
            for data in self.waste_data:
                input_data = []
                if count >= 8: index = 1
                else: index = 0
                for i in range(len(processed_input_data[index])):
                    input_data.append((processed_input_data[index][i]))
                input_list.append(input_data)
                try:
                    output_data = [int(data[2])/int(data[3])]
                except:
                    output_data = [0]
                output_list.append([output_data]) 
                count += 1
                
            #grouping of training data=====================================================================
            index = 0
            for key in self.waste_data:
                pastry_key = key[1]
                day_key = pd.Timestamp(key[0]).day_name()
                data = input_list[index]
                index += 1
                data.insert(0, day_key)
                data.insert(0, pastry_key)
            used_data_list = [None]
            for pastry in self.waste_data:
                grouped_data, grouped_output = [], []
                for data in input_list:
                    for date in self.weight_dates[1:]:
                        date = pd.Timestamp(date).day_name()
                        if date == data[1]:
                            if pastry[1] == data[0]: 
                                grouped_date = (date)
                                grouped_output.append(output_list[input_list.index(data)])
                                grouped_data.append(data[2:])
                                for used_data in used_data_list:
                                    if used_data == [pastry[1], date]:
                                        break
                                    else:
                                        Network(pastry[1], date, np.array(grouped_data), np.array(grouped_output), 1)
                                        used_data_list.append([pastry[1], grouped_date])
                                        break
                                    break
                                break 
                        
                    
                
          
    

        
