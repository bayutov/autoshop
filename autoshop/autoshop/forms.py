from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator, RegexValidator
from .models import Order
User = get_user_model()
class LoginForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={
            'required': 'Обязательное поле.',
            'max_length': 'Пароль должен содержать не более 150 символов.',
            'invalid': 'Пароль может содержать только буквы, цифры и символы @/./+/-/_.',
        },
        validators=[
            MaxLengthValidator(150, message='Пароль должен содержать не более 150 символов.'),
            RegexValidator(
                r'^[\w.@+-]+$',
                message='Пароль может содержать только буквы, цифры и символы @/./+/-/_.'
            ),
        ]
    )

    class Meta:
        model=User
        fields = ["username", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["password"].label = "Пароль"

    def clean(self):
        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]
        #Проверка существования пользователя
        user = User.objects.filter(username=username).first()
        if not user:
            raise forms.ValidationError(f"Пользователь с логином {username} не существует.")
        if not user.check_password(password):
            raise forms.ValidationError("Неверный пароль")
        return self.cleaned_data

class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField(required=False)
    address = forms.CharField(required=False)
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["password"].label = "Пароль"
        self.fields["confirm_password"].label = "Подтверждение пароля"
        self.fields["phone"].label = "Телефон"
        self.fields["address"].label = "Адрес"
        self.fields["email"].label = "E-mail"
        self.fields["first_name"].label = "Имя"
        self.fields["last_name"].label = "Фамилия"
    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Аккаунт с данной почтой уже зарегистрирован.")
        return email
    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f"Логин {username} уже зарегистрирован.")
        return username
    def clean(self):
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]
        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают.")
        return self.cleaned_data
    class Meta:
        model = User
        fields = ["username", "password", "confirm_password", "first_name", "last_name","email", "address", "phone"]

class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order_date"].label = "Назначьте удобную дату получения заказа"

    order_date = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))

    class Meta:
        model = Order
        fields = (
            "first_name", "last_name", "phone", "address", "buying_type", "order_date", "comment"
        )







