from django import forms
from django.forms import ModelForm
from django.db import transaction, IntegrityError
from apps.contacts.models import *

class BasicContactForm(ModelForm):
    perm_send = forms.BooleanField(required=False, label="Can blast messages", initial=True)
    perm_receive = forms.BooleanField(required=False, label="Can receive messages", initial=True)
    perm_ignore = forms.BooleanField(required=False, label="Is spam number")    
    age_years = forms.FloatField(required=False, label="Age in Years")
    first_name = forms.CharField(max_length=30, required=False, label="Given Name")
    last_name = forms.CharField(max_length=30, required=False, label="Family Name")
    
    class Meta:
        model = Contact
        fields = ('common_name','gender')
   
    def __init__(self, data=None, instance=None):
        super(BasicContactForm, self).__init__(data=data, instance=instance)
        if data is not None:
            set = lambda x: x in data and True or False
            self.fields['perm_send'].value = set( 'perm_send' )
            self.fields['perm_receive'].value = set( 'perm_receive' )
            self.fields['perm_ignore'].value = set( 'perm_ignore' )
            self.fields['age_years'].value = data['age_years']
            self.fields['first_name'].value = data['first_name']
            self.fields['last_name'].value = data['last_name']
        if instance is not None:
            self.fields['perm_send'].initial = instance.perm_send
            self.fields['perm_receive'].initial = instance.perm_receive
            self.fields['perm_ignore'].initial = instance.perm_ignore
            self.fields['age_years'].initial = instance.age_years
            self.fields['first_name'].initial = instance.reporter.first_name
            self.fields['last_name'].initial = instance.reporter.last_name

    @transaction.commit_on_success
    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(BasicContactForm, self).save(commit=False)
        if not hasattr(m,'reporter'):
            r = Reporter()
            m.reporter = r
        m.reporter.first_name = self.fields['first_name'].value
        m.reporter.last_name = self.fields['last_name'].value
        m.reporter.alias = self.fields['common_name']
        m.reporter.save()
        m.perm_send = self.fields['perm_send'].value
        m.perm_receive = self.fields['perm_receive'].value
        m.perm_ignore = self.fields['perm_ignore'].value
        if self.fields['age_years'].value:
            m.age_years = float( self.fields['age_years'].value )
        if commit:
            m.save()
        return m

class ContactWithChannelForm(BasicContactForm):
    phone_number = forms.CharField(max_length=64, required=False, label="Phone Number")
    backend = forms.ModelChoiceField(PersistantBackend.objects, required=False)
     
    def __init__(self, data=None, instance=None):
        super(ContactWithChannelForm, self).__init__(data=data, instance=instance)
        conns = PersistantConnection.objects.filter(reporter=instance.reporter)
        if conns:
            self.fields['phone_number'].initial = conns[0].identity
            self.fields['backend'].initial = conns[0].backend
    
    @transaction.commit_on_success
    def save(self):
        contact = super(ContactWithChannelForm, self).save()
        if 'phone_number' in self.cleaned_data and self.cleaned_data['phone_number']:
            conns = PersistantConnection.objects.filter(reporter=contact.reporter)
            if not conns:
                conn = PersistantConnection( reporter=contact.reporter )
            else:
                conn = conns[0]
            conn.identity=self.cleaned_data['phone_number']
            if 'backend' not in self.cleaned_data or not self.cleaned_data['backend']:
                raise ValueError("If you specify phone number, you must also add communication channel")
            conn.backend=self.cleaned_data['backend']
            conn.save()
        else:
            conns = PersistantConnection.objects.filter(reporter=contact.reporter)
            if conns: conns.delete()            
        return contact

    def clean(self):
         cleaned_data = self.cleaned_data
         if 'phone_number' in cleaned_data and cleaned_data['phone_number']: 
             if 'backend' not in cleaned_data or not cleaned_data['backend']:
                 # don't need to set the communication channel if there is only one in the system
                 raise forms.ValidationError("If you specify phone number, you must also add communication channel")
         return cleaned_data;

class GSMContactForm(BasicContactForm):
    phone_number = forms.CharField(max_length=64, required=False, label="Phone Number")
    backend = None

    def __init__(self, data=None, instance=None):
        super(GSMContactForm, self).__init__(data=data, instance=instance)
        if instance is not None:
            conns = PersistantConnection.objects.filter(reporter=instance.reporter)
            if conns:
                self.fields['phone_number'].initial = conns[0].identity
            
    @transaction.commit_on_success
    def save(self):
        contact = super(GSMContactForm, self).save()
        # keep default channelconnection
        # unless none exists, in which case create the default one
        if 'phone_number' in self.cleaned_data and self.cleaned_data['phone_number']:
            # this is rather hack-ish
            phone_number = self.cleaned_data['phone_number']
            try:
                # default to gsm if it exists
                channel = PersistantBackend.objects.get(slug__icontains='gsm')
            except PersistantBackend.DoesNotExist: 
                # otherwise default to whatever
                try:
                    channel = PersistantBackend.objects.get()
                except PersistantBackend.DoesNotExist:
                    raise Exception("No Communication Channels are defined!")
            conns = PersistantConnection.objects.filter(reporter=contact.reporter, backend=channel)
            if not conns:
                conn = PersistantConnection( reporter=contact.reporter, backend=channel )
            else:
                conn = conns[0]
            try:
                conn.identity = self.cleaned_data['phone_number']
                conn.save()
            except IntegrityError, e:
                # More user friendly error message
                if unicode(e).find('Duplicate') != -1:
                    raise IntegrityError("That phone number is already in use!")
        return contact
