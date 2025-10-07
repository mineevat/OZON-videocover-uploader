import requests
import pandas as pd
import cv2
import os
import time
from PIL import Image
import numpy as np
import urllib.request
from config import *

ids, key, _ = ACCOUNTS[ACTIVE_ACCOUNT_INDEX]
HEADERS = {
    "Host": "api-seller.ozon.ru",
    "Client-Id": ids,
    "Api-Key": key,
    "Content-Type": "application/json"
}

# Загружаем список артикулов товаров (GUID-ы)
df = pd.read_excel( GUIDS_FILE, sheet_name = GUIDS_SHEET_NAME)
art_list = df['Артикул'].tolist()
print('Количество артикулов: ',len(art_list))


def create_zoom_video(image_path, video_path, frames=60):
    img = cv2.imread(image_path)
    height, width, _ = img.shape
    if height > 1920 or width > 1920: 
        img = Image.open(image_path)
        img.thumbnail(size=(1100,1100))
        img.save(image_path)
    # img = Image.open(image_path)
    # img.thumbnail(size=(1080,1080))
    # img.save(image_path)
    


    img = cv2.imread(image_path)
    height, width, _ = img.shape


    desired_width = max(height, width)
    desired_height = max(width, height)

    if height < 1080 and width < 1080:
        desired_width = 1080
        desired_height = 1080

    new_image = np.ones((desired_height, desired_width, 3), dtype=np.uint8) * 255

    x_offset = (desired_width - img.shape[1]) // 2
    y_offset = (desired_height - img.shape[0]) // 2


    new_image[y_offset:y_offset+img.shape[0], x_offset:x_offset+img.shape[1]] = img
    img = new_image
    height, width, _ = img.shape
 


    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 40.0, (width, height))

    for _ in range(40*3):
        out.write(img)

    for i in range(1, frames + 1):
        zoom_level = 1 + 0.005 * i  # Уровень зума
        M = cv2.getRotationMatrix2D((width / 2, height / 2), 0, zoom_level)
        zoomed = cv2.warpAffine(img, M, (width, height))
        out.write(zoomed)

    for i in range(frames, 0, -1):
        zoom_level = 1 + 0.005 * i  # Уровень зума
        M = cv2.getRotationMatrix2D((width / 2, height / 2), 0, zoom_level)
        zoomed = cv2.warpAffine(img, M, (width, height))
        out.write(zoomed)

    for _ in range(40*5):
        out.write(img)

    out.release()
    #cv2.destroyAllWindows()

def get_data_ozon(masv): 
    js = {
        "filter": {
            "offer_id": masv,
            "visibility": "ALL"
        },
        "limit": 1000,
        "last_id": "okVsfA==«",
        "sort_dir": "ASC"
    }

    resp_data = requests.post("https://api-seller.ozon.ru/v3/products/info/attributes", headers=HEADERS, json=js).json()
  
    for i in range(len(masv)):

        if resp_data["result"][i]['complex_attributes'] == []: 
            img = resp_data["result"][i]['images'][0]['file_name']
            resource = urllib.request.urlopen(img)
            out = open(IMAGES_FOLDER + '\\img' + str(i) + '.jpg', 'wb')
            out.write(resource.read())
            out.close()
            for a in resp_data["result"][i]['attributes']:
                if a['attribute_id'] == 8229:
                    cat = a['values'][0]['value']
            df1.loc[len(df1.index)] = [resp_data["result"][i]['offer_id'], VIDEO_PREFIX + 'img' + str(i) + '.mp4', cat]
            cat = ''
        

        elif resp_data["result"][i]['complex_attributes'] != []:
            marker = 0
            for ats in resp_data["result"][i]['complex_attributes']:
                for atri in ats['attributes']:
                    if atri['attribute_id'] == 21845:
                        marker = 1
            if marker == 0:
                img = resp_data["result"][i]['images'][0]['file_name']
                resource = urllib.request.urlopen(img)
                out = open(IMAGES_FOLDER + '\\img' + str(i) + '.jpg', 'wb')
                out.write(resource.read())
                out.close()
                for a in resp_data["result"][i]['attributes']:
                    if a['attribute_id'] == 8229:
                        cat = a['values'][0]['value']
                df1.loc[len(df1.index)] = [resp_data["result"][i]['offer_id'], VIDEO_PREFIX + 'img' + str(i) + '.mp4', cat]
                cat = ''

        else:
            print(resp_data["result"][i]['offer_id'], '  уже есть обложка')

    print('df1 = ',df1)


def upload_video_to_yandex_disk(video_path, video_name, file_path): # загружает видео, делает его публичным
    upload_url = f"https://cloud-api.yandex.net/v1/disk/resources/upload?path={YANDEX_DISK_FOLDER}/{video_name}&overwrite=true"
    headers = {
        "Authorization": f"OAuth {YANDEX_DISK_TOKEN}"
    }
    params = {
        "path": file_path
    }

    with open(video_path, "rb") as video_file:
        response = requests.get(upload_url, headers=headers)
        print('загрузка на яд', response)
        upload_data = response.json()
        #print(upload_data)

        if "href" in upload_data:
            upload_response = requests.put(upload_data["href"], data=video_file)

            if upload_response.status_code == 201:
                print("video has been uploaded on Yandex.disk successfully")
            else:
                print("error with uploadind video on Yandex.disk")
        else:
            print("error with getting a link for uploading video on Yandex.disk")

    time.sleep(2)

    response = requests.put("https://cloud-api.yandex.net/v1/disk/resources/publish", headers=headers, params=params)

    if response.status_code == 200:
        print("File published successfully!")
    else:
        print("Failed to publish file.")


