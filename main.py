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
    parser = argparse.ArgumentParser()
    inputGroup = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument(
        '-l',
        '--login',
        type=str,
        help='Email to login'
    )
    parser.add_argument(
        '-p',
        '--password',
        type=str,
        help='Password to login'
    )
    parser.add_argument(
        '-c',
        '--credentials',
        type=str,
        help='Path to the folder with email.txt, password.txt'
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        help='Path to the output folder',
    )
    inputGroup.add_argument(
        '-u',
        '--url-list',
        nargs='+',
        help="List of urls to download",
    )
    inputGroup.add_argument(
        '-i',
        '--input-file',
        help="Input file with urls to download",
    )
    args = parser.parse_args()

    fileDir = path.dirname(argv[0])
    outputDir = fileDir + "/Output" if not args.output else args.output
    makedirs(outputDir, exist_ok=True)

    client = Client()
    client._timeout = Timeout(3)
    client.base_url = Pages.main
    SetSessionHeaders(client)
    credentialsFolder = fileDir + "/PrivateConfig" if not args.credentials else args.credentials
    emailPath = credentialsFolder + "/email.txt"
    passwordPath = credentialsFolder + "/password.txt"
    authorized = False
    if (args.login and args.password):
        email = args.login
        password = args.password
        authorized = Authorize(client, email, password)
    elif (path.exists(emailPath)
        and path.exists(passwordPath)):
        with open(emailPath) as f:
            email = f.readline()
        with open(passwordPath) as f:
            password = f.readline()
        authorized = Authorize(client, email, password)

    if authorized:
        print(f"Authorized as {email}")
    else:
        print("You are not authorized")

    t = time()
    if args.url_list:
        for url in args.url_list:
            downloadBook(client, authorized, sub('http://|https://|author.today/', '', url), outputDir)
    elif (args.input_file):
        with open(args.input_file, 'r') as f:
            for line in f:
                url = line.strip()
                if url == '':
                    continue
                try:
                    downloadBook(client, authorized, sub('http://|https://|author.today/', '', url), outputDir)
                except Exception:
                    print(f"Fail to download {line}")
    if authorized:
        Logoff(client)
    print(f"All requests took {time() - t} seconds.")
