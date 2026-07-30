from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class FisherForm(forms.ModelForm):
    class Meta:
        model = Fisher
        fields = ['first_name', 'last_name', 'name', 'lookup', 'contracted', 'commercial_license']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'lookup': forms.TextInput(attrs={'class': 'form-control'}),
            'contracted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'commercial_license': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ensure consistent Bootstrap classes
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                # Leave checkbox styling as form-check-input
                continue
            field.widget.attrs.setdefault('class', 'form-control')

    def clean_first_name(self):
        val = self.cleaned_data.get('first_name', '')
        return val.strip().capitalize()

    def clean_last_name(self):
        val = self.cleaned_data.get('last_name', '')
        return val.strip().capitalize()

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Model's save() already capitalizes and sets lookup/name if empty,
        # but make sure we persist changes and call model save for any side-effects.
        if commit:
            instance.save()
        return instance

class ObserverForm(forms.ModelForm):
    class Meta:
        model = Observer
        fields = ['first_name', 'last_name', 'agency', 'name']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'agency': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # keep checkbox logic out (none here) and ensure form-control where appropriate
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))

            if isinstance(field.widget, forms.Select):
                    self.fields[name].empty_label = "..."


    def clean_first_name(self):
        val = self.cleaned_data.get('first_name', '')
        return val.strip().capitalize()

    def clean_last_name(self):
        val = self.cleaned_data.get('last_name', '')
        return val.strip().capitalize()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class FishingSiteHPForm(forms.ModelForm):
    class Meta:
        model = FishingSite_HP
        fields = [
            'name', 'latitude', 'longitude', 'river_mi', 'type', 'pool', 'state',
            'county', 'basin', 'trib'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'}),
            'river_mi': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'pool': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'state': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'county': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'basin': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'trib': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))
            
            if isinstance(field.widget, forms.Select):
                    self.fields[name].empty_label = "..."


    def clean_name(self):
        val = self.cleaned_data.get('name', '')
        return val.strip().title()

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get('latitude')
        lon = cleaned.get('longitude')
        if (lat is None) != (lon is None):
            raise forms.ValidationError('Both latitude and longitude must be provided together.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class CrewCreateForm(forms.ModelForm):
    class Meta:
        model = Crew
        fields = ['agency', 'office', 'leader']
        widgets = {
            'agency': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'office': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'leader': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))

            if isinstance(field.widget, forms.Select):
                    self.fields[name].empty_label = "..."

    def clean_leader(self):
        val = self.cleaned_data.get('leader', '')
        return val.strip().title()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class TribForm(forms.ModelForm):
    class Meta:
        model = Trib
        fields = ['basin', 'pool', 'name', 'lat', 'lon', 'rm']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'basin': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'pool': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'lat': forms.NumberInput(attrs={'step': '0.000001', 'class': 'form-control'}),
            'lon': forms.NumberInput(attrs={'step': '0.000001', 'class': 'form-control'}),
            'rm': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))

            if isinstance(field.widget, forms.Select):
                    self.fields[name].empty_label = "..."

    def clean_name(self):
        val = self.cleaned_data.get('name', '')
        return val.strip().title()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class SampleSiteForm(forms.ModelForm):
    class Meta:
        model = SampleSite
        fields = [
            'site_code', 'name', 'latitude', 'longitude', 'river_mi', 'type', 'pool', 'state',
            'county', 'basin', 'trib', 'woody_debris', 'submersed_av'
        ]

        widgets = {
            'site_code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'}),
            'river_mi': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': ''}),
            'pool': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': ''}),
            'state': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': ''}),
            'county': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': ''}),
            'basin': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': ''}),
            'trib': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': ''}),
            'woody_debris': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'submersed_av': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))

            if isinstance(field.widget, forms.Select):
                    self.fields[name].empty_label = "..."

    def clean_name(self):
        val = self.cleaned_data.get('name', '')
        return val.strip().title()

    def clean_site_code(self):
        val = self.cleaned_data.get('site_code', '')
        return val.strip() if val else val

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get('latitude')
        lon = cleaned.get('longitude')
        if (lat is None) != (lon is None):
            raise forms.ValidationError('Both latitude and longitude must be provided together.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class FishingSiteCFForm(forms.ModelForm):
    class Meta:
        model = FishingSite_CF
        fields = [
            'site_code', 'name', 'latitude', 'longitude', 'river_mi', 'type', 'pool', 'state',
            'county', 'basin', 'trib'
        ]

        widgets = {
            'site_code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'}),
            'river_mi': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'pool': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'state': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'county': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'basin': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'trib': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select'}),
            'trib_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))

            if isinstance(field.widget, forms.Select):
                    self.fields[name].empty_label = "..."


    def clean_name(self):
        val = self.cleaned_data.get('name', '')
        return val.strip().title()

    def clean_site_code(self):
        val = self.cleaned_data.get('site_code', '')
        return val.strip() if val else val

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get('latitude')
        lon = cleaned.get('longitude')
        if (lat is None) != (lon is None):
            raise forms.ValidationError('Both latitude and longitude must be provided together.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class CfEventForm(forms.ModelForm):
    class Meta:
        model = CfEvent
        fields = [
            'cf_date', 'fisher', 'observer', 'site', 'latitude', 'longitude', 'gear', 'set_num',
            'start_time', 'end_time', 'gear_length', 'gear_depth', 'mesh_size', 'water_temp_f'
        ]

        widgets = {
            'cf_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'data-date-format': 'Y-m-d', 'autofocus': 'autofocus', 'data-allow-input': 'true'}),
            'fisher': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select...'}),
            'observer': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select...'}),
            'site': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select...'}),
            'latitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'}),
            'gear': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select...'}),
            'set_num': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'text', 'class': 'form-control', 'data-provider': 'timepickr', 'data-time-hrs': 'true', 'data-allow-input': 'true'}),
            'end_time': forms.TimeInput(attrs={'type': 'text', 'class': 'form-control', 'data-provider': 'timepickr', 'data-time-hrs': 'true', 'data-allow-input': 'true'}),
            'gear_length': forms.NumberInput(attrs={'class': 'form-control'}),
            'gear_depth': forms.NumberInput(attrs={'class': 'form-control'}),
            'mesh_size': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'water_temp_f': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        active_contract_fishers = kwargs.pop('active_contract_fishers', False)
        active_observers_first = kwargs.pop('active_observers_first', False)
        super().__init__(*args, **kwargs)
        if active_contract_fishers:
            self.fields['fisher'].queryset = Fisher.objects.filter(
                contracted=True,
                active=True,
            ).order_by('last_name', 'first_name')
        if active_observers_first:
            self.fields['observer'].queryset = Observer.objects.order_by(
                '-active', 'last_name', 'first_name'
            )
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get('latitude')
        lon = cleaned.get('longitude')
        if (lat is None) != (lon is None):
            raise forms.ValidationError('Provide both latitude and longitude or leave both blank.')

        start = cleaned.get('start_time')
        end = cleaned.get('end_time')
        if start and end and end <= start:
            raise forms.ValidationError('End time must be later than start time.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class CfEventForm2(forms.Form):
    cf_date = forms.DateField(
        label='Date',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'data-date-format': 'Y-m-d',
            'placeholder': 'YYYY-MM-DD',
        })
    )
    fisher = forms.ModelChoiceField(
        queryset=Fisher.objects.filter(contracted=True).order_by('-active', 'last_name', 'first_name'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select a fisher'}),
        empty_label='...'
    )
    observer = forms.ModelChoiceField(
        queryset=Observer.objects.order_by('-active', 'last_name', 'first_name'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select an observer'}),
        empty_label='...'
    )
    site =  forms.ModelChoiceField(
        queryset=FishingSite_CF.objects.order_by('river_mi'),
        widget=forms.Select(attrs={'class': 'form-control select2', 'data-toggle': 'select2', 'placeholder': '...'}),
        empty_label='...'
    )
    gear = forms.ModelChoiceField(
        queryset=Gear.objects.order_by('priority'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select gear'}),
        empty_label='...'
    )
    latitude = forms.DecimalField(
        label='Latitude',
        max_digits=8,
        decimal_places=5,
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'})
    )
    longitude = forms.DecimalField(
        label='Longitude',
        max_digits=8,
        decimal_places=5,
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'})
    )
    set_num = forms.IntegerField(
        label='Set Num',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '-'})
    )
    start_time = forms.TimeField(
        label='Set Time',
        required=False,
        widget=forms.TimeInput(attrs={'type': 'text', 'class': 'form-control', 'data-provider': 'timepickr', 'data-time-hrs': 'true', 'allow-input': 'true'})
    )
    end_time = forms.TimeField(
        label='Pull Time',
        required=False,
        widget=forms.TimeInput(attrs={'type': 'text', 'class': 'form-control', 'data-provider': 'timepickr', 'data-time-hrs': 'true', 'allow-input': 'true'})
    )
    gear_length = forms.IntegerField(
        label='Net Length',
        required=False,
        widget=forms.NumberInput(attrs={'step': '50', 'class': 'form-control'})
    )
    gear_depth = forms.IntegerField(
        label='Net Depth',
        required=False,
        widget=forms.NumberInput(attrs={'step': '2', 'class': 'form-control'})
    )
    mesh_size = forms.DecimalField(
        label='Mesh Size',
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.25', 'class': 'form-control'})
    )
    water_temp_f = forms.DecimalField(
        label='Water Temp (°F)',
        max_digits=4,
        decimal_places=1,
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.5', 'class': 'form-control'})
    )

class RaEventForm(forms.ModelForm):
    class Meta:
        model = RaEvent
        fields = [
            'ra_date', 'fisher', 'observer', 'site', 'latitude', 'longitude',
            'gear', 'net_set', 'start_time', 'end_time',
            'gear_length', 'gear_depth', 'mesh_size'
        ]

        widgets = {
            'ra_date': forms.DateInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'data-provider': 'flatpickr',
                'data-date-format': 'Y-m-d',
                'autofocus': 'autofocus'
            }),
            'fisher': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select...'}),
            'observer': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select...'}),
            'site': forms.Select(attrs={'class': 'form-control select2', 'data-toggle': 'select2', 'placeholder': '...'}),
            'latitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control', 'placeholder': '--.-----'}),
            'longitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control', 'placeholder': '--.-----'}),
            'gear': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select...'}),
            'net_set': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '-'}),
            'start_time': forms.DateTimeInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'data-provider': 'flatpickr',
                'data-date-format': 'Y-m-d',
                'data-enable-time': 'true',
                'data-time-format': 'H:i'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'data-provider': 'flatpickr',
                'data-date-format': 'Y-m-d',
                'data-enable-time': 'true',
                'data-time-format': 'H:i'
            }),
            'set_duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '--'}),
            'gear_length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '---'}),
            'gear_depth': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '--'}),
            'mesh_size': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control', 'placeholder': '-.-'}),
            'water_temp_f': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control', 'placeholder': '--.-'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get('latitude')
        lon = cleaned.get('longitude')
        if (lat is None) != (lon is None):
            raise forms.ValidationError('Provide both latitude and longitude or leave both blank.')

        start = cleaned.get('start_time')
        end = cleaned.get('end_time')
        if start and end and end <= start:
            raise forms.ValidationError('End time must be later than start time.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class CfEventBatchInfoForm(forms.Form):
    cf_date = forms.DateField(
        label='Date',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'data-date-format': 'Y-m-d',
            'placeholder': 'YYYY-MM-DD',
        })
    )
    fisher = forms.ModelChoiceField(
        queryset=Fisher.objects.filter(contracted=True).order_by('-active', 'last_name', 'first_name'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select a fisher'}),
        empty_label='...'
    )
    observer = forms.ModelChoiceField(
        queryset=Observer.objects.order_by('-active', 'last_name', 'first_name'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select an observer'}),
        empty_label='...'
    )

class CfEventRowForm(forms.ModelForm):
    class Meta:
        model = CfEvent
        fields = ['gear', 'set_num', 'site', 'latitude', 'longitude', 'start_time', 'end_time', 'gear_length', 'gear_depth', 'mesh_size', 'water_temp_f']
        widgets = {
            'gear': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select...'}),
            'set_num': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': '#'}),
            'site': forms.Select(attrs={'class': 'form-control select2', 'data-toggle': 'select2', 'placeholder': '...'}),
            'latitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'text', 'class': 'form-control', 'data-provider': 'timepickr', 'data-time-hrs': 'true', 'data-allow-input': 'true',}),
            'end_time': forms.TimeInput(attrs={'type': 'text', 'class': 'form-control', 'data-provider': 'timepickr', 'data-time-hrs': 'true', 'data-allow-input': 'true',}),
            'gear_length': forms.NumberInput(attrs={'step': '50', 'class': 'form-control'}),
            'gear_depth': forms.NumberInput(attrs={'step': '2', 'class': 'form-control'}),
            'mesh_size': forms.NumberInput(attrs={'step': '0.25', 'class': 'form-control'}),
            'water_temp_f': forms.NumberInput(attrs={'step': '0.5', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['set_num'].required = False
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))
        
        if 'gear' in self.fields:
            try:
                self.fields['gear'].empty_label = '...'
            except Exception:
                pass

        if 'site' in self.fields:
            try:
                self.fields['site'].empty_label = '...'
            except Exception:
                pass

    def clean_set_num(self):
        value = self.cleaned_data.get('set_num')
        if value is None:
            return value
        if value < 1:
            raise forms.ValidationError('Set number must be 1 or greater.')
        return value

class CfCatchEventForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=CfEvent.objects.all().order_by('-event_id')[:100],
        label='Fishing Event',
        widget=forms.Select(attrs={'class': 'form-control select2', 'data-toggle': 'select2', 'placeholder': '...'}),
        empty_label='...'
    )

    no_fish = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={
            'type': 'checkbox',
            'class': 'form-check-input'
            })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_event = self.initial.get('event') or (self.data.get('event') if self.data else None)
        if initial_event:
            try:
                selected_event = CfEvent.objects.get(pk=initial_event)
                # Union the limited queryset with the selected event
                self.fields['event'].queryset = (self.fields['event'].queryset | CfEvent.objects.filter(pk=selected_event.pk)).distinct()
            except CfEvent.DoesNotExist:
                pass  # Let validation handle invalid IDs

class CfCatchRowForm(forms.ModelForm):
    class Meta:
        model = CfCatch
        fields = ['species', 'healthy_cnt', 'moribund_cnt', 'total_cnt']
        widgets = {
            'species': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
            'healthy_cnt': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'moribund_cnt': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_cnt': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
         }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))

            if isinstance(field.widget, forms.Select):
                    self.fields[name].empty_label = "..."

