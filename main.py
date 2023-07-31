import os
import asyncio
import httpx
import json
import math

from colorama import init, Fore
from tqdm import tqdm

from config import API_KEY, PROXY_LOGIN, PROXY_PASS, PROXY_IP


class AsyncParser:
    __HEADERS = {"Authorization": f'{API_KEY}'}
    __PROXIES = {
        'https://': f'http://{PROXY_LOGIN}:{PROXY_PASS}@{PROXY_IP}',
    }

    def __init__(self, query):
        self.query = query
        self.query_str = f'https://api.pexels.com/v1/search?query={query}&per_page=80&orientation=landscape'
        self.img_dir_path = self.img_dir_manager()

    async def collector(self):
        response = await self.fetch_response(self.query_str)
        print(f'{Fore.YELLOW}[INFO] Connection established. Status Code: {Fore.GREEN + str(response.status_code)}')

        json_data = response.json()
        images_count = json_data.get('total_results')
        self.json_response_to_file(json_data, self.img_dir_path)

        print(f'{Fore.YELLOW}[INFO] Total images: {images_count}. Download can take some time.')

        if not json_data.get('next_page'):
            images_urls = [item.get('src').get('original') for item in json_data.get('photos')]
            self.download(images_urls, self.img_dir_path)
        else:
            self.download(await self.parse_pages(images_count), self.img_dir_path)

    async def fetch_response(self, query_str: str) -> httpx.Response:
        async with httpx.AsyncClient(proxies=self.__PROXIES) as client:
            response = await client.get(url=query_str, headers=self.__HEADERS)
            if not response.status_code == 200:
                print(f'{Fore.RED}[Error] Status code: {response.status_code}.')
        return response

    def json_response_to_file(self, json_data, query: str) -> None:
        with open(f'{self.img_dir_path}/result_{query}.json', 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)
            file.close()

    def img_dir_manager(self) -> str:
        img_dir_path = '_'.join(i for i in self.query.split(' ') if i.isalnum())
        if not os.path.exists(img_dir_path):
            os.makedirs(img_dir_path)
        return img_dir_path

    def download(self, images_urls: list[str], img_dir_path: str):
        with httpx.Client(proxies=self.__PROXIES) as client:
            for item_url in tqdm(images_urls):
                response = client.get(url=item_url)
                if not response.status_code == 200:
                    print(f'Error: Status code: {response.status_code}.')
                else:
                    with open(f'./{img_dir_path}/{item_url.split("-")[-1]}', 'wb') as file:
                        file.write(response.content)

    async def get_page_images_urls(self, page) -> list[str]:
        query_str = f'{self.query_str}&page={page}'
        response = await self.fetch_response(query_str)
        json_data = response.json()
        page_images_urls = [item.get('src').get('original') for item in json_data.get('photos')]
        return page_images_urls

    async def parse_pages(self, images_count) -> list[str]:
        tasks = set()
        for page in range(1, math.ceil(images_count / 80) + 1):
            task = asyncio.create_task(self.get_page_images_urls(page))
            tasks.add(task)

        images_urls = [item for sublist in await asyncio.gather(*tasks) for item in sublist]

        return images_urls


def main():
    try:
        query = input('Enter keyword for a search: ')
        if not query:
            raise ValueError

    except ValueError:
        print(Fore.RED + '[ERROR]', 'Input value cannot be empty.')

    else:
        init(autoreset=True)  # colorama core
        async_parser = AsyncParser(query=query)
        asyncio.run(async_parser.collector())


if __name__ == '__main__':
    main()