def get_published_resources():
    headers = {
        "Authorization": f"OAuth {YANDEX_DISK_TOKEN}"
    }

    response = requests.get(f"https://cloud-api.yandex.net/v1/disk/resources/public?public_key={FOLDER_LINK}&limit=1000", headers=headers)

    if response.status_code == 200:
        resources = response.json()["items"]
        for resource in resources:
            df2.loc[len(df2.index)] = [resource['name'], resource['public_url']]
    else:
        print("Failed to get published resources.")

def empty_yandex_disk_folder():
    headers = {'Authorization': YANDEX_DISK_TOKEN }

    response = requests.get(f'https://cloud-api.yandex.net/v1/disk/resources?path={YANDEX_DISK_FOLDER}', headers=headers)
    files = response.json()

    for file in files['_embedded']['items']:
        file_path = file['path']
        response = requests.delete(f'https://cloud-api.yandex.net/v1/disk/resources?path={file_path}', headers=headers)
        if response.status_code == 204 :
            print(f'Файл {file_path} успешно удален')
        else:
            print(f'Ошибка при удалении файла {file_path}: {response.status_code}')

    print('yandex disk folder is empty')

def empty_trash():
    headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}" }
    response = requests.delete("https://cloud-api.yandex.net/v1/disk/trash/resources", headers=headers)

    if response.status_code == 204:
        print('trash is empty')
    elif response.status_code == 202:
        print('trash is empty')
    else:
        print("trash is not empty")


#empty_yandex_disk_folder() 
#empty_trash()


df1 = pd.DataFrame(columns=['offer_id', 'video_name', 'category'])

for k in range(0, len(art_list), 1000): # Скачиваем по артикулам картинки с товарами
    part = art_list[k:k+1000]
    if len(part) != 0:
        get_data_ozon(part)


images_list = os.listdir(IMAGES_FOLDER) # делаем из картинок видео
for image_file in images_list:
    image_path = os.path.join(IMAGES_FOLDER, image_file)
    video_path = os.path.join(VIDEOS_FOLDER, ''.join([VIDEO_PREFIX ,image_file[:-4],'.mp4']))
    create_zoom_video(image_path, video_path)


videos_list = os.listdir(VIDEOS_FOLDER) # загружаем видео на яндекс диск(только если оно имеет нужный формат) и делаем видео публичными

for vid in videos_list:
    vid1 = cv2.VideoCapture( VIDEOS_FOLDER + '\\'+vid)
    height = vid1.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid1.get(cv2.CAP_PROP_FRAME_WIDTH)
    file_info = os.stat(VIDEOS_FOLDER + '\\'+vid)
    file_size = file_info.st_size
    if int(height) >= 1080 and int(height) <= 1920 and int(width) >= 1080 and int(width) <= 1920 and file_size < 20000000:
        try:
            print('vid =' ,vid)
            video_path = VIDEOS_FOLDER + '\\' + vid
            file_path =  'disk:' + YANDEX_DISK_FOLDER +'/' + vid
            upload_video_to_yandex_disk(video_path, vid, file_path)
        except:
            print(vid ,"unuploaded")




df2 = pd.DataFrame(columns=['video_name', 'yandex_disk_link'])
get_published_resources() # получаем публичные ссылки на видео на яндекс диске

df3 = df1.merge(df2, how='inner', on='video_name') #таблица |артикул|название видео|публичная ссылка на ЯД|
df3['yandex_disk_link'] = df3['yandex_disk_link'].str.replace("yadi.sk", "disk.yandex.ru")
print(df3)
print(df3.shape[0])

with pd.ExcelWriter(TABLE_PATH, mode = 'a', engine="openpyxl", if_sheet_exists="replace") as writer:
    df3.to_excel(writer, sheet_name = TABLE_SHEET_NAME)



#далее код, отправляющий api запросы


if df3.empty == False:

    items_mas = []

    for i in range(df3.shape[0]):
        item = {
                "attributes": [
                    {
                        "complex_id": 100002,
                        "id": 21845,
                        "values": [
                            {
                                "dictionary_value_id": 0,
                                "value": df3.loc[i,'yandex_disk_link']
                            }
                        ]
                    }
                ],
                "offer_id": df3.loc[i, 'offer_id']
            }
        items_mas.append(item)

        if (i != 0 and i % 100 == 0) or i == df3.shape[0]-1: 
            jsn = { "items": [] }
            if i != df3.shape[0]-1:
                jsn['items'] = items_mas[i-100:i]
            if i == df3.shape[0]-1:
                jsn['items'] = items_mas[df3.shape[0]//100 * 100 : df3.shape[0]]
            resp = requests.post("https://api-seller.ozon.ru/v1/product/attributes/update", headers=HEADERS, json=jsn)
            print('загрузка на озон', resp)
            print(resp.json())
            print('exit')

else:
    print('df3 пуст')



print('success')
