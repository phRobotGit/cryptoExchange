#%%
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.utils import formataddr

# sender = "hang.p@logtec.com"
# receiver = "hang.p@logtec.com"
# password = "GGph620!"
# password = "cnjt lubc mfqa cxvi"

class Email():
    sender = None
    password = None
    
    def __init__(self, sender, password):
        self.sender = sender
        self.password = password
    
    def send_email(self, receiver_list, cc_list,  subject, text, attachment_excel_path_list):
        msg = MIMEMultipart()
        msg["From"] = formataddr(["DA邮件机器人", self.sender])
        msg["To"] = ",".join(receiver_list)
        msg["Cc"] = ",".join(cc_list)
        msg["Subject"] = subject #"商务BD日报"
        msg.attach(MIMEText(text, "plain", "utf-8")) # "您好, 请查收商务BD报表。"
        
        for excel_file_path in attachment_excel_path_list:
            xlsxpart = MIMEApplication(open(excel_file_path, "rb").read())
            xlsxpart.add_header("Content-Disposition", "attachment", filename=excel_file_path.name)
            msg.attach(xlsxpart)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(user=self.sender, password=self.password)
        server.sendmail(from_addr=self.sender, to_addrs=receiver_list+cc_list, msg=msg.as_string())
        server.quit()
        print("Eamil Sent!")
        

