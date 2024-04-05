# from django import forms
#
# from account.models import Account
#
#
# class AccountForm(forms.ModelForm):
#     class Meta:
#         model = Account
#         exclude = ('owner',)
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             field.widget.attrs['class'] = 'form_control'
