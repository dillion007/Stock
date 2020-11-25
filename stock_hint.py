import time
import requests


class Stock(object):
    name = ""
    code = ""
    alarm_price = 0
    alarm_percent = 0
    change_percent = 0

    def __init__(self, name, code, alarm_price, alarm_percent=5, change_percent=1):
        self.name = name
        self.code = code
        self.alarm_price = alarm_price
        self.alarm_percent = alarm_percent
        self.change_percent = change_percent


dict = [Stock("云南铜业", "sz000878", 15.9),
        Stock("北方稀土", "sh600111", 13.1),
        Stock("厦门钨业", "sh600549", 15.7)]
messages = set()


def add_send_message(message):
    print(message)
    messages.add("hint==> " + message)


def send_we_chat():
    for send in messages:
        """这里发送微信消息"""
        requests.get(
            u"http://127.0.0.1:3000/openwx/send_friend_message?displayname=苍穹&content=%s" % (send,))
    messages.clear()


def check_stock_price(stock):
    try:
        response = requests.get("http://hq.sinajs.cn/list=%s" % (stock.code,))
        res = response.text.split(',')
        name, now, yesterday = res[0][21:], float(res[3]), float(res[2])  # 名称，现价，昨收
        diff = now - yesterday  # 差价
        percent = diff / yesterday * 100  # 涨跌幅

        if percent > stock.change_percent or percent < stock.change_percent - 1:
            message = "{}({:.2f} {:.2f} {:.2f}%) 波动范围超出 {}% ~ {}%" \
                .format(name, now, diff, percent, stock.change_percent - 1, stock.change_percent)
            add_send_message(message)

            if percent > 0:
                stock.change_percent = int(percent) + 1
            else:
                stock.change_percent = int(percent)

        if percent < -stock.alarm_percent:
            message = "{}({:.2f} {:.2f} {:.2f}%) 跌幅超出 {}%" \
                .format(name, now, diff, percent, stock.alarm_percent)
            add_send_message(message)

        if now <= stock.alarm_price:
            message = "===alarm alarm alarm===\n{}({:.2f} {:.2f} {:.2f}%) 低于停损价 {}" \
                .format(name, now, diff, percent, stock.alarm_price)
            add_send_message(message)

        send_we_chat()
    except Exception as e:
        print(e)


while True:
    for s in dict:
        check_stock_price(s)
        time.sleep(5)
