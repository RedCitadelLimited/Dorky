# Dorky

Dorky is a command-line Google dorking tool that uses the Google Custom Search API.

Instead of scraping Google search result pages, Dorky sends searches through the official Google API. This makes the results cleaner, more reliable, and avoids the mess that comes with scraping Google directly.

## Requirements

Dorky requires:

- Python 3
- A Google API key
- A Google Custom Search Engine ID
- The `requests` Python module

Install the required Python module:

```bash
pip install requests
```

## Google API Setup

To use Dorky, you need your own:

- Google API key
- Google Custom Search Engine ID

Once you have these, add them to the script:

```python
api_key = 'YOUR_API_KEY'
search_engine_id = 'YOUR_CUSTOM_SEARCH_ENGINE_ID'
```

Dorky uses these values to query the Google Custom Search API.

## What Dorky Does

Dorky performs Google dork searches from the command line against a target domain.

It can search for:

- Keywords in page text using `intext:`
- Keywords in URLs using `inurl:`
- Specific file types using `filetype:`
- Default keyword lists
- Custom keyword lists from text files
- Default file extension lists
- Custom file extension lists from text files

It can also:

- Print search results with titles, links, snippets, and selected metadata
- Highlight matched search terms in results
- Show only the generated Google dork queries without running them
- Save raw API responses to a debug file
- Generate a `wget.txt` file containing download commands for discovered files

## Usage

Basic syntax:

```bash
python dorky.py -u <target-domain> [options]
```

Example:

```bash
python dorky.py -u example.com -IT
```

The target URL can be supplied with or without `http://` or `https://`.

For example, these are treated the same:

```bash
python dorky.py -u example.com -IT
python dorky.py -u https://example.com -IT
python dorky.py -u http://example.com -IT
```

## Options

| Option | Description |
|---|---|
| `-u`, `--url` | Target domain to search. This is required. |
| `-IT` | Run `intext:` searches. Uses default terms if no file is supplied. |
| `-IU` | Run `inurl:` searches. Uses default terms if no file is supplied. |
| `-FT` | Run `filetype:` searches. Uses default file types if no file is supplied. |
| `-e` | Generate download commands for filetype results. Only works with `-FT`. |
| `-o`, `--only-urls` | Print the generated dork queries without running the searches. |
| `-v`, `--verbose` | Print verbose output, including searches with no results. |
| `-d`, `--debug` | Save the raw Google API JSON response to `debug.txt`. |

## In-Text Searches

Use `-IT` to search for keywords within indexed page text.

If no keyword file is supplied, Dorky uses the default terms:

```text
admin
password
username
```

Example:

```bash
python dorky.py -u example.com -IT
```

This generates searches such as:

```text
site:example.com intext:admin
site:example.com intext:password
site:example.com intext:username
```

You can also supply your own keyword file:

```bash
python dorky.py -u example.com -IT keywords.txt
```

Example `keywords.txt`:

```text
confidential
internal
backup
private
```

## In-URL Searches

Use `-IU` to search for keywords within indexed URLs.

If no keyword file is supplied, Dorky uses the default terms:

```text
admin
password
username
```

Example:

```bash
python dorky.py -u example.com -IU
```

This generates searches such as:

```text
site:example.com inurl:admin
site:example.com inurl:password
site:example.com inurl:username
```

You can also supply your own keyword file:

```bash
python dorky.py -u example.com -IU url-keywords.txt
```

Example `url-keywords.txt`:

```text
login
portal
dashboard
backup
```

## Filetype Searches

Use `-FT` to search for indexed files by extension.

Example:

```bash
python dorky.py -u example.com -FT
```

If no filetype list is supplied, Dorky uses a built-in list of common and sensitive file extensions, including:

```text
pdf
doc
docx
xls
xlsx
zip
bak
txt
config
web.config
ini
js
php
html
sql
log
pem
crt
key
p12
pfx
env
git
svn
htpasswd
htaccess
vmdk
pst
ost
eml
xml
```

You can also supply your own filetype list:

```bash
python dorky.py -u example.com -FT filetypes.txt
```

Example `filetypes.txt`:

```text
pdf
docx
xlsx
bak
sql
env
log
```

## Extracting File Results

The `-e` option creates a `wget.txt` file containing a `wget` command for files found during filetype searches.

Example:

```bash
python dorky.py -u example.com -FT -e
```

This writes discovered file URLs to:

```text
wget.txt
```

The generated file can then be reviewed before downloading anything.

The `-e` option only works with `-FT`.

This is valid:

```bash
python dorky.py -u example.com -FT -e
```

These are not valid:

```bash
python dorky.py -u example.com -IT -e
python dorky.py -u example.com -IU -e
```

## Preview Queries Without Searching

Use `-o` or `--only-urls` to print the dork queries without sending them to the API.

Example:

```bash
python dorky.py -u example.com -IT -o
```

Example output:

```text
site:example.com intext:admin
site:example.com intext:password
site:example.com intext:username
```

This is useful for checking what Dorky will search before running it.

## Verbose Mode

Use `-v` or `--verbose` to print additional output.

Example:

```bash
python dorky.py -u example.com -FT -v
```

Verbose mode shows the search being performed and also prints when no results are found.

## Debug Mode

Use `-d` or `--debug` to save the raw Google Custom Search API response to `debug.txt`.

Example:

```bash
python dorky.py -u example.com -IT -d
```

This is useful for troubleshooting or reviewing the full API response.

## Example Commands

Run default in-text searches:

```bash
python dorky.py -u example.com -IT
```

Run default in-URL searches:

```bash
python dorky.py -u example.com -IU
```

Run default filetype searches:

```bash
python dorky.py -u example.com -FT
```

Run filetype searches and generate `wget.txt`:

```bash
python dorky.py -u example.com -FT -e
```

Run in-text searches using a custom keyword file:

```bash
python dorky.py -u example.com -IT keywords.txt
```

Run in-URL searches using a custom keyword file:

```bash
python dorky.py -u example.com -IU url-keywords.txt
```

Run filetype searches using a custom filetype list:

```bash
python dorky.py -u example.com -FT filetypes.txt
```

Preview generated searches without running them:

```bash
python dorky.py -u example.com -FT -o
```

Run a verbose filetype search:

```bash
python dorky.py -u example.com -FT -v
```

Run a search and save the raw API response:

```bash
python dorky.py -u example.com -IT -d
```

## Output

For standard searches, Dorky prints:

- Title
- Link
- Snippet
- Selected metadata, where available

The metadata Dorky attempts to show includes:

```text
moddate
creationdate
creator
author
producer
```

For in-URL searches, Dorky prints:

- Title
- Link

Matched terms in links or snippets are highlighted in the terminal output.

## Notes

Dorky does not scrape Google search result pages.

It uses the Google Custom Search API, which requires your own API key and Custom Search Engine ID.

API usage may be subject to Google quotas, pricing, and search engine configuration.

## Intended Use

Dorky is intended for authorised security testing, reconnaissance, and exposure review against domains you own or have permission to assess.
