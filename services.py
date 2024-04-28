import csv
import random
import time
import json
import subprocess

from jinja2 import Environment, FileSystemLoader
from xlsxwriter.workbook import Workbook

def reload_nginx(host, port):
    backend_servers = []
    with open("backend_servers.txt", "r") as servers_file:
        backend_servers = [line.strip() for line in servers_file]

    # Загрузите шаблон Jinja из текущего каталога
    template_loader = FileSystemLoader(searchpath="./")
    template_env = Environment(loader=template_loader)
    template = template_env.get_template("nginx_template.j2")

    # Заполните шаблон данными
    rendered_template = template.render(backend_servers=backend_servers, host=host, port=port)

    with open("conf\\nginx.conf", "w") as config_file:
        config_file.write(rendered_template)

    # Перезапустите Nginx, если это необходимо
    subprocess.run(["nginx.exe", "-s", "reload"])

def getDataFromJSON(path):
    with open((path + ".JSON"), "r") as read_file:
        data = json.load(read_file)
    return data

def createTSV(rowsCount, tsv_file):
    with open(tsv_file, 'wt', newline='') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        song_name = ""
        band_name = ""
        upload_time = ""
        album_name = ""
        label = ""
        explicit_lyrics = True
        rating = 0.0
        num32_n = 0
        num64_id = 1234567899876543234567
        numf_chrono = 0.14 
        
        tsv_writer.writerow(["#", "Track", "Author", "Album", "Chrono", "E", "Rating", "id", "label", "Upload time"])
        for x in range(0, rowsCount):
            song_name = "R" + str(x)
            band_name = str(x) + "klaS"
            album_name = "A" + str(x)
            label = "L" + str(x)
            num32_n = num32_n + 1
            num64_id = num64_id + 1
            explicit_lyrics = not(explicit_lyrics)
            numf_chrono = 3 + random.random()
            rating = 4 + random.random()
            upload_time = time.asctime(time.localtime(time.time()))
            
            tsv_writer.writerow([num32_n, song_name, band_name, album_name, round(numf_chrono, 2), explicit_lyrics, round(rating, 1), num64_id, label, upload_time])

def createXLSX(tsv_file):
    xlsx_file = tsv_file.replace('.', '') + '.xlsx'

    workbook = Workbook(xlsx_file)
    worksheet = workbook.add_worksheet()

    tsv_reader = csv.reader(open(tsv_file, 'r'), delimiter='\t')

    for row, data in enumerate(tsv_reader):
        worksheet.write_row(row, 0, data)

    workbook.close()

def readTSV(tsv_file, s_print):
    result = []
    tsv_reader = csv.reader(open(tsv_file, 'r'), delimiter='\t')

    for row, data in enumerate(tsv_reader):
        result.append(data)

    if(s_print == True):
        print(result)
    return result

def call_createTSV(file):
    rowsCount = int(input("Enter rows count-> "))
    if(rowsCount > 9999): rowsCount = 9999
    elif(rowsCount < 0) : rowsCount = 0
    createTSV(rowsCount, file)