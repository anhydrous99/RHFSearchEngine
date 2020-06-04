#
#  Created by Armando Herrera (ID: 20217690)
#

from zipfile import ZipFile
import collections
import html2text
import re

# Create named tuple that will contain a file's information
File = collections.namedtuple('File', ['filename', 'contents', 'wordlist'])


def main():
    # Initiate the html parser
    h = html2text.HTML2Text()
    # Compile the regular expression engine
    p = re.compile(r'[^\W_0123456789]+')
    # Set some options for the html parser
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_emphasis = True
    h.escape_all = True

    file_list = []
    # Open the zipfile called Jan.zip
    with ZipFile('Jan.zip') as zipfile:
        # Get list of file names from the zip file
        file_path_list = zipfile.namelist()
        # Iterate through the list of file names
        for path in file_path_list:
            # Open each html file
            with zipfile.open(path) as htmlfile:
                # Get each html file's content and decode w/ utf-8
                contents = htmlfile.read().decode('utf-8')
                # Parse html to text (removes tags and such)
                contents_txt = h.handle(contents)
                # Parses the text into a list of words and converts said words to lower case
                wordlist = [w.lower() for w in p.findall(contents_txt)]
                # Add gathered information to list
                file_list.append(File(path, contents, wordlist))

    print('Now, the search begins:')
    while True:
        search_term = input('Enter a search key=> ')
        # Breaks when empty string
        if not search_term:
            break

        found = []
        # Search list of files for word
        for file in file_list:
            if search_term in file.wordlist:
                found.append(file.filename)

        # This is what happens if found or not found :D
        if found:
            if len(found) == 1:
                print(f'found a match: {found[0]}')
            else:
                print('found matches: ')
                for f in found:
                    print(f)
        else:
            print('no match')
    print('Bye')


if __name__ == '__main__':
    main()
