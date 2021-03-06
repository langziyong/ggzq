import json
import sys
import asyncio
import queue
import time
import threading

import pyppeteer
from bs4 import BeautifulSoup
import re
from pyppeteer import launch
from multiprocessing import Process, Queue, Lock
import os

sys.path.append("../")
import database_io

# 定义全局消息头
HEADERS = {
    "User-Agent": r"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0"
}

# 定义全局参数
db = database_io.DatabaseIO()
config = db.config()
PROCESS_N = int(json.loads(config["SYSTEM_CONFIG"])["PROCESS_N"])
THREAD_N = int(json.loads(config["SYSTEM_CONFIG"])["THREAD_N"])
ASYNC_N = int(json.loads(config["SYSTEM_CONFIG"])["ASYNC_TASK_N"])
TITLE_LENGTH = int(json.loads(config["SYSTEM_CONFIG"])["TITLE_LENGTH"])
GET_HTML_TIMEOUT = int(json.loads(config["SYSTEM_CONFIG"])["GET_HTML_TIMEOUT"])
EFFECTIVE_TIME_DIFFERENCE = int(json.loads(config["SYSTEM_CONFIG"])["EFFECTIVE_TIME_DIFFERENCE"])
TITLE_SEARCH_DEPTH = int(json.loads(config["SYSTEM_CONFIG"])["TITLE_SEARCH_DEPTH"])
WEIGHTS_LIMIT = int(json.loads(config["SYSTEM_CONFIG"])["WEIGHTS_LIMIT"])
TITLE_KEYWORD = json.loads(config["KEYWORD"])
# 计数初始化
J = {
    "PAGE_FIND_OK": 0,
    "PAGE_FIND_FAIL": 0,
    "FIND_TARGET": 0,
    "FIND_DATE_OBJ": 0,
    "FIND_TITLE_DISCARD": 0,
}


# 初始化

# 异步请求网页 配合多进程
class AsyncGetHTML:
    def __init__(self, process_id, entryQueue: Queue, outputQueue: Queue, lock: Lock):
        try:
            self.loop = asyncio.new_event_loop()
            self.browser = self.loop.run_until_complete(launch())
            self.entry_queue = entryQueue
            self.output_queue = outputQueue
            self.lock = lock
            self.process_id = process_id
            self.async_lock = asyncio.Lock()
        except Exception as e:
            print(e)

    @staticmethod
    async def download_html(obj, browser, name) -> dict:
        # print("进程 %s 获取到 URL : %s 当前 task: %s" % (self.process_id, url_obj["web_url"], task))
        url_obj = obj
        url = url_obj["web_url"]
        host = re.search(r"http[s]?://.+?/|http[s]?://.+", url_obj["web_url"])
        if host is None:
            url_obj["host"] = url + '/'
            print("HOST不匹配 尝试直接添加 / URL：%s" % url)
        else:
            url_obj["host"] = host.group()
        page = await browser.newPage()
        try:
            await page.goto(url, {
                "waitUntil": "networkidle2",
                "timeout": 1000 * GET_HTML_TIMEOUT
            })
            url_obj["html"] = await page.content()
            print("Task:%s GET_HTML:%s OK " % (name, url,))
            url_obj["status"] = "SUCCESS"
            url_obj["error"] = "OK"
            # self.output_queue.put(url_obj)
        except TimeoutError as e:
            print("Task:%s GET_HTML:%s Fail: %s" % (name, url, e))
            url_obj["status"] = "TIMEOUT"
            url_obj["error"] = e
        except Exception as e:
            print("Task:%s GET_HTML:%s Fail: %s" % (name, url, e))
            url_obj["status"] = "FAIL"
            url_obj["error"] = e
        await page.close()
        return url_obj

    async def run(self, name):
        result = []
        try:
            while True:
                self.lock.acquire()
                await self.async_lock.acquire()
                if self.entry_queue.empty():
                    self.async_lock.release()
                    self.lock.release()
                    return result
                else:
                    url_obj = self.entry_queue.get_nowait()
                    self.async_lock.release()
                    self.lock.release()
                    r = await self.download_html(url_obj, self.browser, name)
                    result.append(r)
        except Exception as e:
            print(e)

    def start(self):
        result = []
        try:
            # 异步 并发
            tasks = [self.run(i) for i in range(ASYNC_N)]
            done, pending = self.loop.run_until_complete(asyncio.wait(tasks))
            for i in pending:
                print("pending:%s" % i)
            print("进程任务完成，准备退出")
        except Exception as e:
            print(e)
        else:
            try:
                self.loop.run_until_complete(self.browser.close())
            except Exception as e:
                print("浏览器关闭失败")
                print(e)
            for c in [i.result() for i in done]:
                if not c:
                    pass
                else:
                    pass
                    [result.append(r) for r in c]
            return result