class IcEventForm(forms.ModelForm):
    class Meta:
        model = IcEvent
        fields = [
            'event_date', 'site', 'project', 'agency', 'crew_lead', 'gear', 'effort_num',
            'latitude', 'longitude', 'effort_min', 'ef_duty_cycle', 'ef_pps_hertz',
            'ef_voltage', 'ef_amps', 'ef_watts', 'net_length_ft', 'net_depth_ft',
            'mesh_size_in', 'start_time', 'end_time', 'carp_sighted', 'yoy_sighted',
            'water_temp_f', 'secchi_depth_in', 'net_set_type', 'ef_cond', 'water_ph',
            'egn_panel_num', 'event_loc_type', 'weather', 'bankside', 'run_distance', 
            'dipper_cnt', 'air_temp_f', 'wind_speed_mph',
            ]

        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'data-date-format': 'Y-m-d', 'placeholder': 'YYYY-MM-DD'}),
            'site': forms.Select(attrs={'class': 'form-control select2', 'data-toggle': 'select2', 'placeholder': '...', 'empty_label': '...'}),
            'project': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
            'agency': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
            'crew_lead': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
            'gear': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
            'effort_num': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 999}),
            'latitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'}),
            'effort_min': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control', 'min': 1, 'max': 999999}),
            'ef_duty_cycle': forms.NumberInput(attrs={'class': 'form-control', 'step': '10'}),
            'ef_pps_hertz': forms.NumberInput(attrs={'class': 'form-control'}),
            'ef_voltage': forms.NumberInput(attrs={'class': 'form-control'}),
            'ef_amps': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'ef_watts': forms.NumberInput(attrs={'class': 'form-control'}),
            'net_length_ft': forms.NumberInput(attrs={'class': 'form-control'}),
            'net_depth_ft': forms.NumberInput(attrs={'class': 'form-control'}),
            'mesh_size_in': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'text', 'class': 'form-control', 'data-provider': 'timepickr', 'data-time-hrs': 'true', 'data-allow-input': 'true',}),
            'end_time': forms.TimeInput(attrs={'type': 'text', 'class': 'form-control', 'data-provider': 'timepickr', 'data-time-hrs': 'true', 'data-allow-input': 'true',}),
            'carp_sighted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'yoy_sighted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'water_temp_f': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'secchi_depth_in': forms.NumberInput(attrs={'class': 'form-control'}),
            'net_set_type': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select...'}),
            'ef_cond': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'water_ph': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'egn_panel_num': forms.NumberInput(attrs={'class': 'form-control'}),
            'event_loc_type': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select...'}),
            'weather': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select...'}),
            'bankside': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select...'}),
            'run_distance': forms.NumberInput(attrs={'step': '0.001', 'class': 'form-control'}),
            'dipper_cnt': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 3}),
            'air_temp_f': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'wind_speed_mph': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['crew_lead'].queryset = Crew.objects.none()
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))

            if isinstance(field.widget, forms.Select):
                    self.fields[name].empty_label = "..."

        site_field = self.fields.get('site')
        if site_field:
            site_field.queryset = SampleSite.objects.none()
            selected_site = self.initial.get('site') or (self.data.get('site') if self.data else None)
            if selected_site:
                try:
                    site_id = int(selected_site)
                except (TypeError, ValueError):
                    site_id = None
                if site_id is not None:
                    site_field.queryset = SampleSite.objects.filter(pk=site_id)

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get('latitude')
        lon = cleaned.get('longitude')
        if (lat is None) != (lon is None):
            raise forms.ValidationError('Provide both latitude and longitude or leave both blank.')

        start = cleaned.get('start_time')
        end = cleaned.get('end_time')
        if start and end and end <= start:
            raise forms.ValidationError('End time must be later than start time.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class EventSelectForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=IcEvent.objects.select_related('site', 'gear').order_by('-event_date', '-event_id')[:250],
        label='',
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'data-toggle': 'select2',
            'placeholder': 'Select sampling event...',
            'data-placeholder': 'Select sampling event...',
            'aria-label': 'Agency Sampling Event',
            'autofocus': 'autofocus',
        }),
        empty_label='Select sampling event...'
    )
    no_fish = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={
            'type': 'checkbox',
            'class': 'form-check-input'
            })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_event = self.initial.get('event') or (self.data.get('event') if self.data else None)
        if initial_event:
            try:
                selected_event = IcEvent.objects.get(pk=initial_event)
                # Union the limited queryset with the selected event
                self.fields['event'].queryset = (self.fields['event'].queryset | IcEvent.objects.filter(pk=selected_event.pk)).distinct()
            except IcEvent.DoesNotExist:
                pass  # Let validation handle invalid IDs

