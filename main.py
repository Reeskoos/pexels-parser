import os
import asyncio
import httpx
from tqdm import tqdm
import json
import math

from config import API_KEY, PROXY_LOGIN, PROXY_PASS, PROXY_IP


class AsyncParser:
    HEADERS = {"Authorization": f'{API_KEY}'}
    PROXIES = {
        'https://': f'http://{PROXY_LOGIN}:{PROXY_PASS}@{PROXY_IP}',

    }

    def __init__(self, query):
        self.query = query
        self.query_str = f'https://api.pexels.com/v1/search?query={query}&per_page=80&orientation=landscape'
        self.img_dir_path = self.img_dir_manager()

    def collector(self):

        response = self.fetch_response(self.query_str)
        print(f'Connection established. Status Code: {response.status_code}')

        json_data = response.json()
        self.json_response_to_file(json_data, self.img_dir_path)

        images_count = json_data.get('total_results')

        if not json_data.get('next_page'):
            print(f'[INFO] Total images: {images_count}')
            images_urls = [item.get('src').get('original') for item in json_data.get('photos')]
            self.download(images_urls=images_urls, img_dir_path=self.img_dir_path)
        else:
            print(f'[INFO] Total images: {images_count}. Download can take some time.')
            images_urls_list = []
            for page in range(1, math.ceil(images_count / 80) + 1):
                query_str = f'{self.query_str}&page={page}'
                response = self.fetch_response(query_str)
                json_data = response.json()
                images_urls = [item.get('src').get('original') for item in json_data.get('photos')]
                images_urls_list.extend(images_urls)
            asyncio.run(self.download(images_urls_list, self.img_dir_path))

    def fetch_response(self, query_str: str) -> httpx.Response:
        """
        Collects data from input query
        Returns response.
        """
        with httpx.Client(proxies=self.PROXIES) as client:
            response = client.get(url=query_str, headers=self.HEADERS)
            if not response.status_code == 200:
                print(f'Error: Status code: {response.status_code}.')
        return response

    def json_response_to_file(self, json_data, query: str) -> None:
        """Creates result_query json file in images directory"""
        with open(f'{self.img_dir_path}/result_{query}.json', 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)
            file.close()

    def img_dir_manager(self) -> str:
        img_dir_path = '_'.join(i for i in self.query.split(' ') if i.isalnum())
        if not os.path.exists(img_dir_path):
            os.makedirs(img_dir_path)
        return img_dir_path

    async def download(self, images_urls: list[str], img_dir_path: str) -> Courootin:
        async with httpx.AsyncClient(proxies=self.PROXIES) as client:
            for item_url in tqdm(images_urls):
                response = await client.get(url=item_url)
                if not response.status_code == 200:
                    print(f'Error: Status code: {response.status_code}.')
                else:
                    with open(f'./{img_dir_path}/{item_url.split("-")[-1]}', 'wb') as file:
                        file.write(response.content)


def main():
    query = input('Enter keyword for a search: ')
    async_parser = AsyncParser(query=query)
    async_parser.collector()


if __name__ == '__main__':
    main()

"""
TODO
Сделать асинхронность везде, где возможно
возможно на загрузку она не нужна
убрать лишнее
"""
