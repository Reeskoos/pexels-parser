import asyncio

import aiofiles
import httpx
import json
import math
import os

from colorama import init, Fore
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from config import API_KEY, PROXY_LOGIN, PROXY_PASS, PROXY_IP
from exceptions import error_handler_decorator, EmptyInputError, SpecialCharInputError, NoImagesFoundError


class AsyncParser:
    __HEADERS = {"Authorization": f'{API_KEY}'}
    __PROXIES = {
        'https://': f'http://{PROXY_LOGIN}:{PROXY_PASS}@{PROXY_IP}',
    }

    def __init__(self, query):
        self.query = query
        self.query_str = f'https://api.pexels.com/v1/search?query={query}&per_page=80&orientation=landscape'

    async def collector(self) -> None:
        """Start full cycle of parsing"""
        response = await self.fetch_response(self.query_str)

        json_data = response.json()
        images_count = json_data.get('total_results')
        if images_count != 0:
            # if where are images creates directory + result_query.json
            img_dir_path = self.img_dir_manager()
            self.json_response_to_file(json_data, img_dir_path)

            print(f'{Fore.LIGHTYELLOW_EX}[INFO]'
                  f'{Fore.YELLOW} Total images: {images_count}. Download can take some time.')

            # checking for next page if True: parse all pages and start downloading.
            if not json_data.get('next_page'):
                images_urls = await self.get_page_images_urls(page=1)
            else:
                images_urls = await self.parse_pages(images_count)
            await self.download_urls_list(images_urls, img_dir_path)
        else:
            raise NoImagesFoundError

    async def fetch_response(self, query_str: str) -> httpx.Response:
        """ Get and return response for given url."""
        async with httpx.AsyncClient(proxies=self.__PROXIES) as client:
            response = await client.get(url=query_str, headers=self.__HEADERS)
            if not response.status_code == 200:
                print(f'{Fore.RED}[Error] Status code: {response.status_code}.')
        return response

    def json_response_to_file(self, json_data, img_dir_path: str) -> None:
        """Creates a JSON file result_{query} in query directory."""
        with open(f'{img_dir_path}/result_{self.query}.json', 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)
            file.close()

    def img_dir_manager(self) -> str:
        """
        Validates given query for special chars.
        Creates directory and returns its path as string.
        """
        img_dir_path = '_'.join(i for i in self.query.split(' ') if i.isalnum())
        if not img_dir_path:
            raise SpecialCharInputError

        if not os.path.exists(img_dir_path):
            os.makedirs(img_dir_path)

        return img_dir_path

    async def download(self, img_url: str, img_dir_path: str) -> None:
        """Downloads image by url"""
        response = await self.fetch_response(query_str=img_url)
        async with aiofiles.open(f'./{img_dir_path}/{img_url.split("-")[-1]}', 'wb') as file:
            await file.write(response.content)
            await file.close()

    async def download_urls_list(self, images_urls: list[str], img_dir_path: str):
        """Asynchronously download list[urls] by 10 in one time"""
        tasks = set()
        for url in tqdm(images_urls):
            task = asyncio.create_task(self.download(url, img_dir_path))
            tasks.add(task)
            if len(tasks) == 10:
                await asyncio.gather(*tasks)
                tasks.clear()
        if tasks:
            await asyncio.gather(*tasks)

    async def get_page_images_urls(self, page: int) -> list[str]:
        """Gets all images urls of given page. Returns list[urls]"""
        query_str = f'{self.query_str}&page={page}'
        response = await self.fetch_response(query_str)
        json_data = response.json()
        page_images_urls = [item.get('src').get('original') for item in json_data.get('photos')]
        return page_images_urls

    async def parse_pages(self, images_count: int) -> list[str]:
        """
        Creates and completes async tasks
        Return list of urls for download.
        """
        tasks = set()
        for page in range(1, math.ceil(images_count / 80) + 1):
            task = asyncio.create_task(self.get_page_images_urls(page))
            tasks.add(task)

        # Takes asyncio.gather() -> list[list], makes images_urls flat list.
        images_urls = [item for sublist in await asyncio.gather(*tasks) for item in sublist]

        return images_urls


@error_handler_decorator
def main():
    init(autoreset=True)  # colorama core

    print(Fore.LIGHTYELLOW_EX + '[INFO]',
          Fore.YELLOW + 'Welcome to PexelsParser!\n'
                        'Do not use special characters ($%#!* etc.) in your input.')

    query = input(Fore.GREEN + 'Enter your query: ')
    if not query:
        raise EmptyInputError
    else:
        async_parser = AsyncParser(query=query)
        asyncio.run(async_parser.collector())


if __name__ == '__main__':
    main()