class IcCatchForm(forms.ModelForm):
    class Meta:
        model = IcCatch
        fields = [
            'species', 'fish_sex', 'length_mm', 'weight_g', 'fish_count',
            'spawn_patch', 'collected4ag', 'gonad_stage', 'gonad_wt_g'
        ]
        widgets = {
            'species': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
            'fish_sex': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
            'length_mm': forms.NumberInput(attrs={'step': '1.0', 'class': 'form-control'}),
            'weight_g': forms.NumberInput(attrs={'step': '1.0', 'class': 'form-control'}),
            'fish_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 999}),
            'spawn_patch': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'collected4ag': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gonad_stage': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
            'gonad_wt_g': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': 0, 'max': 999}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))
            
            if isinstance(field.widget, forms.Select):
                self.fields[name].empty_label = "..."


        if 'fish_sex' in self.fields:
            try:
                self.fields['fish_sex'].required = False
            except Exception:
                pass

    def clean(self):
        cleaned = super().clean()

        species = cleaned.get('species')
        fish_sex = cleaned.get('fish_sex')
        length_mm = cleaned.get('length_mm')
        weight_g = cleaned.get('weight_g')
        fish_count = cleaned.get('fish_count')
        gonad_stage = cleaned.get('gonad_stage')
        gonad_wt_g = cleaned.get('gonad_wt_g')
        spawn_patch = bool(cleaned.get('spawn_patch'))
        collected4ag = bool(cleaned.get('collected4ag'))

        # Skip empty rows in formsets.
        has_data = any([
            species is not None,
            fish_sex is not None,
            length_mm is not None,
            weight_g is not None,
            fish_count not in (None, ''),
            bool(gonad_stage),
            gonad_wt_g is not None,
            spawn_patch,
            collected4ag,
        ])
        if not has_data:
            return cleaned

        if species is None:
            self.add_error('species', 'Select a species for each populated row.')
            return cleaned

        species_id = getattr(species, 'pk', None)
        sex_id = getattr(fish_sex, 'pk', None)

        # Species 0 is the "no fish" row and must not include biological measurements.
        if species_id == 0:
            if fish_count not in (None, 0):
                self.add_error('fish_count', 'Use count 0 when species is "No Fish".')
            if length_mm is not None:
                self.add_error('length_mm', 'Length must be blank for "No Fish" rows.')
            if weight_g is not None:
                self.add_error('weight_g', 'Weight must be blank for "No Fish" rows.')
            if gonad_stage:
                self.add_error('gonad_stage', 'Gonad stage must be blank for "No Fish" rows.')
            if gonad_wt_g is not None:
                self.add_error('gonad_wt_g', 'Gonad weight must be blank for "No Fish" rows.')
            if spawn_patch:
                self.add_error('spawn_patch', 'Spawn patch must be off for "No Fish" rows.')
            if collected4ag:
                self.add_error('collected4ag', 'Age and growth must be off for "No Fish" rows.')
            if fish_sex is None:
                cleaned['fish_sex'] = FishSex.objects.filter(sx_id=0).first()
            elif sex_id != 0:
                self.add_error('fish_sex', 'Use "NA" sex for "No Fish" rows.')
            return cleaned

        if fish_count is not None and fish_count < 0:
            self.add_error('fish_count', 'Fish count cannot be negative.')
        if fish_count == 0:
            self.add_error('fish_count', 'Fish count must be at least 1 for captured fish rows.')

        if gonad_wt_g is not None and not gonad_stage:
            self.add_error('gonad_stage', 'Select gonad stage when gonad weight is entered.')

        if fish_sex is None:
            cleaned['fish_sex'] = FishSex.objects.filter(sx_id=0).first()

        return cleaned

class SubsampleBatchInfoForm(forms.Form):
    cf_date = forms.DateField(
        label='Catch Date',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'data-date-format': 'Y-m-d',
            'placeholder': 'YYYY-MM-DD',
        })
    )
    fisher = forms.ModelChoiceField(
        queryset=Fisher.objects.order_by('last_name', 'first_name'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select a fisher'}),
        empty_label='...'
    )
    observer = forms.ModelChoiceField(
        queryset=Observer.objects.order_by('last_name', 'first_name'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select an observer'}),
        empty_label='...'
    )
    pool = forms.ModelChoiceField(
        queryset=Pool.objects.order_by('pool_id'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select a pool'}),
        empty_label='...'
    )
    basin = forms.ModelChoiceField(
        queryset=Basin.objects.order_by('basin_id'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select a basin'}),
        empty_label='...'
    )
    spp = forms.ModelChoiceField(
        queryset=FishSpecies.objects.order_by('-ranked', 'name'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Select a species'}),
        empty_label='...'
    )

class SubsampleForm(forms.ModelForm):
    class Meta:
        model = Subsample
        fields = ['sex', 'length_mm', 'weight_g']
        widgets = {
            'sex': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': 'Sex'}),
            'length_mm': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'weight_g': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))
        
        # Allow sex to be optional on the form; cleaned data or model save will enforce a default if needed
        if 'sex' in self.fields:
            try:
                self.fields['sex'].required = False
                self.fields['sex'].empty_label = '...'
                # If this is a ModelChoiceField, provide an empty option label
                # if hasattr(self.fields['sex'], 'empty_label'):
                #     self.fields['sex'].empty_label = 'NA'
            except Exception:
                pass

    def clean(self):
        cleaned = super().clean()
        length = cleaned.get('length_mm')
        weight = cleaned.get('weight_g')
        sx = cleaned.get('sex')
        print(length, weight, sx)

         # Ensure at least one of length or weight is provided
        if length is None and weight is None:
            raise forms.ValidationError('At least one of length or weight must be provided.')

        # if length_mm > 0, and sex is NONE, then set sex to 0 ('NA') by default
        if length is not None and length > 0 and sx is None:
            cleaned['sex'] = FishSex.objects.get(sx_id=0)  # assuming 0 corresponds to 'NA'

        return cleaned

class IcAgeGrowthBatchInfoForm(forms.Form):
    catch_date = forms.DateField(
        label='Catch Date',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'data-date-format': 'Y-m-d',
            'placeholder': 'YYYY-MM-DD',
        })
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects.order_by('project_id'), required=False,
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': ''}),
        empty_label='...'
    )
    agency = forms.ModelChoiceField(
        queryset=Partner.objects.order_by('partner_id'), required=False,
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': ''}),
        empty_label='...'
    )
    basin = forms.ModelChoiceField(
        queryset=Basin.objects.order_by('basin_id'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': ''}),
        empty_label='...'
    )
    pool = forms.ModelChoiceField(
        queryset=Pool.objects.order_by('pool_id'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': ''}),
        empty_label='...'
    )
    site = forms.ModelChoiceField(
        queryset=SampleSite.objects.select_related('pool','basin').order_by('river_mi'),
        widget=forms.Select(attrs={'class': 'form-control select2', 'data-toggle': 'select2', 'placeholder': ''}),
        empty_label='...'
    )
    spp = forms.ModelChoiceField(
        queryset=FishSpecies.objects.order_by('-ranked', 'name'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': ''}),
        empty_label='...'
    )
    latitude = forms.DecimalField(
        label='Latitude', required=False,
        widget=forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'})
    )
    longitude = forms.DecimalField(
        label='Longitude', required=False,
        widget=forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'})
    )

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get('latitude')
        lon = cleaned.get('longitude')
        if (lat is None) != (lon is None):
            raise forms.ValidationError('Provide both latitude and longitude or leave both blank.')
        return cleaned

class IcAgeGrowthRowForm(forms.ModelForm):
    class Meta:
        model = IcAgeGrowth
        fields = ['length_mm', 'weight_g', 'sex', 'ic_age']
        widgets = {
            'length_mm': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'weight_g': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'sex': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': ''}),
            'ic_age': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))

        if 'sex' in self.fields:
            try:
                self.fields['sex'].required = False
                self.fields['sex'].empty_label = '...'
            except Exception:
                pass

    def clean(self):
        cleaned = super().clean()
        if not self.has_changed():
            return cleaned

        length = cleaned.get('length_mm')
        weight = cleaned.get('weight_g')
        age = cleaned.get('ic_age')

        if length is None and weight is None and age is None:
            raise forms.ValidationError('Provide a length, weight, or age before submitting the row.')

        return cleaned

class RaEventBatchInfoForm(forms.Form):
    ra_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'data-date-format': 'Y-m-d',
            'placeholder': 'YYYY-MM-DD',
        })
    )
    fisher = forms.ModelChoiceField(
        queryset=Fisher.objects.order_by('last_name', 'first_name'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
        empty_label='...'
    )
    observer = forms.ModelChoiceField(
        queryset=Observer.objects.order_by('last_name', 'first_name'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
        empty_label='...'
    )
    site = forms.ModelChoiceField(
        queryset=FishingSite_HP.objects.select_related('basin', 'pool').order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control select2', 'data-toggle': 'select2', 'placeholder': '...'}),
        empty_label='...'
    )
    gear = forms.ModelChoiceField(
        queryset=Gear.objects.order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
        empty_label='...'
    )
    net_set = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    latitude = forms.DecimalField(
        label='Latitude',
        max_digits=8,
        decimal_places=5,
        min_value=0.00001,
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'})
    )
    longitude = forms.DecimalField(
        label='Longitude',
        max_digits=8,
        decimal_places=5,
        max_value=-0.00001,
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'})
    )
    start_time = forms.DateTimeField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    set_time = forms.TimeField(
        label='Start Time',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
            'data-provider': 'timepickr',
            'data-time-hrs': 'true',
            'data-time-format': 'hh:mm',
            'data-allow-input': 'true',
        })
    )
    
    end_time = forms.DateTimeField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    pull_time = forms.TimeField(
        label='End Time',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
            'data-provider': 'timepickr',
            'data-time-hrs': 'true',
            'data-time-format': 'hh:mm',
            'data-allow-input': 'true',
        })
    )
    
    dead_set = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={
            'type': 'checkbox',
            'class': 'form-check-input'
            })
    )

    water_temp_f = forms.DecimalField(
        label='Water Temperature (°F)',
        required=False,
        max_digits=5,
        decimal_places=1,
        widget=forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'})
    )
    
    water_depth_ft = forms.DecimalField(
        label='Water Depth (ft)',
        required=False,
        max_digits=3,
        decimal_places=1,
        widget=forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'})
    )

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get('latitude')
        lon = cleaned.get('longitude')
        if (lat is None) != (lon is None):
            raise forms.ValidationError('Provide both latitude and longitude or leave both blank.')

        # start = cleaned.get('start_time')
        # end = cleaned.get('end_time')
        # if start and end and end <= start:
        #     raise forms.ValidationError('End time must be later than start time.')

        return cleaned

