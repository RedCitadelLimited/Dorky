#!/usr/bin/env python3

import requests
import sys
import json
import argparse

# DORKY API Keys
# api_key = 'YOUR_API'
# search_engine_id = 'YOUR_ID'


# ANSI escape codes for colors
BLUE = '\033[94m'
YELLOW = '\033[93m'
WHITE = '\033[0m'
BOLD = '\033[1m'
PURPLE = '\033[95m'
RED = '\033[91m'

# Default keywords and file types
DEFAULT_IT_TERMS = ['admin', 'password', 'username']
DEFAULT_IU_TERMS = ['admin', 'password', 'username']
DEFAULT_FILE_TYPES = [
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'bak', 'txt',
    'config', 'web.config', 'ini', 'js', 'php', 'html', 'htm',
    'cfm', 'jsp', 'asp', 'aspx', 'mp4', 'mp3', 'db', 'dbf',
    'sql', 'mdb', 'log', 'err', 'tar', 'gz', 'tgz', 'rar',
    'bak', 'old', 'pem', 'crt', 'key', 'p12', 'pfx', 'yml',
    'yaml', 'env', '.gitignore', 'sh', 'bash', 'pl', 'cgi',
    'rtf', 'odt', 'odp', 'ods', 'java', 'c', 'cpp', 'cs',
    'py', 'rb', 'go', '.git', '.svn', '.hg', '.bzr', '.cvs',
    'vmdk', 'ova', 'ovf', 'iso', 'img', 'bin', 'dmg', 'mbox',
    'pst', 'ost', 'eml', '.properties', 'xml', '.htpasswd',
    '.htaccess', 'fla', 'psd', 'ai', 'indd', 'dwg', 'cad'
]

