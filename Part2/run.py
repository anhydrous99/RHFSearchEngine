import collections
from zipfile import ZipFile
from tok import Tokenizer


def main():
    with ZipFile('Jan.zip') as zipfile:
        file_path_list = zipfile.namelist()
        tokenizer = Tokenizer()

        # Create a list of File types that store all information pertaining to an html file.
        # In he third period, the task says to use a hash map but I believe that we don't need to use a hash map.
        # The index of the list would be the same as the unique numerical id of a hash map.
        file_list = []
        for path in file_path_list:
            with zipfile.open(path) as html_file:
                contents = html_file.read().decode('utf-8')
                df = tokenizer.tokenize(path, contents)
                file_list.append(df)

    # Calculate the document frequency
    # The counter container is great!! :D
    df = collections.Counter()
    for file in file_list:
        df.update(file.wordlist)
    print(df)


if __name__ == "__main__":
    main()
