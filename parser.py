from os.path import exists
import codecs
from datetime import datetime
from json import dumps

# pip install beautifulsoup4
from bs4 import BeautifulSoup

def get_files():
    """Check number of files to be parsed and return their file names"""
    number_of_files = 1
    file_exists = True
    filenames = []

    while(file_exists):
        filename = './AllaNyheterWithText' + str(number_of_files) + '.html'
        if not exists(filename):
            file_exists = False
            break
        filenames.append(filename)
        number_of_files += 1
    return filenames

def parse_files(filenames):
    post_list = []
    for filename in filenames:
        # Open file
        html = BeautifulSoup(codecs.open(filename, 'r', 'utf8', 'ignore').read(), 'html.parser')

        # Set iterator to the correct level of the tree
        post_iterator = html.body.div.div.next_sibling.next_sibling.div.previous_sibling.next_siblings
        new_list = []

        # Filter out irrelevant tags
        for item in post_iterator:
            if item.name == 'div':
                new_list.append(item.contents)
        
        post_dict = {}
        
        for i, item in enumerate(new_list):
            # Join arrays of strings and make sure linebreaks remain linebreaks
            item_string = ''.join(map(lambda x: '' if repr(x)==repr('\n') else repr(x), item)) 
            match (i % 6):
                case 0:
                    # Link to post will be dead next year anyways, so we ignore it and just create a empty dict for the other data
                    post_dict = dict()
                case 1:
                    time_string = fix_time_string(remove_description(repr(item[0]), "Publicerad"))
                    post_dict['published'] = datetime.strptime(time_string, '%d %b %Y %H:%M').isoformat()
                case 2:
                    time_string = fix_time_string(remove_description(repr(item[0]), "Uppdaterad"))
                    post_dict['last_edited'] = datetime.strptime(time_string, '%d %b %Y %H:%M').isoformat()
                case 3:
                    post_dict['title'] = remove_description(repr(item[0]), "Rubrik på sidan")
                case 4:
                    post_dict['preamble'] = remove_description(item_string, "Ingress")
                case 5:
                    post_dict['content'] = item_string
                    post_list.append(post_dict)
        
    return post_list

def remove_description(item, description_string):
    return item.replace(description_string, "").replace(":\\xa0\\xa0\\xa0\\xa0 ", "") \
        .replace(":\\xa0\\xa0\\xa0\\xa0", "").replace("'", "")

def fix_time_string(time_string):
    """
    Turn Swedish month-abbrevations into English ones
    """
    return time_string.replace("OKT", "OCT").replace('MAJ', 'MAY')
    
def generate_json_file(post_list):
    json_string = (dumps(post_list, ensure_ascii=False))
    f = open('allPosts.json', 'w', 1, 'utf8', 'ignore')
    f.write(json_string)

if __name__ == "__main__":
    filenames = get_files()
    post_list = parse_files(filenames)
    generate_json_file(post_list)