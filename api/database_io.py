import json
import math
import sys

sys.path.append("../")

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
        self.host = HOST

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

    def delete(self, id):
        with self.connection.cursor() as cursor:
            sql = """DELETE FROM crawl_source where f_source_id=%s"""
            cursor.execute(sql, id)
        self.connection.commit()
        return {
                    "type": "delete",
                    "id": id,
                }

    def source_update(self, new_date: dict, ):
        with self.connection.cursor() as cursor:
            if len(new_date) == 2 and new_date.get("id", "") != "":
                id = new_date.pop("id")
                d = new_date.popitem()
                sql = """UPDATE crawl_source SET %s=%s WHERE f_source_id=%s;""" % (d[0], d[1], id)
                cursor.execute(sql,)
                result = {
                    "type": "update",
                    "id": id,
                    "key": d[0],
                    "value": d[1]
                }
            else:
                if "id" in new_date and new_date["id"] != "":
                    sql = """UPDATE crawl_source SET f_source_url=%s,f_source_name=%s,disabled=%s WHERE f_source_id=%s;"""
                    cursor.execute(sql, (new_date["web_url"], new_date["web_name"], new_date.get("disabled", 0), new_date["id"]))
                    result = {
                        "type": "update",
                        "id": new_date["id"]
                    }
                else:
                    sql = """INSERT INTO crawl_source (f_source_name,f_source_url,disabled) VALUES (%s,%s,%s)"""
                    cursor.execute(sql, (new_date["web_name"], new_date["web_url"], new_date.get("disabled", 0)))
                    sql = """SELECT f_source_id FROM crawl_source WHERE f_source_url=%s"""
                    cursor.execute(sql, (new_date["web_url"]))
                    result = {
                        "type": "new_add",
                        "id": cursor.fetchone()[0]
                    }
        self.connection.commit()
        return result

    def upload_result(self, result: list):
        with self.connection.cursor() as cursor:
            sql = """INSERT INTO result (web_url, web_name, target_title, target_url, target_date, weights) VALUES (%s,%s,%s,%s,%s,%s)"""
            for i in result:
                cursor.execute(sql, (i["web_url"], i["web_name"], i["target_title"], i["target_url"], i["target_date"], i["weights"]))
        self.connection.commit()
        print("%s ??????????????????????????????" % len(result))

    def upload_url_status(self, web_obj: list):
        with self.connection.cursor() as cursor:
            sql = """UPDATE crawl_source SET f_crawl_status=%s,f_error_msg=%s WHERE f_source_id=%s;"""
            for i in web_obj:
                cursor.execute(sql, (i["status"], i["error"], i["id"]))
        self.connection.commit()

    def get_all_target_url(self):
        with self.connection.cursor() as cursor:
            sql = """SELECT target_url FROM result"""
            cursor.execute(sql)
            return [i[0] for i in cursor.fetchall()]

    def get_all_web_obj(self):
        with self.connection.cursor() as cursor:
            sql = """SELECT f_source_id,f_source_url,f_source_name FROM ggzq.crawl_source WHERE disabled=0"""
            cursor.execute(sql)
            return [{
                "id": i[0],
                "web_url": i[1],
                "web_name": i[2]
            } for i in cursor.fetchall()]

    def get_data(self, p, l):
        with self.connection.cursor() as cursor:
            sql = """SELECT COUNT(*) FROM result"""
            cursor.execute(sql, )
            total = cursor.fetchall()[0][0]
            all_page = math.ceil(int(total) / int(l))
            if not 1 <= int(p) <= int(all_page):
                p = 1
            sql = """SELECT * FROM result ORDER BY target_date DESC LIMIT %d,%d""" % (int((int(p) - 1) * 50), int(l))
            cursor.execute(sql, )
            return {
                "total": int(total),
                "all_page": int(all_page),
                "page": int(p),
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
            sql = """SELECT f_source_id,f_source_url,f_source_name,f_crawl_status,f_error_msg,disabled FROM crawl_source LIMIT %d,%d""" % (int((int(p) - 1) * 50), int(l))
            cursor.execute(sql, )
            return {
                "total": total,
                "data": [{
                    "id": i[0],
                    "web_url": i[1],
                    "web_name": i[2],
                    "web_status": i[3],
                    "web_info": i[4],
                    "disabled": i[5]
                } for i in cursor.fetchall()]
            }

    def get_source_detailed(self, id):
        with self.connection.cursor() as cursor:
            sql = """SELECT f_source_id,f_source_url,f_source_name,f_province,f_city,f_county,f_province_code,f_create_time,disabled,f_crawl_status,f_error_msg FROM  crawl_source WHERE f_source_id = %s"""
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
                "create_time": source[7],
                "disabled": source[8],
                "web_status": source[9],
                "web_info": source[10]
            }

    def get_data_by_weights(self, p, l, weights):
        with self.connection.cursor() as cursor:
            sql = """SELECT COUNT(*) FROM result  WHERE weights >= %d""" % int(weights)
            cursor.execute(sql, )
            total = cursor.fetchall()[0][0]
            all_page = math.ceil(int(total) / int(l))
            if not 1 <= int(p) <= int(all_page):
                p = 1
            sql = """SELECT * FROM result WHERE weights >= %d ORDER BY target_date DESC LIMIT %d,%d""" % (int(weights), int((int(p) - 1) * 50), int(l))
            cursor.execute(sql, )
            return {
                "total": int(total),
                "all_page": int(all_page),
                "page": int(p),
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

    def config(self, name = None, new_data = None):
        if new_data is None and name is None:
            with self.connection.cursor() as cursor:
                sql = """SELECT * FROM config"""
                cursor.execute(sql, )
                data = cursor.fetchall()
                return {
                    data[0][0]: data[0][1],
                    data[1][0]: data[1][1],
                    data[2][0]: data[2][1],
                    data[3][0]: data[3][1],
                }
        elif name is not None and new_data is None:
            with self.connection.cursor() as cursor:
                sql = """SELECT * FROM config WHERE name=%s"""
                cursor.execute(sql, name)
                data = cursor.fetchall()
                return {
                    data[0][0]: data[0][1],
                }
        elif name is None and new_data is not None:
            with self.connection.cursor() as cursor:
                for i in new_data:
                    sql = """UPDATE config SET value=%s WHERE name=%s"""
                    cursor.execute(sql, (json.dumps(new_data[i]), i))
                    print("???????????? %s ??? %s" % (i, new_data[i]))
                self.connection.commit()
                return "????????????"
        else:
            return None

    def clearn_result(self):
        with self.connection.cursor() as cursor:
            sql = """DELETE FROM result"""
            cursor.execute(sql)
        self.connection.commit()
        return "????????????"


if __name__ == "__main__":
    db = DatabaseIO()
    print(db.get_all_web_obj())
    # print(db.get_source(1,50))
