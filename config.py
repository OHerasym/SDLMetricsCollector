server = "http://adc.luxoft.com/jira"

developers = ["dtrunov", "agaliuzov", "akutsan", "aoleynik", "anosach", "okrotenko", "vveremjova",
         "abyzhynar", "ezamakhov", "aleshin", "akirov", "vprodanov", "alambin"]

github_luxoft_map = {
    "dtrunov": "LuxoftAKutsan",
    "agaliuzov": "LuxoftAKutsan",
    "akutsan": "LuxoftAKutsan",
    "aoleynik": "LuxoftAKutsan",
    "anosach": "LuxoftAKutsan",
    "okrotenko": "LuxoftAKutsan",
    "vveremjova": "LuxoftAKutsan",
    "abyzhynar": "LuxoftAKutsan",
    "ezamakhov": "LuxoftAKutsan",
    "aleshin": "LuxoftAKutsan",
    "akirov": "LuxoftAKutsan",
    "vprodanov": "LuxoftAKutsan",
    "alambin": "LuxoftAKutsan",
    }

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