# 多线程解析页面
class Threads(threading.Thread):
    def __init__(self, id: int, entryQueue: queue.Queue, outputQueue: queue.Queue, lock: threading.Lock):
        super().__init__()

        self.thread_id = id
        self.output_queue = outputQueue
        self.entry_queue = entryQueue
        self.lock = lock
        # 创建解析对象
        self.Parser = ParserHTML()

    def run(self) -> None:
        while True:
            self.lock.acquire()
            if self.entry_queue.empty():
                self.lock.release()
                break
            else:
                url_obj = self.entry_queue.get_nowait()
                self.lock.release()
                result = self.Parser.resolve(url_obj = url_obj)
                if result is [] or result is None:
                    J["PAGE_FIND_FAIL"] += 1
                    pass
                else:
                    J["PAGE_FIND_OK"] += 1
                    [self.output_queue.put_nowait(i) for i in result]
        print("线程ID: %s执行完成" % self.thread_id)


class ParserHTML:
    def __init__(self):
        pass

    def resolve(self, url_obj: dict):
        # 生成BS 对象以供下步解析
        url_obj["page"] = BeautifulSoup(url_obj["html"], "html.parser")
        result = []
        for node in url_obj["page"].find_all():
            date_obj = self.find_date_obj(node)
            if date_obj is not None:
                r = self.find_title(date_obj, url_obj)
                if r is not None:
                    result.append(r)
        if result is []:
            return None
        else:
            return result

    # 传入节点单元 判定是否存在日期
    def find_date_obj(self, obj: BeautifulSoup):
        d = re.search(r"(20[0-9][0-9])?[-\\/年]?([0,1]?[0-9])[-\\/月]([0-3]?[0-9])[日]?", str(obj.string))
        if d is not None:
            tag_name = obj.name
            if self.has_chinese(str(obj.string)):
                return None
            # elif tag_name not in ALLOW_DATE_OBJ_TAG_NAME:
            #     print("日期标签非法并且丢弃，tag_name为 %s" % tag_name)
            #     return None
            # print("找到DATE_OBJ tag为 %s" % tag_name)
            if len(str(obj.string)) > 11:
                return None

            t = time.localtime()
            if d.group(1) is None or d.group(1) == "":
                y = t[0]
            else:
                y = int(d.group(1))

            m = int(d.group(2))
            d = int(d.group(3))

            if y != t[0]:
                return None

            if not 1 <= m <= 12:
                return None

            if not 1 <= d <= 31:
                return None
            try:
                s_to_t = time.mktime(time.strptime("%s-%s-%s" % (str(y), str(m), str(d)), '%Y-%m-%d'))
                now_t = time.time()
            except ValueError as e:
                print(e)
                print("错误日期: %s-%s-%s" % (str(y), str(m), str(d)))
                return None
            else:
                if s_to_t > now_t:
                    return None
                elif now_t - s_to_t > EFFECTIVE_TIME_DIFFERENCE:
                    return None

            J["FIND_DATE_OBJ"] += 1
            return {
                "obj": obj,
                "date": [str(y), str(m), str(d)]
            }
        return None

    def find_title(self, date_obj: dict, url_obj: dict, title_search_depth = TITLE_SEARCH_DEPTH):
        search_depth = title_search_depth
        date_obj_obj = date_obj["obj"]
        parent = date_obj_obj.parent
        target = None  # a 标签
        while True:
            if search_depth == 0:
                return None
            if parent.name == "a":
                target = parent
                break
            else:
                r = parent.find("a")
                if r is None:
                    search_depth -= 1
                    continue
                else:
                    target = r
                    break

        if self.has_chinese(str(target.string)):
            target_title = str(target.string)
        elif self.has_chinese(target.text):
            target_title = target.text
        else:
            return None

        result = {
            "target_title": target_title
        }

        if len(result["target_title"]) <= TITLE_LENGTH:
            J["FIND_TITLE_DISCARD"] += 1
            return None

        if "href" in target.attrs:
            # 取到URL
            result["target_url"] = target.attrs["href"]
        else:
            result["target_url"] = ""
        if "title" in target.attrs and target.attrs["title"] != "":
            result["target_title"] = target.attrs["title"]
        # 结束查找

        # 数据校验
        result["target_title"] = re.sub(r'\s', '', result["target_title"])
        # 标签格式清理 （去掉日期）
        if str(date_obj_obj.string) in result["target_title"]:
            result["target_title"] = re.sub(str(date_obj_obj.string), '', result["target_title"])
        result["web_url"] = url_obj["web_url"]
        result["web_name"] = url_obj["web_name"]
        # 格式化日期
        result["target_date"] = self.date_format(date_obj["date"])
        # URL 是否完整
        if "http" in result["target_url"]:
            pass
        else:

            result["target_url"] = url_obj["host"] + result["target_url"]

        J["FIND_TARGET"] += 1
        # print(result)
        return result

    @staticmethod
    def has_chinese(string) -> bool:
        """
        检查整个字符串是否包含中文
        :param string: 需要检查的字符串
        :return: bool
        """
        for ch in string:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

    @staticmethod
    def date_format(s: str | list) -> str:
        if None not in s:
            return "%s-%s-%s" % (s[0], s[1], s[2])
        elif s[0] is None:
            return "%s-%s-%s" % ("2088", s[1], s[2])


