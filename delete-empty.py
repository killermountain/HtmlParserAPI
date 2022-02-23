import os

curr_dir = os.getcwd()
hospital_name = "Broomfield" # "MSE" # 
input_dir = curr_dir + os.path.sep +"input-html"+ os.path.sep + hospital_name + os.path.sep
folders = os.listdir(input_dir)

for folder in folders:
    print(folder)
    folder_path =os.path.join(input_dir,folder)
    d = os.listdir(folder_path)
    if len(d) == 0:
        # print(folder)
        os.rmdir(folder_path)
        print("deleted")