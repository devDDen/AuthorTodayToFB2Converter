from typing import List, Union, cast

from FB2.Author import Author

from httpx import Client
from FB2 import FictionBook2

from Classes.Book import Book
from Classes.Functions import RemoveInvalidFilenameCharacters


def downloadBook(
        client: Client,
        authorized: bool,
        url: str,
        outputDir: str,
        verbose: bool,
        ):
    book: Book = Book(client)
    book.GetBookFromUrl(authorized, url)
    if verbose:
        print(book.header)
        print(
            "-----------------\nTable of Contents\n-----------------",
            end="\n",
        )
        for chapterHeader in book.header.tableOfContents:
            print(chapterHeader)
        print("End of book")
    fb2 = FictionBook2()
    fb2.titleInfo.title = book.header.title
    fb2.titleInfo.authors = cast(
        List[Union[str, Author]],
        book.header.authors,
    )
    fb2.titleInfo.annotation = book.header.annotation
    fb2.titleInfo.genres = book.header.genres
    fb2.titleInfo.lang = "ru"
    fb2.titleInfo.sequences = (
        [(book.header.sequence.name, book.header.sequence.number)]
        if book.header.sequence
        else None
    )
    fb2.titleInfo.keywords = book.header.tags
    fb2.titleInfo.coverPageImages = (
        [book.header.coverImageData]
        if book.header.coverImageData
        else None
    )
    fb2.titleInfo.date = (book.header.publicationDate, None)
    fb2.chapters = list(
        map(
            lambda chapter: (chapter.header.title, chapter.paragraphs),
            book.chapters,
        )
    )
    fb2.write(f"{outputDir}/{RemoveInvalidFilenameCharacters(fb2.titleInfo.title)}.fb2")
    print(f"Book {fb2.titleInfo.title} saved")