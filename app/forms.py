from django import forms


class BookingForm(forms.Form):
    first_name = forms.CharField(max_length=100, label='姓')
    last_name = forms.CharField(max_length=100, label='名')
    #tel = forms.CharField(max_length=100, label='電話番号')
    remarks = forms.CharField(label='備考', widget=forms.Textarea())