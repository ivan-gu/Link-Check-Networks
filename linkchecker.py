"""
Ivan Gu and Chase Brown
This program finds broken links in an HTML document whose URL is provided
as a command line argument.
"""

import argparse
import urllib.request
import urllib.error
import urllib.parse
import bs4
import os.path


def check_links(url, trace):
    """
    Check the img src and a href links in a document with a given URL
    :param url: a URL, e.g. 'https://wofford.edu'
    :param trace: True if the function should print each link as it is
                  processed, False otherwise
    :return: a dictionary whose keys are the URLs in the document and whose values are
             the code returned by a request for the resource located by the URL
    :raise: urllib.error.HTTPError if the url argument is not a valid document
    """

    # Fetch the document at url
    site = urllib.request.urlopen(url)
    code = site.getcode()
    content = site.read().decode('utf-8')
    if trace:
        print(site)
        print(code)

    # Parse the URL so we can process relative links
    # parsed_url = urllib.parse.urlparse(url)

    # Dump the document into Beautiful Soup
    soup = bs4.BeautifulSoup(content, 'html.parser')

    # Find all the linked docs <a> tag
    link_set = set()
    for link in soup.find_all('a'):
        href = link.get('href')
        if trace:
            print('Found link', href)
        link_set.add(href)

    # Find all the linked images <img>
    for image in soup.find_all('img'):
        src = image.get('src')
        if trace:
            print('Found img', src)
        link_set.add(src)

    result = {}
    for link in link_set:
        # Convert any relative to an absolute
        # If not absolute, convert to absolute
        parse_result = urllib.parse.urlparse(link)
        if parse_result.scheme == '':
            url_parse = urllib.parse.urlparse(url)
            link_parse = urllib.parse.urlparse(link)
            joint_path = os.path.normpath(os.path.join(url_parse.path, link_parse.path))
            scheme = (url_parse.scheme, url_parse.netloc, joint_path, '', '', '')
            relative_link = urllib.parse.urlunparse(scheme)
        else:
            relative_link = link
        try:
            response = urllib.request.urlopen(relative_link)
            result[link] = response.getcode()
            pass
        except urllib.error.HTTPError as err:
            if trace:
                print(err.reason)
            http_error = err.getcode()
            result[link] = http_error
        except urllib.error.URLError as err:
            if trace:
                print(err.reason)
            result[link] = err
    return result                           # STUB


def main():
    """
    Parse the command line argument and then process the document
    :return: None
    """

    # Parse the command line arguments to get a URL and the trace flag setting
    ap = argparse.ArgumentParser(prog='link_checker', description='Link checker')
    ap.add_argument('url',
                    metavar='url',
                    type=str,
                    help='the URL of the document')
    ap.add_argument('-t',
                    '--trace',
                    action='store_true',
                    help='display each link when first checked')

    args = ap.parse_args()
    url = args.url
    trace = args.trace

    # Check the links
    result = check_links(url, trace)

    # Print the findings
    row_format = '{:>4}\t{}'
    print(row_format.format("Code", "Link"))
    for url, code in result.items():
        print(row_format.format(code, url))
    print()
    print('{} distinct links processed'.format(len(result)))


if __name__ == '__main__':
    main()
