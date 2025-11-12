from django import forms
from django.core.exceptions import ValidationError
from .models import Device


class DeviceForm(forms.ModelForm):
    """
    Form for creating and editing GPS devices
    """
    class Meta:
        model = Device
        fields = [
            'user', 'product', 'device_type', 'name',
            'imei', 'device_id', 'serial_number',
            'protocol', 'firmware_version', 'config_settings',
            'status', 'activation_code'
        ]
        widgets = {
            'config_settings': forms.Textarea(attrs={'rows': 3}),
            'firmware_version': forms.TextInput(attrs={'placeholder': 'e.g., 1.2.3'}),
            'activation_code': forms.TextInput(attrs={'placeholder': 'Leave blank for auto-generation'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make user field optional if editing existing device
        if self.instance and self.instance.pk:
            self.fields['user'].required = False

    def clean(self):
        cleaned_data = super().clean()
        imei = cleaned_data.get('imei')
        device_id = cleaned_data.get('device_id')

        if not imei and not device_id:
            raise ValidationError("Either IMEI or Device ID must be provided.")

        return cleaned_data


class DeviceRegistrationForm(forms.ModelForm):
    """
    Simplified form for device registration (user-facing)
    """
    class Meta:
        model = Device
        fields = ['name', 'imei', 'device_id', 'serial_number', 'activation_code']
        widgets = {
            'imei': forms.TextInput(attrs={'placeholder': '15-digit IMEI number'}),
            'device_id': forms.TextInput(attrs={'placeholder': 'Alternative device identifier'}),
            'serial_number': forms.TextInput(attrs={'placeholder': 'Device serial number'}),
            'activation_code': forms.TextInput(attrs={'placeholder': 'Activation code if provided'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        imei = cleaned_data.get('imei')
        device_id = cleaned_data.get('device_id')

        if not imei and not device_id:
            raise ValidationError("Either IMEI or Device ID must be provided.")

        return cleaned_data