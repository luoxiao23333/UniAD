from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header
import smtplib
import time
import yaml


'''
If set enabled=True, you will receive a notification email with execution time.
If you want to enable this function, please write following config into email.yaml within the same dir of this py file
code: Authentication Code of you proxy email
proxy_email: proxy email address
dest_email: email address that you want to receive the result
proxy_url:  proxy url of email service provider, for qq email: 'smtp.qq.com'
proxy_port: port of email service provider, for qq email: 465
'''
class task_counter(object):
    def __init__(self, task_name='Unnamed', enabled=True):
        self.task_name = task_name
        self.enabled = enabled
        self.contents = []
        self.attach_msg = []

    def __enter__(self):
        if not self.enabled:
            return
        print("Start Task Email Counter")
        self.tick = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.enabled:
            return
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

            text = 'Task executed {}\nExtra Info:\n\n'.format(latency)
            for content in self.contents:
                text = text + '-----------------------\n{}\n'.format(content)
            text = MIMEText(text, 'plain', 'utf-8')
            msg.attach(text)

            for (content, file_name) in self.attach_msg:
                longtext_attachment = MIMEApplication(content.encode("utf-8"), Name=file_name)
                longtext_attachment['Content-Disposition'] = R'attachment; filename="{}"'.format(file_name)
                msg.attach(longtext_attachment)

            con.sendmail(proxy_email, dest_email, msg.as_string())
            con.quit()

    # Add extra message in the email
    def add_msg(self, msg: str):
        self.contents.append(msg)

    # Add long message as attachment
    def add_attach(self, msg: str, file_name: str):
        self.attach_msg.append((msg, file_name))
