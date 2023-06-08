from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import time
import yaml


class task_counter(object):
    def __init__(self, task_name='Unnamed'):
        self.task_name = task_name

    def __enter__(self):
        print("Start Task Email Counter")
        self.tick = time.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        latency = time.perf_counter() - self.tick
        latency = task_counter.__format_time__(latency)
        self.__send_email__(latency)
        print("email sent, latency is {}".format(latency))

    @staticmethod
    def __format_time__(seconds):
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, remainder = divmod(remainder, 60)
        seconds, milliseconds = divmod(remainder, 1)

        result = []
        if days > 0:
            result.append("{}days ".format(int(days)))
        if hours > 0:
            result.append("{}hours ".format(int(hours)))
        if minutes > 0:
            result.append("{}minutes ".format(int(minutes)))
        if seconds > 0:
            result.append("{}seconds ".format(int(seconds)))
        if milliseconds > 0:
            result.append("{:.0f}milliseconds ".format(milliseconds * 1000))

        return "".join(result)

    def __send_email__(self, latency):
        with open('email.yaml', 'r') as file:
            config = yaml.safe_load(file)
            code = config['code']
            proxy_email = config['proxy_email']
            dest_email = config['dest_email']
            proxy_url = config['proxy_url']
            proxy_port = config['proxy_port']

            con = smtplib.SMTP_SSL(proxy_url, proxy_port)
            con.login(proxy_email, code)
            msg = MIMEMultipart()
            subject = Header('Task {} Done'.format(self.task_name), 'utf-8').encode()
            msg['Subject'] = subject
            msg['From'] = 'python robot <{}>'.format(proxy_email)
            msg['To'] = dest_email
            text = MIMEText('Task executed {}'.format(latency), 'plain', 'utf-8')
            msg.attach(text)
            con.sendmail(proxy_email, dest_email, msg.as_string())
            con.quit()