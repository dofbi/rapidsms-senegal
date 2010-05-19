for i in 'deb' 'dyu' 'en' 'fr' 'pul' 'wol' 'mnk' 'snk'
do
     msgfmt -o ../apps/smsforum/locale/$i/LC_MESSAGES/django.mo ../apps/smsforum/locale/$i/LC_messages/django.po
done
