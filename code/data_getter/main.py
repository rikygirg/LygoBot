from data_getter import get_formatted_data

string = "1 may 2024 00:00:00.00"
string2 = "9 may 2024 00:00:00.00"
folder_path = "data"
get_formatted_data(start_date=string, end_date=string2, interval="1s", 
                   categories=["close", "high", "low", "volume", "qav"],
                   folder_path=folder_path)

# Before running this code, insert the apy_key and secret_key in the data_getter.py file.