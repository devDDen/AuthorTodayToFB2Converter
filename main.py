from time import time

from os import path, makedirs
from sys import argv

import argparse
from re import sub

from httpx import Client, Timeout
from Classes.Dataclasses import Pages

from Classes.Functions import Authorize, Logoff, SetSessionHeaders
from Classes.DownloadBook import downloadBook

if __name__ == "__main__":
    appDir = path.dirname(argv[0])
    parser = argparse.ArgumentParser()
    urlGroup = parser.add_mutually_exclusive_group(required=True)
    credentialsGroup = parser.add_mutually_exclusive_group(required=True)
    lpGroup = credentialsGroup.add_argument_group()
    lpGroup.add_argument(
        '-l',
        '--login',
        type=str,
        help='Email to login'
    )
    lpGroup.add_argument(
        '-p',
        '--password',
        type=str,
        help='Password to login'
    )
    credentialsGroup.add_argument(
        '-c',
        '--credentials',
        type=str,
        default=(appDir + '/PrivateConfig'),
        help='Path to the folder with email.txt, password.txt'
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        help='Path to the output folder'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        default=False,
        action="store_true",
        help="Show book chapters"
    )
    urlGroup.add_argument(
        '-u',
        '--url-list',
        nargs='+',
        help="List of urls to download"
    )
    urlGroup.add_argument(
        '-i',
        '--input-file',
        help="Input file with urls to download"
    )
    args = parser.parse_args()

    
    outputDir = appDir + "/Output" if not args.output else args.output
    makedirs(outputDir, exist_ok=True)

    client = Client()
    client._timeout = Timeout(3)
    client.base_url = Pages.main
    SetSessionHeaders(client)

    credentialsFolder = args.credentials
    emailPath = credentialsFolder + "/email.txt"
    passwordPath = credentialsFolder + "/password.txt"
    authorized = False
    if (args.login and args.password):
        email = args.login
        password = args.password
        authorized = Authorize(client, email, password)
    elif (path.exists(emailPath) and path.exists(passwordPath)):
        with open(emailPath) as f:
            email = f.readline()
        with open(passwordPath) as f:
            password = f.readline()
        if (email != '' and password != ''):
            authorized = Authorize(client, email, password)

    if authorized:
        print(f"Authorized as {email}")
    else:
        print("You are not authorized")

    url_regexp = '(http://|https://)author\.today/(work|reader)'
    t = time()
    if args.url_list:
        for url in args.url_list:
            try:
                downloadBook(
                    client,
                    authorized,
                    sub(url_regexp, '', url),
                    outputDir,
                    args.verbose)
            except Exception:
                    print(f"Fail to download {url}")
    elif (args.input_file):
        with open(args.input_file, 'r') as f:
            for line in f:
                url = line.strip()
                if url == '':
                    continue
                try:
                    downloadBook(
                        client,
                        authorized,
                        sub(url_regexp, '', url),
                        outputDir,
                        args.verbose)
                except Exception:
                    print(f"Fail to download {line}")
    if authorized:
        Logoff(client)
    print(f"All requests took {time() - t} seconds.")
