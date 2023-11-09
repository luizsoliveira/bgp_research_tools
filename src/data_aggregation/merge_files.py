import fileinput

def merge_files(files_in, file_out, header_line=False):

    with open(file_out, 'w') as file:
        
        input_lines = fileinput.input(files_in)
        if (header_line): file.write(f"{header_line}\n")
        file.writelines(input_lines)