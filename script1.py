import asyncio
import aiohttp
import json
import re

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

forms = {}
final_forms = []


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
    form_number = columns[0].find('a').contents[0].strip()
    form_title = columns[1].contents[0].strip()
    year = columns[2].contents[0].strip()
    form_data = {
        'form_title': form_title,
        'year': year
    }
    if form_number not in forms:
        forms[form_number] = []
    forms[form_number].append(form_data)


def handle_forms() -> None:
    max_year = 0
    min_year = 10000

    for key, value in forms.items():
        for data in value:
            if max_year < int(data['year']):
                max_year = int(data['year'])
            if min_year > int(data['year']):
                min_year = int(data['year'])

        form_data = {
            'form_number': key,
            'form_title': value[0]['form_title'],
            'min_year': min_year,
            'max_year': max_year
        }

        final_forms.append(form_data)
        max_year = 0
        min_year = 10000


def write_file() -> None:
    with open('results.txt', 'w') as file:
        print(json.dumps(final_forms, indent=4))
        json.dump(final_forms, file, indent=4)


async def main():
    async with aiohttp.ClientSession() as session:
        count = await get_files_count(session)
        await asyncio.gather(*[get_data(i, session) for i in range(0, count, 200)])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    handle_forms()
    write_file()