# 数据重复筛选
def target_compare(compared_data: list, existed_target_url: list):
    result = []
    for i in compared_data:
        if i["target_url"] in existed_target_url:
            pass
        else:
            result.append(i)

    repeat = 0
    result_ = []
    target_title_ = []
    while len(result) != 0:
        i = result.pop()
        if i["target_title"] in target_title_:
            repeat += 1
        else:
            result_.append(i)
            target_title_.append(i["target_title"])

    print("已存在总条数: %s 条" % len(existed_target_url))
    print("新数据量: %s 条" % len(result_))
    print("自检重复: %s 条" % repeat)
    return result_


# 关键词查询
def keyword_query(compared_data: list, keyword_list = None, weights_limit = WEIGHTS_LIMIT):
    result = []
    if keyword_list is None: keyword_list = TITLE_KEYWORD

    for target in compared_data:
        target["weights"] = 0
        for keyword in keyword_list:
            if keyword in target["target_title"]: target["weights"] += 1
        if target["weights"] >= weights_limit:
            result.append(target)

    return result


# 启动函数
def start():
    global PROCESS_N, THREAD_N, ASYNC_N, TITLE_KEYWORD, TITLE_LENGTH, EFFECTIVE_TIME_DIFFERENCE, GET_HTML_TIMEOUT, TITLE_SEARCH_DEPTH, db
    print("已连接到数据库 %s 载入配置..." % db.host)
    all_url = db.get_all_web_obj()

    # 获取到 [web_name,url] url_obj 对象列表
    # all_url = [{"web_url": "http://jyj.qz.gov.cn/col/col1229278217/index.html", "web_name": "TEST"}]
    # all_url = [{"url": "http://www.hzedu.gov.cn/sites/main/template/list.aspx?Id=56&classid=3", "web_name": "TEST_2"}]
    # all_url = [{"web_url": "http://hrss.huzhou.gov.cn/", "web_name": "TEST_2"}]
    # all_url = [{"web_url": "http://www.zjtt.gov.cn/col/col1683846/index.html", "web_name": "TEST_2"}]
    # all_url = [{"web_url": " http://www.zjzs.net/moban/index/index.html", "web_name": "TEST_2"}]
    # all_url = [{"web_url": " http://www.zjzs.net/moban/index/index.html", "web_name": "TEST_2"}, {"web_url": "http://www.zjtt.gov.cn/col/col1683846/index.html", "web_name": "TEST_2"}, {"web_url": "http://hrss.huzhou.gov.cn/", "web_name": "TEST_2"}, {"web_url": "http://www.hzedu.gov.cn/sites/main/template/list.aspx?Id=56&classid=3", "web_name": "TEST_2"}]
    # all_url = [{"web_url": "http://www.aiyanlin.cn/", "web_name": "TEST_2"} for i in range(50)]
    tag = str(time.time_ns())
    # ——————————————————————————— 进程开始 ———————————————————————————————#

    web_obj = []
    if PROCESS_N is None or PROCESS_N == 0: PROCESS_N = os.cpu_count()
    p_t_s = time.time()
    if PROCESS_N == 1:
        print("进程数量为1，不使用多进程技术")
        t_eq = queue.Queue()
        t_oq = queue.Queue()

        async def AsyncGET(web_obj_list: list, browser: pyppeteer.launch, name):
            _result = []
            while web_obj_list:
                _result.append(await AsyncGetHTML.download_html(web_obj_list.pop(), browser, name))
            return _result

        async def main():
            browser = await pyppeteer.launch()
            _r = await asyncio.gather(*[asyncio.create_task(AsyncGET(all_url, browser, i)) for i in range(ASYNC_N)])
            await browser.close()
            _result = []
            for i in _r:
                _result += i
            return _result

        result = asyncio.run(main())
        for r in result:
            if r["status"] == "SUCCESS":
                t_eq.put(r)
            web_obj.append(r)

    else:
        eq = Queue()
        oq = Queue()
        t_eq = queue.Queue()
        t_oq = queue.Queue()
        [eq.put(i) for i in all_url]
        lock = Lock()
        try:
            process_id_list = range(PROCESS_N)
            process = [Process(target = loading_process, args = (i, eq, oq, lock)) for i in process_id_list]
            [p.start() for p in process]
            RESULT = []
            while len(RESULT) != PROCESS_N:
                RESULT.append(oq.get())

            [p.join() for p in process]

            for i in RESULT:
                if i is None:
                    pass
                else:
                    for r in i:
                        if r["status"] == "SUCCESS":
                            t_eq.put(r)
                        web_obj.append(r)
        except Exception as e:
            print(e)
    p_t_e = time.time()
    print("获取网页内容完成 使用进程数量：%s 耗时：%s" % (PROCESS_N, (p_t_e - p_t_s)))

    # ——————————————————————————— 解析开始 ———————————————————————————————#
    print("解析开始 线程数量：%s 任务TAG：%s" % (THREAD_N, tag))
    thread_lock = threading.Lock()
    threads = [Threads(id = thread_id, entryQueue = t_eq, outputQueue = t_oq, lock = thread_lock) for thread_id in range(THREAD_N)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    print("解析完成 使用线程数量：%s 任务TAG：%s" % (THREAD_N, tag))

    # ——————————————————————————— 数据处理 ———————————————————————————————#
    # 从线程输出队列中取出数据
    result = []
    while not t_oq.empty():
        result.append(t_oq.get())

    result = target_compare(result, db.get_all_target_url())

    result = keyword_query(result)

    # ——————————————————————————— 数据上传 ———————————————————————————————#
    print("执行数据入库.....")
    db.upload_result(result)

    # ——————————————————————————— 统计数据上传 ———————————————————————————————#
    print("执行统计数据入库.....")
    db.upload_url_status(web_obj)


# 加载进程函数
def loading_process(name, eq: Queue, oq: Queue, lock):
    try:
        AsyncDownload = AsyncGetHTML(name, entryQueue = eq, outputQueue = oq, lock = lock)
        result = AsyncDownload.start()
        oq.put(result)
    except Exception as e:
        print("异步操作异常")
        print(e)
    print("进程关闭 id: %s" % name)


def info():
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())


if __name__ == "__main__":
    t_s = time.time()
    start()
    t_e = time.time()
    print("主进程退出 J = %s \n共耗时: %s " % (J, (t_e - t_s)))
