for i in 'deb' 'dyu' 'en' 'fr' 'pul' 'wol' 'mnk' 'snk'
do
     python is_gsm_compatible.py ../apps/smsforum/locale/$i/LC_MESSAGES/django.po
done