class RaEventRowForm(forms.ModelForm):
    class Meta:
        model = RaEvent
        fields = ['net_num', 'gear_length', 'gear_depth', 'mesh_size']
        widgets = {
            'net_num': forms.HiddenInput(),
            'gear_length': forms.NumberInput(attrs={'class': 'form-control'}),
            'gear_depth': forms.NumberInput(attrs={'class': 'form-control'}),
            'mesh_size': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['net_num'].required = False
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))

class RaCatchEventForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=RaEvent.objects.all().order_by('-ra_date','fisher__lookup','net_set','net_num')[:250],
        label='Ride-Along Event',
        widget=forms.Select(attrs={'class': 'form-control select2', 'data-toggle': 'select2', 'placeholder': ''}),
        empty_label='...'
    )
    no_fish = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={
            'type': 'checkbox',
            'class': 'form-check-input'
            })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_event = self.initial.get('event') or (self.data.get('event') if self.data else None)
        if initial_event:
            try:
                selected_event = RaEvent.objects.get(pk=initial_event)
                # Union the limited queryset with the selected event
                self.fields['event'].queryset = (self.fields['event'].queryset | RaEvent.objects.filter(pk=selected_event.pk)).distinct()
            except RaEvent.DoesNotExist:
                pass  # Let validation handle invalid IDs

