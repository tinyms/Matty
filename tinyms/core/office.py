__author__ = 'tinyms'

import xlrd
import xlsxwriter


#Excel 常规操作类
#Ref: http://www.sharejs.com/codes/python/4345
class Excel(object):
    @staticmethod
    def import_(file_name, sheet_name="", sheet_index=0):
        """
        导入Excel数据
        :param file_name: 文件名称
        :param sheet_name: Sheet名称
        :param sheet_index: Sheet索引
        :return: [(..)..]
        """
        file = xlrd.open_workbook(file_name)
        sheets = file.sheets()
        dataset = list()
        if len(sheets) > 0:
            if sheet_name:
                sheet = file.sheet_by_name(sheet_name)
            else:
                sheet = sheets[sheet_index]
            if sheet:
                row_num = sheet.nrows
                for row_index in range(row_num):
                    row_values = sheet.row_values(row_index)
                    dataset.append(row_values)
        return dataset

    @staticmethod
    def export(file_name, dataset, sheet_name="sheet 1"):
        """
        导出数据到Excel中
        :param file_name: 文件名称
        :param dataset: 数据集
        :param sheet_name: Sheet名称
        :return: 真或者假
        """
        if not dataset:
            return False
        wb = xlsxwriter.Workbook(file_name)
        ws = wb.add_worksheet(sheet_name)
        row = 0
        size = len(dataset)
        for item in dataset:
            for col in size:
                ws.write(row, col, item[col])
            row += 1
        return True