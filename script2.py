import asyncio
import aiohttp
import aiofiles
import os
import re
import sys

from aiohttp.web_exceptions import HTTPError
from bs4 import BeautifulSoup


url = 'https://apps.irs.gov/app/picklist/list/priorFormPublication.html'
step = 200
params = {
    'resultsPerPage': 200,
    'sortColumn': 'sortOrder',
    'indexOfFirstRow': 0,
    'criteria': '',
    'value': '',
    'isDescending': 'false'
}
links = []
download_dir = 'downloads'


def create_dir(dirname):
    path = os.getcwd()
    path = os.path.join(path, dirname)
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


async def get_files_count(session) -> int:
    try:
        response = await session.request(method='GET', url=url)
        response_text = await response.text()
        soup = BeautifulSoup(response_text, 'html.parser')
        tag_text = soup.find("th", class_="ShowByColumn").text
        files_count = re.findall(r'(\d+),(\d+)', tag_text)
        files_count = ''.join(files_count[0])
        return int(files_count)
    except HTTPError as http_err:
        print(f"HTTP error: {http_err}")
    except Exception as err:
        print(f"An error: {err}")


async def get_data(index_of_first_row, session) -> None:
    try:
        params['indexOfFirstRow'] = index_of_first_row
        response = await session.request(method='GET', url=url, params=params)
        response_text = await response.text()
        soup = BeautifulSoup(response_text, 'html.parser')
        table = soup.find("table", attrs={"class": "picklist-dataTable"})
        rows = table.findAll("tr")[1::]
        for row in rows:
            row_handler(row)
    except HTTPError as http_err:
        print(f"HTTP error: {http_err}")
    except Exception as err:
        print(f"An error: {err}")


def row_handler(row) -> None:
    columns = row.findAll('td')
    link = columns[0].find('a')
    form_number = columns[0].find('a').contents[0].strip()
    if form_number.find('/') > 0: form_number = form_number.replace('/', '_')
    year = columns[2].contents[0].strip()
    path = os.path.join(download_dir, form_number)
    filename = os.path.join(path, f"{form_number}-{year}.pdf")
    create_dir(path)
    links.append([filename, link['href']])


async def get_forms_info():
    async with aiohttp.ClientSession() as session:
        count = await get_files_count(session)
        await asyncio.gather(*[get_data(i, session) for i in range(0, count, 200)])


async def download_file(semaphore, link, session, filename):
    async with semaphore:
        try:
            response = await session.request(method='GET', url=link)
            content = await response.read()
            async with aiofiles.open(filename, "+wb") as f:
                await f.write(content)
        except HTTPError as http_err:
            print(f"HTTP error: {http_err}")
        except Exception as err:
            print(f"An error: {err}")


async def download():
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(100)
        await asyncio.gather(*[download_file(semaphore, link, session, filename) for filename, link in links])


if __name__ == '__main__':
    create_dir(download_dir)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_forms_info())
    loop.run_until_complete(download())
