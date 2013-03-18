from django import forms

class ExternalSubscriberUpload(forms.Form):
    xls = forms.FileField(label = '*.xls File')
