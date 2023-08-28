import os

def concatenate_files(directory):
    # List all files in the directory
    all_files = os.listdir(directory)
    
    # Filter only .txt files and sort them
    txt_files = sorted([f for f in all_files if f.endswith('.txt')])
    
    # Function to generate a sort key for filenames
    def file_sort_key(filename):
        chapter, section = filename[:-8].split('_')
        if section[-1].isalpha():
            section_order = ord(section[-1])
        else:
            # Give a high priority to sections without an alphabetical suffix, 
            # except for 'C' which should have priority
            section_order = ord('A') - 1 if section[-1] != 'C' else ord(section[-1])
        return (int(chapter), int(section[:-1]), section_order)

    # Sort the filenames based on our custom order
    txt_files = sorted(txt_files, key=file_sort_key)

    # Filter out alternate endings except those denoted by 'C'
    txt_files = [f for f in txt_files if not (f[-7].isalpha() and f[-7] != 'C')]

    # Concatenate the text files
    output_text = ""
    for file_name in txt_files:
        print("Concatenating " + file_name)
        with open(os.path.join(directory, file_name), 'r') as f:
            output_text += f.read() + "\n\n"

    # Save the concatenated text to the current directory
    with open('combined_script.txt', 'w') as f:
        f.write(output_text)

concatenate_files('./sg_script_raw/')