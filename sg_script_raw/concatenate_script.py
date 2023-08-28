import os

def concatenate_txt_files(directory):
    # List all files in the directory
    files = os.listdir(directory)

    # Filter for .txt files
    txt_files = [f for f in files if f.endswith('.txt')]

    # Check if there are any .txt files
    if not txt_files:
        print("No .txt files found in the directory.")
        return

    # Create a new file to save the concatenated content
    output_file_name = "concatenated.txt"
    with open(output_file_name, 'w') as outfile:
        for txt_file in txt_files:
            with open(os.path.join(directory, txt_file), 'r') as infile:
                # Write the content of the file to the outfile
                outfile.write(infile.read())
                # Add a newline to separate contents of files
                outfile.write('\n')

    print(f"Concatenated {len(txt_files)} files and saved to {output_file_name}")

if __name__ == "__main__":
    # Using the current directory of the script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    concatenate_txt_files(current_directory)