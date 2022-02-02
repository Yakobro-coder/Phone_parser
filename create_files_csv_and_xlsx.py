import csv
import json
import xlsxwriter
import datetime


def create_csv():
    date = datetime.datetime.now().strftime('%d.%m.%Y %H-%M')
    with open(f'CSV_contacts_{date}.csv', 'w', newline='', encoding='utf-8') as csv_file:
        spamwriter = csv.writer(csv_file, delimiter=',')
        spamwriter.writerow(['Name', 'Given Name', 'Additional Name', 'Family Name', 'Yomi Name', 'Given Name Yomi',
                             'Additional Name Yomi', 'Family Name Yomi', 'Name Prefix', 'Name Suffix', 'Initials',
                             'Nickname', 'Short Name', 'Maiden Name', 'Birthday', 'Gender', 'Location',
                             'Billing Information', 'Directory Server', 'Mileage', 'Occupation', 'Hobby', 'Sensitivity',
                             'Priority', 'Subject', 'Notes', 'Language', 'Photo', 'Group Membership', 'Phone 1 - Type',
                             'Phone 1 - Value', 'Address 1 - Type', 'Address 1 - Formatted', 'Address 1 - Street',
                             'Address 1 - City', 'Address 1 - PO Box', 'Address 1 - Region', 'Address 1 - Postal Code',
                             'Address 1 - Country', 'Address 1 - Extended Address', 'Organization 1 - Type',
                             'Organization 1 - Name', 'Organization 1 - Yomi Name', 'Organization 1 - Title',
                             'Organization 1 - Department', 'Organization 1 - Symbol', 'Organization 1 - Location',
                             'Organization 1 - Job Description'])

        with open('data_base.json', encoding='utf-8') as file:
            dict_book = json.load(file)
            for key in dict_book:
                spamwriter.writerow([dict_book.get(key)[0], dict_book.get(key)[1], '', '', '', '', '', '', '', '', '',
                                     '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Mobile',
                                     dict_book.get(key)[2]])

    print('-' * 90)
    print(f'База номеров сохранена в файле CSV_contacts_{date}.CSV')
    print('-' * 90)


def create_exel():
    date = datetime.datetime.now().strftime('%d.%m.%Y %H-%M')
    workbook = xlsxwriter.Workbook(f'XLSX_contacts_{date}.xlsx')
    worksheet = workbook.add_worksheet()

    # Запись на ПЕРВЫЙ лист для клиентов
    bold = workbook.add_format({'bold': True})
    worksheet.write('A1', 'first_name, last_name', bold)
    worksheet.set_column('A:A', 33)

    worksheet.write('B1', 'Phone', bold)
    worksheet.set_column('B:B', 33)

    with open('data_base.json', encoding='utf-8') as file:
        dict_book = json.load(file)
        for numb, didi in enumerate(dict_book, 2):
            worksheet.set_row(numb, 18)
            worksheet.write(f'A{numb}', dict_book.get(didi)[0] + ' ' + dict_book.get(didi)[1])
            worksheet.write(f'B{numb}', dict_book.get(didi)[2])

    workbook.close()

    print('-' * 90)
    print(f'База номеров сохранена в файле XLSX_contacts_{date}.XLSX')
    print('-' * 90)


def menu():
    while True:
        print('*' * 30, '~~~ВЫГРУЗКА ДАННЫХ В ФАЙЛ~~~', '*' * 30)
        what = input("""Введите число:
1 — Сохранить базу номеров в contacts.CSV;
2 — в contacts.XLSX;
3 — Что бы выйти;
Если хотите ОЧИСТИТЬ базу данных, введите DELETE.
Ввод: """)
        if what == '1':
            create_csv()
        elif what == '2':
            create_exel()
        elif what == '3':
            return what
        elif what == 'DELETE' or what == 'delete' or what == 'Delete':
            date = datetime.datetime.now().strftime('%d.%m.%Y %H-%M')

            with open("data_base.json", "r", encoding="utf-8") as frm, \
                    open(f"data_base_BACKUP_{date}.json", "w", encoding="utf-8") as to:
                to.write(frm.read())

            with open("data_base.json", "w", encoding="utf-8") as file:
                file.write(json.dumps({}))

            print('-' * 90)
            print(f'Перед очищение базы данных был создан БЭКАП базы "data_base_BACKUP_{date}.json"')
            print('-' * 90)
        else:
            print('-' * 90)
            print('!!!НЕВЕРНЫЙ ВВОД!!!')
            print('-' * 90)
