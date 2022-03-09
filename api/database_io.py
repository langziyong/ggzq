import pymysql
import api.config as config

HOST = config.HOST
PORT = config.PORT
USER = config.USER
PASSWORD = config.PASSWORD
DATABASE = config.DATABASE


class DatabaseIO:
    def __init__(self, connect_args = None):
        if connect_args is None:
            self.connect_args = {
                "HOST": HOST,
                "PORT": PORT,
                "USER": USER,
                "PASSWORD": PASSWORD,
                "DATABASE": DATABASE
            }
        self.connection = self.connect_db(self.connect_args)

    @staticmethod
    def connect_db(connect_args = None) -> pymysql.connect:
        if connect_args is None:
            connect_args = {
                "HOST": HOST,
                "PORT": PORT,
                "USER": USER,
                "PASSWORD": PASSWORD,
                "DATABASE": DATABASE
            }
        connection = pymysql.connect(
            host = connect_args["HOST"],
            port = connect_args["PORT"],
            user = connect_args["USER"],
            password = connect_args["PASSWORD"],
            database = connect_args["DATABASE"],
        )
        return connection

    def add_url(self, url_obj: list) -> None:
        with self.connection.cursor() as cursor:
            sql = """INSERT INTO all_url (title, url) VALUES (%s,%s)"""
            cursor.execute(sql, (url_obj[0], url_obj[1]))
        self.connection.commit()

    def upload_result(self, result: list):
        with self.connection.cursor() as cursor:
            sql = """INSERT INTO result (web_url, web_name, target_title, target_url, target_date, weights) VALUES (%s,%s,%s,%s,%s,%s)"""
            for i in result:
                cursor.execute(sql, (i["web_url"], i["web_name"], i["target_title"], i["target_url"], i["target_date"], i["weights"]))
        self.connection.commit()
        print("%s 条数据已更新至数据库" % len(result))

    def upload_url_status(self, url_status: list, tag):
        with self.connection.cursor() as cursor:
            sql = """DELETE FROM url_status"""
            cursor.execute(sql)
            sql = """INSERT INTO url_status (web_name, url, status, tag) VALUES (%s,%s,%s,%s)"""
            for i in url_status:
                cursor.execute(sql, (i["web_name"], i["web_url"], i["status"], tag))
        self.connection.commit()

    def get_all_target_url(self):
        with self.connection.cursor() as cursor:
            sql = """SELECT target_url FROM result"""
            cursor.execute(sql)
            return [i[0] for i in cursor.fetchall()]

    def get_all_web_obj(self):
        with self.connection.cursor() as cursor:
            sql = """SELECT f_source_url,f_source_name FROM ggzq.crawl_source"""
            cursor.execute(sql)
            return [{
                "web_url": i[0],
                "web_name": i[1]
            } for i in cursor.fetchall()]

    def get_data(self, p, l):
        with self.connection.cursor() as cursor:
            sql = """SELECT COUNT(*) FROM result"""
            cursor.execute(sql, )
            total = cursor.fetchall()[0][0]
            sql = """SELECT * FROM result ORDER BY id DESC LIMIT %d,%d""" % (int((int(p) - 1) * 50), int(l))
            cursor.execute(sql, )
            return {
                "total": total,
                "data": [{
                    "id": i[0],
                    "web_url": i[1],
                    "web_name": i[2],
                    "target_title": i[3],
                    "target_url": i[4],
                    "target_date": str(i[5]),
                    "create_time": str(i[7]),
                    "weights": str(i[8])
                } for i in cursor.fetchall()]
            }

    def get_source(self, p, l):
        with self.connection.cursor() as cursor:
            sql = """SELECT COUNT(*) FROM crawl_source"""
            cursor.execute(sql, )
            total = cursor.fetchall()[0][0]
            sql = """SELECT f_source_id,f_source_url,f_source_name FROM crawl_source LIMIT %d,%d""" % (int((int(p) - 1) * 50), int(l))
            cursor.execute(sql, )
            return {
                "total": total,
                "data": [{
                    "id": i[0],
                    "web_url": i[1],
                    "web_name": i[2],
                } for i in cursor.fetchall()]
            }

    def get_source_detailed(self, id):
        with self.connection.cursor() as cursor:
            sql = """SELECT f_source_id,f_source_url,f_source_name,f_province,f_city,f_county,f_province_code,f_create_time FROM  crawl_source WHERE f_source_id = %s"""
            cursor.execute(sql, id)
            source = cursor.fetchall()[0]
            return {
                "id": source[0],
                "web_name": source[2],
                "web_url": source[1],
                "web_province": source[3],
                "web_city": source[4],
                "web_county": source[5],
                "web_province_code": source[6],
                "create_time": source[7]
            }

    def get_data_by_weights(self, p, l, weights):
        with self.connection.cursor() as cursor:
            sql = """SELECT COUNT(*) FROM result"""
            cursor.execute(sql, )
            total = cursor.fetchall()[0][0]
            sql = """SELECT * FROM result WHERE weights >= %d ORDER BY id DESC LIMIT %d,%d""" % (int(weights), int((int(p) - 1) * 50), int(l))
            cursor.execute(sql, )
            return {
                "total": total,
                "data": [{
                    "id": i[0],
                    "web_url": i[1],
                    "web_name": i[2],
                    "target_title": i[3],
                    "target_url": i[4],
                    "target_date": str(i[5]),
                    "create_time": str(i[7]),
                    "weights": str(i[8])
                } for i in cursor.fetchall()]
            }


if __name__ == "__main__":
    db = DatabaseIO()
    # print(db.get_all_web_url())
    print(db.get_data(5, 20))
