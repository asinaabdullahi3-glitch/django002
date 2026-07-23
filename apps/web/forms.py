from django import forms
from django.forms import BaseForm


def set_form_fields_disabled(form: BaseForm, disabled: bool = True) -> None:
    """
    For a given form, disable (or enable) all fields.
    """
    for field in form.fields:
        form.fields[field].disabled = disabled


class ContactForm(forms.Form):
    """Form for contacting the PetPal team."""

    name = forms.CharField(max_length=100, required=True, label="Your Name")
    email = forms.EmailField(required=True, label="Your Email")
    subject = forms.CharField(max_length=200, required=True, label="Subject")
    message = forms.CharField(widget=forms.Textarea, required=True, label="Message")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "input input-bordered w-full"