def google_search(query, start_index=1):
    """Perform a Google search and return raw JSON response."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': query,
        'start': start_index,  # Pagination: which result to start at
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        sys.exit(1)
    except Exception as err:
        print(f"An error occurred: {err}")
        sys.exit(1)

def print_search_results(items, verbose, search_term=None):
    """Print the search results with TITLE, LINK, SNIPPET, and specific METATAGS (if available)."""
    desired_meta_tags = ['moddate', 'creationdate', 'creator', 'author', 'producer']

    if items:
        for result in items:
            print(f"{BOLD}{BLUE}TITLE: {WHITE}{result['title']}")
            print(f"{BLUE}LINK: {WHITE}{result['link']}")

            if search_term and 'snippet' in result:
                highlighted_snippet = result['snippet'].replace(search_term, f"{RED}{search_term}{WHITE}")
                print(f"{YELLOW}SNIPPET: {WHITE}\"{highlighted_snippet}\"")

            if 'metatags' in result.get('pagemap', {}):
                printed_meta_tags = []
                for tag in result['pagemap']['metatags']:
                    for key in desired_meta_tags:
                        if key in tag:
                            printed_meta_tags.append(f"  {key}: {tag[key]}")

                if printed_meta_tags:
                    print(f"{YELLOW}METATAGS:{WHITE}")
                    for meta in printed_meta_tags:
                        print(meta)

            print("==============================================\n")
    else:
        if verbose:
            print(f"{BOLD}{WHITE}No results found for this query.{WHITE}\n==============================================")
        else:
            print(f"{BOLD}{WHITE}No results found.{WHITE}\n==============================================")

def print_inurl_search_results(items, verbose, search_term=None):
    """Print the search results for in-URL searches with highlighted search terms in links."""
    if items:
        for result in items:
            title = result['title']
            link = result['link']
            
            if search_term and search_term in link:
                highlighted_link = link.replace(search_term, f"{RED}{search_term}{WHITE}")
            else:
                highlighted_link = link

            print(f"{BOLD}{BLUE}TITLE: {WHITE}{title}")
            print(f"{BLUE}LINK: {WHITE}{highlighted_link}")
            print("==============================================\n")
    else:
        if verbose:
            print(f"{BOLD}{WHITE}No results found for this in-URL query.{WHITE}\n==============================================")
        else:
            print(f"{BOLD}{WHITE}No results found.{WHITE}\n==============================================")

def read_keywords_from_file(file_path):
    """Read keywords from a specified text file."""
    try:
        with open(file_path, 'r') as file:
            keywords = [line.strip() for line in file if line.strip()]
        return keywords
    except FileNotFoundError:
        print(f"{WHITE}Error: File '{file_path}' not found.{WHITE}")
        sys.exit(1)

def download_file(url, output_file):
    """Generate a wget command to download a file from the given URL."""
    wget_command = f"wget '{url}'\n"  # Use single quotes to handle spaces in URLs
    with open(output_file, 'a') as f:
        f.write(wget_command)
    
def handle_file_downloads(items):
    """Handle file downloads and append URLs to a single wget command in wget.txt."""
    file_urls = []

    for item in items:
        if 'link' in item:
            file_urls.append(item['link'])

    with open('wget.txt', 'a') as f:
        combined_wget_command = "wget " + " ".join(f"'{url}'" for url in file_urls) + "\n"
        f.write(combined_wget_command)

def main():
    parser = argparse.ArgumentParser(description='Perform Google Dork searches using the Custom Search API.')
    parser.add_argument('-IT', nargs='?', const=True, help='Perform in-text searches with keywords from a file (default terms if no file provided)')
    parser.add_argument('-IU', nargs='?', const=True, help='Perform in-URL searches with keywords from a file (default terms if no file provided)')
    parser.add_argument('-FT', nargs='?', const=True, help='Perform filetype searches with file extensions from a file (default if no file provided)')
    parser.add_argument('-e', action='store_true', help='Extract (download) all file types found into the current directory')
    parser.add_argument('-u', '--url', help='The base URL to dork (e.g., www.example.com)', required=True)
    parser.add_argument('-o', '--only-urls', action='store_true', help='Only print the URLs and skip the scan')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode, print all results including no results')
    parser.add_argument('-d', '--debug', action='store_true', help='Save raw JSON response to debug.txt')
    args = parser.parse_args()

    if args.e and (args.IT is not None or args.IU is not None):
        print(f"{RED}Error: The -e option can only be used with -FT.{WHITE}")
        sys.exit(1)

    base_url = args.url.strip().replace('http://', '').replace('https://', '')
    queries = []

    if args.IT is not None:
        if args.IT is True:
            print(f"{WHITE}No input file for in-text search provided. Using default terms.{WHITE}\n")
            queries.extend([f"site:{base_url} intext:{term}" for term in DEFAULT_IT_TERMS])
        else:
            intext_terms = read_keywords_from_file(args.IT)
            queries.extend([f"site:{base_url} intext:{term}" for term in intext_terms if term])

    if args.IU is not None:
        if args.IU is True:
            print(f"{WHITE}No input file for in-URL search provided. Using default terms.{WHITE}\n")
            queries.extend([f"site:{base_url} inurl:{term}" for term in DEFAULT_IU_TERMS])
        else:
            inurl_terms = read_keywords_from_file(args.IU)
            queries.extend([f"site:{base_url} inurl:{term}" for term in inurl_terms if term])

    if args.FT is not None:
        if args.FT is True:
            print(f"{WHITE}No input file for file types provided. Using default file types.{WHITE}\n")
            queries.extend([f"site:{base_url} filetype:{file_type}" for file_type in DEFAULT_FILE_TYPES])
        else:
            file_types = read_keywords_from_file(args.FT)
            queries.extend([f"site:{base_url} filetype:{file_type}" for file_type in file_types])

    if args.only_urls:
        print(f"\n{PURPLE}URLs being generated for queries:{WHITE}")
        for query in queries:
            print(f"{query}")
        return

    for query in queries:
        search_term = query.split('intext:')[1].strip() if 'intext:' in query else None

        if args.verbose:
            print(f"{PURPLE}Performing Google search: {query}{WHITE}")

        result_json = google_search(query)

        items = result_json.get('items', [])
        if not items and not args.verbose:
            continue

        if 'inurl:' in query:
            print_inurl_search_results(items, args.verbose, search_term)
        else:
            print_search_results(items, args.verbose, search_term)
        
        if args.e:
            handle_file_downloads(items)
        
        if args.debug:
            with open('debug.txt', 'w') as f:
                json.dump(result_json, f, indent=4)
                f.write('\n')

if __name__ == "__main__":
    print(f"{PURPLE}                                                                                                     ")
    print(f"{PURPLE}                                                                                                     ")
    print(f"{PURPLE}DDDDDDDDDDDDD             OOOOOOOOO     RRRRRRRRRRRRRRRRR   KKKKKKKKK    KKKKKKKYYYYYYY       YYYYYYY")
    print(f"{PURPLE}D::::::::::::DDD        OO:::::::::OO   R::::::::::::::::R  K:::::::K    K:::::KY:::::Y       Y:::::Y")
    print(f"{PURPLE}D:::::::::::::::DD    OO:::::::::::::OO R::::::RRRRRR:::::R K:::::::K    K:::::KY:::::Y       Y:::::Y")
    print(f"{PURPLE}DDD:::::DDDDD:::::D  O:::::::OOO:::::::ORR:::::R     R:::::RK:::::::K   K::::::KY::::::Y     Y::::::Y")
    print(f"{PURPLE}  D:::::D    D:::::D O::::::O   O::::::O  R::::R     R:::::RKK::::::K  K:::::KKKYYY:::::Y   Y:::::YYY")
    print(f"{PURPLE}  D:::::D     D:::::DO:::::O     O:::::O  R::::R     R:::::R  K:::::K K:::::K      Y:::::Y Y:::::Y   ")
    print(f"{PURPLE}  D:::::D     D:::::DO:::::O     O:::::O  R::::RRRRRR:::::R   K::::::K:::::K        Y:::::Y:::::Y    ")
    print(f"{PURPLE}  D:::::D     D:::::DO:::::O     O:::::O  R:::::::::::::RR    K:::::::::::K          Y:::::::::Y     ")
    print(f"{PURPLE}  D:::::D     D:::::DO:::::O     O:::::O  R::::RRRRRR:::::R   K:::::::::::K           Y:::::::Y      ")
    print(f"{PURPLE}  D:::::D     D:::::DO:::::O     O:::::O  R::::R     R:::::R  K::::::K:::::K           Y:::::Y       ")
    print(f"{PURPLE}  D:::::D     D:::::DO:::::O     O:::::O  R::::R     R:::::R  K:::::K K:::::K          Y:::::Y       ")
    print(f"{PURPLE}  D:::::D    D:::::D O::::::O   O::::::O  R::::R     R:::::RKK::::::K  K:::::KKK       Y:::::Y       ")
    print(f"{PURPLE}DDD:::::DDDDD:::::D  O:::::::OOO:::::::ORR:::::R     R:::::RK:::::::K   K::::::K       Y:::::Y       ")
    print(f"{PURPLE}D:::::::::::::::DD    OO:::::::::::::OO R::::::R     R:::::RK:::::::K    K:::::K    YYYY:::::YYYY    ")
    print(f"{PURPLE}D::::::::::::DDD        OO:::::::::OO   R::::::R     R:::::RK:::::::K    K:::::K    Y:::::::::::Y    ")
    print(f"{PURPLE}DDDDDDDDDDDDD             OOOOOOOOO     RRRRRRRR     RRRRRRRKKKKKKKKK    KKKKKKK    YYYYYYYYYYYYY    ")
    print(f"{PURPLE}                                                                                                     ")
    print(f"{PURPLE}                                                                                                     ")
    main()