class RaCatchRowForm(forms.ModelForm):
    class Meta:
        model = RaCatch
        fields = ['species', 'rel_healthy_cnt', 'rel_moribund_cnt', 'harvest_cnt', 'total_cnt']
        widgets = {
            'species': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
            'rel_healthy_cnt': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'rel_moribund_cnt': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'harvest_cnt': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_cnt': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
         }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))

            if isinstance(field.widget, forms.Select):
                self.fields[name].empty_label = "..."

class IchpCatchEventForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=IchpEvent.objects.none(),
        label='Daily Harvest Event',
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': ''}),
        empty_label='...'
    )
    no_fish = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'type': 'checkbox', 'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        event_id = None
        if self.data:
            event_id = self.data.get('event')
        elif self.initial:
            event_id = self.initial.get('event')
        if event_id:
            try:
                self.fields['event'].queryset = IchpEvent.objects.filter(pk=int(event_id))
            except (TypeError, ValueError):
                pass
 
class IchpCatchRowForm(forms.ModelForm):
    class Meta:
        model = IchpCatch
        fields = ['species', 'rel_healthy_cnt', 'rel_moribund_cnt', 'harvest_cnt', 'total_cnt', 'reported_weight_lb', 'reported_mean_length_in']
        widgets = {
            'species': forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
            'rel_healthy_cnt': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'rel_moribund_cnt': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'harvest_cnt': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_cnt': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'reported_weight_lb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'reported_mean_length_in': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': 0}),
         }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))

            if isinstance(field.widget, forms.Select):
                self.fields[name].empty_label = "..."

