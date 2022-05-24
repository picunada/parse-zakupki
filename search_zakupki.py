import datetime as DT
import pandas as pd

import ftplib

from io import BytesIO
from zipfile import ZipFile
# TODO: если не найдено - то лог архивов с размером

HOSTNAME44 = "ftp.zakupki.gov.ru"
USERNAME44 = "free"
PASSWORD44 = "free"

HOSTNAME223 = "ftp.zakupki.gov.ru"
USERNAME223 = "fz223free"
PASSWORD223 = "fz223free"

SUBJECTS44 = ['kraj', 'Resp', 'obl', 'AO', 'Moskva', 'ERUZ', 'g']
SUBJECTS223 = ["okrug", "krai", "obl", "Resp", "Sevastopol", "Sankt-Peterburg", "AO", "Respublika", "Moskva", "g"]
# FZ = {"44": 44, "223": 223}
# TODO: добавить по 223фз


def get_params_from_user():
    # TODO: валидация
    DATE = input("date: ")
    REGION = input("region: ")
    NUMBER = int(input("number: "))
    # 32211403753
    FZ = int(input("fz: "))
    if FZ == 223:
        FOLDER = input("folder: ")
        return {"date": DATE, "region": REGION, "number": NUMBER, "fz": FZ, "folder": FOLDER}
    else:
        return {"date": DATE, "region": REGION, "number": NUMBER, "fz": FZ}


def get_date(filename, range_date):
    if params_from_user["fz"] == 44:
        timestamp = ftp_server44.sendcmd("MDTM " + filename)
    else:
        timestamp = ftp_server223.sendcmd("MDTM " + filename)
    time = DT.datetime.strptime(timestamp[4:], "%Y%m%d%H%M%S").strftime("%Y-%m-%d")
    print(filename)
    if time in range_date:
        return True


def parse(filename):
    with open('buffer.zip', 'wb') as file:
        if params_from_user["fz"] == 44:
            ftp_server44.retrbinary(F'RETR {filename}', file.write)
        else:
            ftp_server223.retrbinary(F'RETR {filename}', file.write)

    with open('buffer.zip', 'rb') as file:
        zipfile = ZipFile(BytesIO(file.read()))

        for name in zipfile.namelist():
            if name.endswith('.sig'):
                # игнорим sig из currMonth
                continue
            xml = ''
            for line in zipfile.open(name).readlines():
                xml += line.decode('utf-8')
            if str(params_from_user["number"]) in xml:
                print(xml)
                return [filename, name]
            else:
                continue


def return_result(filename, filter_date):
    # if filename.endswith(".zip"):
        print(f"filterdate: {filter_date}")
        if filter_date:
            zakupka = parse(filename)
            if zakupka is not None:
                print(f"поиск закончился. закупка: {zakupka[1]}.\nархив: {zakupka[0]}")
                return zakupka


if __name__ == "__main__":
    params_from_user = get_params_from_user()
    print("Поиск начался. Пожалуйста, подождите...")
    ftp_server44 = ftplib.FTP(HOSTNAME44, USERNAME44, PASSWORD44)
    ftp_server44.encoding = "utf-8"

    ftp_server223 = ftplib.FTP(HOSTNAME223, USERNAME223, PASSWORD223)
    ftp_server223.encoding = "utf-8"

    start_date = DT.datetime.strptime(params_from_user['date'], "%Y%m%d").date()
    end_date = DT.datetime.strptime(DT.datetime.today().strftime("%Y%m%d"), "%Y%m%d").date()
    range_date = pd.date_range(
        min(start_date, end_date),
        max(start_date, end_date)
    ).strftime("%Y-%m-%d").tolist()

    if params_from_user["fz"] == 44:
        DIR44 = f'/fcs_regions/{params_from_user["region"]}/notifications'
        files = ftp_server44.nlst(DIR44)
        for filename in files:
            if filename.endswith('.zip'):
                filter_date = get_date(filename, range_date)
                result = return_result(filename, filter_date)
                if result is not None:
                    print(f"поиск закончился. закупка: {result[1]}.\nархив: {result[0]}")
                    break

                # filter_date = get_date(filename, range_date)
                # print(f"filterdate: {filter_date}")
                # if filter_date:
                #     zakupka = parse(filename)
                #     if zakupka is not None:
                #         print(f"поиск закончился. закупка: {zakupka[1]}.\nархив: {zakupka[0]}")
                #         break
                #     else:
                #         continue

            elif filename.endswith("currMonth"):
                DIR44_currMonth = f'/fcs_regions/{params_from_user["region"]}/notifications/currMonth'
                files_currMonth = ftp_server44.nlst(DIR44_currMonth)
                for filename_currMonth in files_currMonth:
                    if filename_currMonth.endswith(".zip"):
                        filter_date = get_date(filename_currMonth, range_date)
                        result = return_result(filename_currMonth, filter_date)
                        if result is not None:
                            print(f"поиск закончился. закупка: {result[1]}.\nархив: {result[0]}")
                            break

    elif params_from_user["fz"] == 223:
        DIR223 = f'/out/published/{params_from_user["region"]}/{params_from_user["folder"]}'
        files = ftp_server223.nlst(DIR223)
        for filename in files:
            if filename.endswith(".zip"):
                filter_date = get_date(filename, range_date)
                result = return_result(filename, filter_date)
                if result is not None:
                    print(f"поиск закончился. закупка: {result[1]}.\nархив: {result[0]}")
                    break

            elif filename.endswith("daily"):
                DIR223_daily = f'{DIR223}/daily'
                files_daily = ftp_server223.nlst(DIR223_daily)
                for filename_daily in files_daily:
                    if filename_daily.endswith(".zip"):
                        filter_date = get_date(filename_daily, range_date)
                        result = return_result(filename_daily, filter_date)
                        if result is not None:
                            print(f"поиск закончился. закупка: {result[1]}.\nархив: {result[0]}")
                            break
