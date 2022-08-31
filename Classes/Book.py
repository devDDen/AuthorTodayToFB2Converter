from Classes.Functions import SearchGroupOne
from httpx import Client
from typing import List

from .BookHeader import BookHeader
from .Chapter import Chapter
from .Dataclasses import ChapterHeader, User


class Book:
    header: BookHeader
    client: Client
    chapters: List[Chapter]

    def __init__(self, client: Client):
        self.client = client
        self.header = BookHeader()

    def GetBookFromUrl(self, authorized: bool, url: str):
        self.header.GetBookHeaderFromUrl(url, self.client)
        self.GetBookChapters(authorized)

    def GetBookChapters(self, authorized: bool) -> List[Chapter]:
        self.chapters = []
        user = User("", "", Chapter.GetUserId(self.client)) if authorized else None
        if len(self.header.tableOfContents) > 1:
            self.getMultipleChapters(user)
        else:
            self.getSingleChapter(user)
        return self.chapters

    def getMultipleChapters(self, user: User):
        for chapterHeader in self.header.tableOfContents:
            self.chapters.append(
                self.GetBookChapter(
                    self.header.GetChapterDataUrl(chapterHeader),
                    chapterHeader,
                    user,
                )
            )

    def getSingleChapter(self, user: User):
        readerPage = self.client.get(self.header.GetReaderUrl())
        readerPage.raise_for_status()
        chapterId = int(SearchGroupOne(r"chapterId: (\d+),", readerPage.text))
        chapterHeader = ChapterHeader(self.header.title, chapterId)
        self.chapters.append(
            self.GetBookChapter(
                self.header.GetChapterDataUrl(chapterHeader),
                chapterHeader,
                user,
            )
        )

    def GetBookChapter(
        self, url: str, chapterHeader: ChapterHeader, user: User
    ) -> Chapter:
        chapter = Chapter(chapterHeader, self.client, user)
        chapter.GetChapterFromUrl(url)
        return chapter
