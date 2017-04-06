#!/usr/local/bin/python
# coding=utf-8
import sys
import csv

reload(sys)
sys.setdefaultencoding('utf-8')
import MySQLdb
# from Writer import Writer

sys.path.append("/opt/meituan/kms/libs/")
# import libPythonKms

reload(sys)


class MysqlWriter():
    """Mysql 数据写回"""

    meta_need = ['host', 'port', 'user', 'passwd', 'db']

    def __init__(self, **meta):
        self.meta = {}
        # super(Writer, self).__init__()
        for item in self.meta_need:
            if item not in meta.keys():
                raise Exception('meta not enough')
            self.meta[item] = meta[item]

        self.meta['charset'] = meta.get('charset', 'utf8')

        self.connect = None

    def _connect(self):
        if self.connect:
            return
        self.connect = MySQLdb.connect(**self.meta)
        # 强制不自动commit
        self.connect.autocommit(0)

    def before_write(self):
        pass

    def after_write(self):
        pass

    def write(self, sql, iscommit=False):
        self.before_write()
        self.write_raw(sql, iscommit)
        self.after_write()

    def write_raw(self, sql, iscommit=False):
        self._connect()
        self.cursor = self.connect.cursor()
        try:
            self.cursor.execute(sql)
        except Exception, e:
            self.connect.rollback()
            raise Exception(str(e))
        else:
            if iscommit:
                self.connect.commit()
        self.cursor.close()

    def query(self, sql):
        self._connect()
        self.cursor = self.connect.cursor()
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.cursor.close()

        return result

if __name__ == '__main__':
    cis = {
        'host': 'data-mysql-cis-write.vip.sankuai.com',
        'port': 5002,
        'db': 'cis',
        'user': 'girl',
        'passwd': 'boy'
        # 'user': libPythonKms.getKeyByName('com.sankuai.cis.fetchsaver', 'db.cis_in_city.username'),
        # 'passwd': libPythonKms.getKeyByName('com.sankuai.cis.fetchsaver', 'db.cis_in_city.password'),
    }

    # SQL = "insert into poi_tag(`%s`) values(\"%s\")"
    SQL = "updated poi_tag set whereExpression='mt_main_poi_id IS NOT NULL AND mt_poi_cate1_id=226 AND poi_close_status=0 AND mt_main_poi_id=poi_id AND partition_chain=\'mt\'' where owner='wujunchao'"
    writer = MysqlWriter(**cis)

    path = "tag_info.csv"

    fopen = csv.DictReader(file(path))
    for row in fopen:
        level = row['level']
        whereException = row['whereExpression']
        row['level'] = "基本属性.%s" % (level)
        keyList = []
        valueList = []
        for key in row:
            keyList.append(key)
            valueList.append(row[key])

        sql = SQL % ('`,`'.join(keyList), "\",\"".join(valueList))
        print sql
        try:
            # print ;
            writer.write(sql, True)
        except Exception, e:
            print e
