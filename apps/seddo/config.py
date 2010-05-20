import re

PIN ="0000"
USSD_ORANGE   ="#117*%(destination)s*%(amount)s*1*%(PIN)s#"
USSD_TIGO     =""
USSD_EXPRESSO =""

ORANGE_PAT =re.compile ("(\+?221?)(77\d{7})")
TIGO_PAT =re.compile ("(\+?221?)(76\d{7})")
EXPRESSO_PAT =re.compile ("(\+?221?)(71\d{7})")

