import six

server = "http://adc.luxoft.com/jira"

class Developer:
    def __init__(self, luxoft_login, github_login):
        self.luxoft_login = luxoft_login
        self.github_login = github_login
    def email(self):
        return "%s@luxoft.com"%self.luxoft_login
    def __str__(self):
        return self.luxoft_login
    def __repr__(self):
        return str(self)
    def __eq__(self, other):
        if isinstance(other, six.string_types):
            return self.luxoft_login.lower() == other.lower()
        if isinstance(other, Developer):
            return  other.luxoft_login.lower() == self.luxoft_login.lower() and other.github_login.lower() == self.github_login.lower()
        return False
    def lower(self):
        return str(self.luxoft_login).lower()

developers = []

developers.append(Developer("AKutsan", "LuxoftAKutsan"))
developers.append(Developer("AOlyenik", "dev-gh"))
developers.append(Developer("VProdanov", "vprodanov"))
developers.append(Developer("ALeshin", "Anatoliy-Leshin"))
developers.append(Developer("DTrunov", "dtrunov"))
developers.append(Developer("OKrotenko", "nk0leg"))
developers.append(Developer("EZamakhov", "pestOO"))
developers.append(Developer("AOlyenik", "dev-gh"))
developers.append(Developer("VVeremjova", "VVeremjova"))
developers.append(Developer("ANosach", "anosach-luxoft"))
developers.append(Developer("AByzhynar", "AByzhynar"))
developers.append(Developer("AGritsevich", "AGritsevich"))
developers.append(Developer("AMikhniev", "AMikhniev"))
developers.append(Developer("AKozoriz", "Kozoriz"))
developers.append(Developer("RMalynovskyi", "malirod"))
developers.append(Developer("OHerasym", "OHerasym"))
developers.append(Developer("AKirov", "asenkk"))

def get_developer_by_github_user_name(guthub_username):
    for developer in developers:
        if developer.github_login == guthub_username:
            return developer
    return None

def get_developer_by_luxoft_user_name(luxoft_username):
    for developer in developers:
        if developer.luxoft_login == luxoft_username:
            return developer
    return None

message_template = '''From: Alexander Kutsan <AKutsan@luxoft.com>
To: %s
Subject: Metric fails WARNING

Hello,

Metric fails collected by script:

%s

Script sources available on github
https://github.com/LuxoftAKutsan/SDLMetricsCollector

Best regards,
Alexander Kutsan
'''
