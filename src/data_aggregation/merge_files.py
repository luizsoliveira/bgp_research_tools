import fileinput
import glob

file_list = glob.glob("*.txt")

def merge_files(files_in, file_out):

    with open(file_out, 'w') as file:
        input_lines = fileinput.input(files_in)
        file.writelines(input_lines)