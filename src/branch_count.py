"""
Optional helper — scrape service-center (branch) counts per region from the
operators' websites and print them. Not part of the pipeline: the numbers are
copied by hand into data/external/employee_count_*.xlsx.

Run:   python src/branch_count.py      (needs internet, requests, beautifulsoup4)
"""
import requests
import re
from bs4 import BeautifulSoup
from collections import defaultdict

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,hy;q=0.8',
}

ALL_REGIONS = [
    'Yerevan', 'Aragatsotn', 'Ararat', 'Armavir', 'Gegharkunik',
    'Kotayk', 'Lori', 'Shirak', 'Syunik', 'Tavush', 'Vayots Dzor',
]


def scrape_viva():
    hy_to_en = {
        'Երևան': 'Yerevan',
        'Արագածոտն': 'Aragatsotn',
        'Արարատ': 'Ararat',
        'Արմավիր': 'Armavir',
        'Գեղարքունիք': 'Gegharkunik',
        'Լոռի': 'Lori',
        'Կոտայք': 'Kotayk',
        'Շիրակ': 'Shirak',
        'Սյունիք': 'Syunik',
        'Վայոց Ձոր': 'Vayots Dzor',
        'Տավուշ': 'Tavush',
    }
    r = requests.get(
        'https://www.viva.am/Individual-customers/help/viva-service-centers',
        headers=HEADERS,
        timeout=15
    )
    soup = BeautifulSoup(r.text, 'html.parser')

    counts = {}
    total = 0
    for group in soup.find_all(class_='faq__group'):
        region_hy = group.find(class_='faq__group-question').get_text(strip=True)
        branches = group.find_all('table', class_='service-block')
        region = hy_to_en.get(region_hy, region_hy)
        counts[region] = len(branches)
        total += len(branches)
        print(f'  {region}: {len(branches)} branches')
        for b in branches:
            address = b.find('th').get_text(strip=True)
            print(f'      - {address}')
    print(f'  TOTAL: {total}\n')
    return counts


def scrape_ucom():
    r = requests.get(
        'https://www.ucom.am/en/ucom-service-centers',
        headers=HEADERS,
        timeout=15
    )

    branch_pattern = re.compile(
        r'<div class="branch_block"'
        r'[^>]*data-region="([^"]*)"'
        r'[^>]*data-subregion="([^"]*)"'
        r'[^>]*>.*?'
        r'<div class="branch_address">\s*(.*?)\s*</div>',
        re.DOTALL
    )

    branches = branch_pattern.findall(r.text)
    regions = defaultdict(list)
    for region, subregion, address in branches:
        clean = re.sub(r'\s+', ' ', address).strip()
        regions[region].append((subregion, clean))

    counts = {}
    for region, items in regions.items():
        normalized = region.replace('_', ' ')
        counts[normalized] = len(items)
        print(f'  {region}: {len(items)} branches')
        for subregion, address in items:
            print(f'      [{subregion}] {address}')
    print(f'  TOTAL: {sum(len(v) for v in regions.values())}\n')
    return counts


def scrape_team():
    city_map = {
        '1': 'Aragatsotn', '2': 'Ararat', '3': 'Armavir', '4': 'Gegharkunik',
        '5': 'Lori', '6': 'Kotayk', '7': 'Shirak', '8': 'Syunik',
        '9': 'Tavush', '10': 'Vayots Dzor', '11': 'Yerevan',
    }
    # NOTE: this is Ucom's URL — replace it with Team's service-center page
    r = requests.get(
        'https://www.ucom.am/en/ucom-service-centers',
        headers=HEADERS,
        timeout=15
    )
    soup = BeautifulSoup(r.text, 'html.parser')

    branch_divs = soup.find_all('div', class_='map-box__info')
    regions = defaultdict(list)

    for branch in branch_divs:
        city_id = branch.get('data-city', '')
        region = city_map.get(city_id, f'Unknown ({city_id})')
        raw = branch.get('data-lng-2', '') or branch.get('data-lng-1', '')
        address = re.split(
            r'\s+(?:[Сс]\s+пон|[Пп]онедельник|[Еe]жедневно|24/7|\d{1,2}:\d{2})',
            raw
        )[0].strip()
        if not address:
            address = raw.strip()
        regions[region].append(address)

    counts = {}
    for region in sorted(regions):
        items = regions[region]
        counts[region] = len(items)
        print(f'  {region}: {len(items)} branches')
        for addr in items:
            print(f'      - {addr}')
    print(f'  TOTAL: {sum(len(v) for v in regions.values())}\n')
    return counts


def main():
    print('=' * 50)
    print('VIVA SERVICE CENTERS')
    print('=' * 50)
    viva = scrape_viva()

    print('=' * 50)
    print('UCOM SERVICE CENTERS')
    print('=' * 50)
    ucom = scrape_ucom()

    print('=' * 50)
    print('TEAM SERVICE CENTERS')
    print('=' * 50)
    team = scrape_team()

    print('=' * 50)
    print('COVERAGE BY REGION')
    print('=' * 50)
    print(f"{'Region':<20} {'Viva':>6} {'Ucom':>6} {'Team':>8}")
    print('-' * 42)
    for region in ALL_REGIONS:
        v = viva.get(region, '-')
        u = ucom.get(region, '-')
        t = team.get(region, '-')
        print(f"{region:<20} {str(v):>6} {str(u):>6} {str(t):>8}")
    print('-' * 42)
    print(f"{'TOTAL':<20} {sum(viva.values()):>6} {sum(ucom.values()):>6} {sum(team.values()):>8}")


if __name__ == "__main__":
    main()