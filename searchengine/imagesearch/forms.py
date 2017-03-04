from django import forms

class Search(forms.Form):
  search_term = forms.CharField()