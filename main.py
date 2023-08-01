import asyncio
import json
import math
import os

import httpx
from colorama import init, Fore
from tqdm import tqdm

from config import API_KEY, PROXY_LOGIN, PROXY_PASS, PROXY_IP
from exceptions import error_handler_decorator, EmptyInputException, SpecialCharInputException, NoImagesFoundException


class AsyncParser:
    __HEADERS = {"Authorization": f'{API_KEY}'}
    __PROXIES = {
        'https://': f'http://{PROXY_LOGIN}:{PROXY_PASS}@{PROXY_IP}',
    }

    def __init__(self, query):
        self.query = query
        self.query_str = f'https://api.pexels.com/v1/search?query={query}&per_page=80&orientation=landscape'

    async def collector(self):
        response = await self.fetch_response(self.query_str)

        json_data = response.json()
        images_count = json_data.get('total_results')

        if images_count != 0:
            img_dir_path = self.img_dir_manager()
            self.json_response_to_file(json_data, img_dir_path)

            if not json_data.get('next_page'):
                images_urls = [item.get('src').get('original') for item in json_data.get('photos')]
                self.download(images_urls, img_dir_path)
            else:
                print(f'{Fore.LIGHTYELLOW_EX}[INFO]'
                      f'{Fore.YELLOW} Total images: {images_count}. Download can take some time.')
                self.download(await self.parse_pages(images_count), img_dir_path)
        else:
            raise NoImagesFoundException

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
            raise SpecialCharInputException

        if not os.path.exists(img_dir_path):
            os.makedirs(img_dir_path)

        return img_dir_path

    def download(self, images_urls: list[str], img_dir_path: str) -> None:
        """Get response for url in given list and write it as file """
        with httpx.Client(proxies=self.__PROXIES) as client:
            for item_url in tqdm(images_urls):  # tqdm makes progress bar of downloading
                response = client.get(url=item_url)
                if not response.status_code == 200:
                    print(f'{Fore.LIGHTRED_EX} + [ERROR]{Fore.RED} Status code: {response.status_code}.')
                else:
                    with open(f'./{img_dir_path}/{item_url.split("-")[-1]}', 'wb') as file:
                        file.write(response.content)
                        file.close()

    async def get_page_images_urls(self, page) -> list[str]:
        """Gets content of given page. Returns list[urls]"""
        query_str = f'{self.query_str}&page={page}'
        response = await self.fetch_response(query_str)
        json_data = response.json()
        page_images_urls = [item.get('src').get('original') for item in json_data.get('photos')]
        return page_images_urls

    async def parse_pages(self, images_count) -> list[str]:
        """
        Creates and completes asynchronously tasks
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
          Fore.YELLOW + 'Welcome to PexelParser!\n'
                        'Do not use special characters ($%#!* etc.) in your input.')

    query = input(Fore.GREEN + 'Enter your query: ')
    if not query:
        raise EmptyInputException
    else:
        async_parser = AsyncParser(query=query)
        asyncio.run(async_parser.collector())


if __name__ == '__main__':
    main()
