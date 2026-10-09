import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Order


class StyledFormMixin:
    def apply_styles(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class RegistrationForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(label="E-mail")

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")
        labels = {"username": "Nome de usuário"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email


class CheckoutForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "recipient_name", "street", "number", "complement", "district", "city",
            "state", "postal_code", "payment_method", "notes",
        ]
        labels = {
            "recipient_name": "Nome de quem recebe",
            "street": "Rua",
            "number": "Número",
            "complement": "Complemento",
            "district": "Bairro",
            "city": "Cidade",
            "state": "UF",
            "postal_code": "CEP",
            "payment_method": "Forma de pagamento",
            "notes": "Observações do pedido",
        }
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()
        self.fields["state"].widget.attrs.update({"maxlength": 2, "placeholder": "SP"})
        self.fields["postal_code"].widget.attrs.update({"placeholder": "00000-000"})

    def clean_state(self):
        state = self.cleaned_data["state"].strip().upper()
        if not re.fullmatch(r"[A-Z]{2}", state):
            raise forms.ValidationError("Informe a UF com duas letras.")
        return state

    def clean_postal_code(self):
        postal_code = self.cleaned_data["postal_code"].strip()
        if not re.fullmatch(r"\d{5}-?\d{3}", postal_code):
            raise forms.ValidationError("Informe um CEP válido, como 01001-000.")
        digits = re.sub(r"\D", "", postal_code)
        return f"{digits[:5]}-{digits[5:]}"


class QuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=20, initial=1)

