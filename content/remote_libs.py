import requests
from urllib.parse import quote


def get_files_list():
    resp = requests.get('https://testgenerator-bf37c-default-rtdb.europe-west1.firebasedatabase.app/libs_list.json')
    if resp.status_code == 200:
        return resp.json()
    return []


def download_file(name):
    url = f"https://firebasestorage.googleapis.com/v0/b/testgenerator-bf37c.appspot.com/o/" \
          f"{quote(f'lib/{name}', safe='')}?alt=media"
    resp = requests.get(url, stream=True)
    if resp.status_code == 200:
        with open(f'files/{name}', 'wb') as f:
            for chunk in resp:
                f.write(chunk)


for file in get_files_list():
    print(file)
    download_file(file)
