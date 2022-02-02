import xlsxwriter
import json


def create_table():

    workbook = xlsxwriter.Workbook('phone_book.xlsx')
    worksheet = workbook.add_worksheet()

    # Запись на ПЕРВЫЙ лист для клиентов
    bold = workbook.add_format({'bold': True})
    worksheet.write('A1', 'user_id', bold)
    worksheet.set_column('A:A', 16)

    worksheet.write('B1', 'Phone', bold)
    worksheet.set_column('B:B', 80)

    with open('data_base.json', encoding='utf-8') as file:
        dict_book = json.load(file)
        for numb, didi in enumerate(dict_book, 2):
            worksheet.set_row(numb, 18)
            worksheet.write(f'A{numb}', didi)
            worksheet.write(f'B{numb}', dict_book.get(didi))

    workbook.close()


if __name__ == '__main__':
    create_table()