class IchpEventBatchInfoForm(forms.Form):
    ichp_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'data-date-format': 'Y-m-d',
            'placeholder': 'YYYY-MM-DD',
        })
    )
    fisher = forms.ModelChoiceField(
        queryset=Fisher.objects.order_by('-active', 'last_name', 'first_name'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
        empty_label='...'
    )
    basin = forms.ModelChoiceField(
        queryset=Basin.objects.order_by('basin_id'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
        empty_label='...'
    )
    gear = forms.ModelChoiceField(
        queryset=Gear.objects.order_by('priority'),
        widget=forms.Select(attrs={'class': 'form-control select', 'data-toggle': 'select', 'placeholder': '...'}),
        empty_label='...'
    )
    agency_obs = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={
            'type': 'checkbox',
            'class': 'form-check-input'
            })
    )

    site = forms.ModelChoiceField(
        queryset=FishingSite_HP.objects.select_related('basin', 'pool').order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control select2', 'data-toggle': 'select2', 'placeholder': '...'}),
        empty_label='...'
    )

    latitude = forms.DecimalField(
        required=False,
        label='Latitude',
        max_digits=8,
        decimal_places=5,
        min_value=0.00001,
        widget=forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'})
    )
    longitude = forms.DecimalField(
        required=False,
        label='Longitude',
        max_digits=8,
        decimal_places=5,
        max_value=-0.00001,
        widget=forms.NumberInput(attrs={'step': '0.00001', 'class': 'form-control'})
    )
    start_time = forms.TimeField(
        required=False,
        label='Start Time',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
            'data-provider': 'timepickr',
            'data-time-hrs': 'true',
            'data-time-format': 'hh:mm',
            'data-allow-input': 'true',
        })
    )
    end_time = forms.TimeField(
        required=False,
        label='End Time',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'class': 'form-control',
            'data-provider': 'timepickr',
            'data-time-hrs': 'true',
            'data-time-format': 'hh:mm',
            'data-allow-input': 'true',
        })
    )

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get('latitude')
        lon = cleaned.get('longitude')
        if (lat is None) != (lon is None):
            raise forms.ValidationError('Provide both latitude and longitude or leave both blank.')

        return cleaned

class IchpEventRowForm(forms.ModelForm):
    class Meta:
        model = IchpEvent
        fields = ['net_haul', 'gear_length', 'gear_depth', 'mesh_size']
        widgets = {
            'net_haul': forms.HiddenInput(),
            'gear_length': forms.NumberInput(attrs={'class': 'form-control'}),
            'gear_depth': forms.NumberInput(attrs={'class': 'form-control'}),
            'mesh_size': forms.NumberInput(attrs={'step': '0.25', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['net_haul'].required = False
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault('class', field.widget.attrs.get('class', 'form-control'))


