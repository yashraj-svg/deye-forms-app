from django import forms
from django.contrib.auth.models import User
from .models import RepairingForm, InwardForm, OutwardForm, ServiceReportForm, StockRequisition


CUSTOMER_ABBREV_CHOICES = [
    ("Alternative Energy", "Alternative Energy"),
    ("Aps", "Aps"),
    ("Arkay Solar", "Arkay Solar"),
    ("Avirat Energy", "Avirat Energy"),
    ("Brither World Engineering Works", "Brither World Engineering Works"),
    ("Ceyone Solar", "Ceyone Solar"),
    ("Chetanbhai Trimandir", "Chetanbhai Trimandir"),
    ("Deye", "Deye"),
    ("Eco Active Energy & Solution", "Eco Active Energy & Solution"),
    ("Envest Energy Solutions Llp", "Envest Energy Solutions Llp"),
    ("Evaanta Solar", "Evaanta Solar"),
    ("Evvo", "Evvo"),
    ("Ferus Solar Energy Solution", "Ferus Solar Energy Solution"),
    ("Feston", "Feston"),
    ("Fine Vibes Renewable Pvt Ltd (Cg)", "Fine Vibes Renewable Pvt Ltd (Cg)"),
    ("Glowx", "Glowx"),
    ("Green Energy", "Green Energy"),
    ("Green Era", "Green Era"),
    ("Green Watt Energy", "Green Watt Energy"),
    ("Greenedge", "Greenedge"),
    ("Gujarat Energy", "Gujarat Energy"),
    ("Invergy", "Invergy"),
    ("Jaffins Enterprise", "Jaffins Enterprise"),
    ("Jay Aditya Solar", "Jay Aditya Solar"),
    ("Ksolare", "Ksolare"),
    ("Madhav Enterprise", "Madhav Enterprise"),
    ("Madhya Pradesh Solar9", "Madhya Pradesh Solar9"),
    ("Mindra", "Mindra"),
    ("Mp Engineering", "Mp Engineering"),
    ("Navi Energy", "Navi Energy"),
    ("Next Tech Solar Energy", "Next Tech Solar Energy"),
    ("Nil Electronics", "Nil Electronics"),
    ("Nk Construction", "Nk Construction"),
    ("Powerone", "Powerone"),
    ("Pushan Renewable Energy Pvt Ltd", "Pushan Renewable Energy Pvt Ltd"),
    ("Radiant Sun Energy", "Radiant Sun Energy"),
    ("Railway Station Dhanera", "Railway Station Dhanera"),
    ("Roshni Solar", "Roshni Solar"),
    ("Rudra Solar", "Rudra Solar"),
    ("Saan Electrical", "Saan Electrical"),
    ("Shantimani Enterprises", "Shantimani Enterprises"),
    ("Smart Solar Bidgely Solution Pvt Ltd", "Smart Solar Bidgely Solution Pvt Ltd"),
    ("Solaryaan", "Solaryaan"),
    ("Suntech Energy", "Suntech Energy"),
    ("Swami Solar", "Swami Solar"),
    ("Symbroz Solar  Pvt Ltd", "Symbroz Solar  Pvt Ltd"),
    ("Tecnogoods Energy", "Tecnogoods Energy"),
    ("Trambaka Solar  Pvt Ltd", "Trambaka Solar  Pvt Ltd"),
    ("Urja Strot", "Urja Strot"),
    ("Utl", "Utl"),
    ("Utl Solar", "Utl Solar"),
    ("Vsole", "Vsole"),
    ("Waaree", "Waaree"),
    ("Water Sun Solar", "Water Sun Solar"),
    ("Watthut", "Watthut"),
    ("Yamas Solar", "Yamas Solar"),
]


class UserRegistrationForm(forms.ModelForm):
    """Custom user registration form"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'First Name',
            'autocomplete': 'given-name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Last Name',
            'autocomplete': 'family-name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email Address',
            'autocomplete': 'email'
        })
    )
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
            'placeholder': 'Date of Birth'
        }),
        help_text='Select your date of birth'
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Phone Number (Optional)',
            'autocomplete': 'tel'
        })
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Department (Optional)',
            'autocomplete': 'organization-title'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        }),
        help_text='Password must be at least 8 characters long'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        })
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        # Check passwords match
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Passwords do not match!")
        
        # Check password length
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long!")
        
        # Check if email already exists
        email = cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered!")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Generate username from first and last name
        first_name = self.cleaned_data.get('first_name', '').lower().strip()
        last_name = self.cleaned_data.get('last_name', '').lower().strip()
        username = f"{first_name}{last_name}"
        
        # Handle duplicate usernames
        counter = 1
        original_username = username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        user.username = username
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
        
        return user

class RepairingFormForm(forms.ModelForm):
    pcb_specification = forms.CharField(
        max_length=255,
        required=False,
        label='PCB Specification',
        widget=forms.TextInput(attrs={'placeholder': 'Enter PCB Specification'})
    )
    pcb_rating = forms.CharField(
        max_length=255,
        required=False,
        label='PCB Rating',
        widget=forms.TextInput(attrs={'placeholder': 'Enter PCB Rating'})
    )
    class Meta:
        model = RepairingForm
        exclude = ('pcba_serial', 'fault_problems')  # Exclude fault_problems for manual handling
    customer_abbrev = forms.ChoiceField(choices=CUSTOMER_ABBREV_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow inverter_spec to be optional when repairing_object is Battery/PCB
        if 'inverter_spec' in self.fields:
            self.fields['inverter_spec'].required = False
        # Make case_number optional
        if 'case_number' in self.fields:
            self.fields['case_number'].required = False

class InwardFormForm(forms.ModelForm):
    accessories = forms.MultipleChoiceField(
        choices=[('data_logger', 'Data Logger'), ('stand', 'Stand')],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Accessories'
    )
    pcb_serial_number = forms.CharField(
        max_length=255,
        required=False,
        label='PCB Serial Number',
        widget=forms.TextInput(attrs={'placeholder': 'Enter PCB Serial Number'})
    )
    pcb_quantity = forms.IntegerField(
        required=False,
        min_value=1,
        label='No of Quantity',
        widget=forms.NumberInput(attrs={'placeholder': 'Enter quantity'})
    )
    class Meta:
        model = InwardForm
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Always make email field not required
        if 'email' in self.fields:
            self.fields['email'].required = False
        # Dynamically relax requirements based on selected inward object
        inward_object = None
        # Prefer posted data when available
        if hasattr(self, 'data') and self.data:
            inward_object = self.data.get('inward_object')
        elif self.initial:
            inward_object = self.initial.get('inward_object')

        # Default: keep server-side requireds
        # Adjust for Battery/PCB so form doesn't reject hidden inverter fields
        if inward_object and inward_object != 'Inverter':
            if 'inverter_id' in self.fields:
                self.fields['inverter_id'].required = False
            if 'inverter_specs' in self.fields:
                self.fields['inverter_specs'].required = False
            if 'inverter_ratings' in self.fields:
                self.fields['inverter_ratings'].required = False
            # Hide accessories field if not Inverter
            self.fields['accessories'].widget = forms.HiddenInput()

    def clean(self):
        cleaned = super().clean()
        inward_object = self.data.get('inward_object')

        # Enforce minimal requirements by object type without forcing inverter fields
        if inward_object == 'Inverter':
            if not cleaned.get('inverter_id'):
                self.add_error('inverter_id', 'This field is required for Inverter.')
            if not cleaned.get('inverter_specs'):
                self.add_error('inverter_specs', 'This field is required for Inverter.')
        elif inward_object == 'Battery':
            # Ensure some battery identifier if available
            if not cleaned.get('battery'):
                # Not strictly required in model, but guide user
                self.add_error('battery', 'Please provide Battery details for Battery object.')
        # For PCB, no model fields exist; allow save without inverter fields
        return cleaned

class OutwardFormForm(forms.ModelForm):
    control_card_changed = forms.ChoiceField(
        choices=[('', 'Select'), ('No', 'No'), ('Yes', 'Yes')],
        required=False,
        label='Control Card Changed'
    )
    new_serial_number = forms.CharField(
        max_length=100,
        required=False,
        label='New Serial Number'
    )

    accessories = forms.MultipleChoiceField(
        choices=[('data_logger', 'Data Logger'), ('stand', 'Stand')],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Accessories'
    )

    class Meta:
        model = OutwardForm
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        outward_object = None
        if hasattr(self, 'data') and self.data:
            outward_object = self.data.get('outward_object')
        elif self.initial:
            outward_object = self.initial.get('outward_object')

        # For Battery/PCB outward objects, relax inverter-specific fields
        if outward_object and outward_object != 'Inverter':
            for f in ('inverter_id_outward', 'inverter_spec', 'inverter_rating'):
                if f in self.fields:
                    self.fields[f].required = False

        # Always allow empty replacement fields; we'll default in clean()
        for f in ('inverter_replaced', 'replacement_type', 'inverter_id_inward'):
            if f in self.fields:
                self.fields[f].required = False

    def clean(self):
        cleaned = super().clean()
        outward_object = self.data.get('outward_object')

        # Provide safe defaults for replacement fields that were removed from the UI
        if not cleaned.get('inverter_replaced'):
            cleaned['inverter_replaced'] = 'No'
        if not cleaned.get('replacement_type'):
            cleaned['replacement_type'] = ''
        if not cleaned.get('inverter_id_inward'):
            cleaned['inverter_id_inward'] = ''

        # Minimal validation by outward object
        if outward_object == 'Inverter':
            if not cleaned.get('inverter_id_outward'):
                self.add_error('inverter_id_outward', 'This field is required for Inverter.')
            if not cleaned.get('inverter_spec'):
                self.add_error('inverter_spec', 'This field is required for Inverter.')
        # Battery/PCB: do not force inverter fields
        return cleaned

class ServiceReportFormForm(forms.ModelForm):
    class Meta:
        model = ServiceReportForm
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pv_data and ac_data are JSON fields; allow them to be omitted
        for f in ('pv_data', 'ac_data'):
            if f in self.fields:
                self.fields[f].required = False
        # Optional battery count; treat empty as None
        if 'no_of_battery' in self.fields:
            self.fields['no_of_battery'].required = False

    def clean(self):
        cleaned = super().clean()
        # Default JSON fields if missing
        if not cleaned.get('pv_data'):
            cleaned['pv_data'] = []
        if not cleaned.get('ac_data'):
            cleaned['ac_data'] = {}

        # Coerce number of battery if provided
        nob = self.data.get('no_of_battery', '')
        # Handle both string and integer inputs
        if isinstance(nob, int):
            cleaned['no_of_battery'] = nob
        elif isinstance(nob, str):
            nob = nob.strip()
            if nob == '':
                cleaned['no_of_battery'] = None
            else:
                try:
                    cleaned['no_of_battery'] = int(nob)
                except ValueError:
                    self.add_error('no_of_battery', 'Enter a whole number.')
        elif nob is None or nob == '':
            cleaned['no_of_battery'] = None

        return cleaned


class FreightCalculatorForm(forms.Form):
    from_pincode = forms.CharField(label='From Pincode', max_length=6)
    to_pincode = forms.CharField(label='To Pincode', max_length=6)
    weight_kg = forms.FloatField(label='Actual Weight (kg)', min_value=0)
    length_cm = forms.FloatField(label='Length (cm)', min_value=0)
    breadth_cm = forms.FloatField(label='Breadth (cm)', min_value=0)
    height_cm = forms.FloatField(label='Height (cm)', min_value=0)
    reverse_pickup = forms.BooleanField(label='Reverse Pickup', required=False)
    insured_value = forms.FloatField(label='Insured Value (₹)', required=False, min_value=0)
    days_in_transit_storage = forms.IntegerField(label='Storage Days (for demurrage)', required=False, min_value=0, initial=0)
    pieces_max_weight_kg = forms.FloatField(label='Heaviest Piece Weight (kg)', required=False, min_value=0)
    longest_side_cm = forms.FloatField(label='Longest Side (cm)', required=False, min_value=0)
    
    # Bigship service type selection
    BIGSHIP_SERVICE_CHOICES = [
        ('LTL', 'LTL (Part Load) - Standard'),
        ('CFT', 'CFT (Cool Food) - Perishable/Refrigerated'),
        ('MPS', 'MPS (Mega Parcel) - Heavy Parcels'),
    ]
    bigship_service_type = forms.ChoiceField(
        label='Bigship Service Type',
        choices=BIGSHIP_SERVICE_CHOICES,
        initial='LTL',
        required=False,
        widget=forms.RadioSelect
    )

    def clean_from_pincode(self):
        p = self.cleaned_data['from_pincode']
        if not str(p).isdigit() or len(str(p)) != 6:
            raise forms.ValidationError('Enter a valid 6-digit pincode')
        return str(p)

    def clean_to_pincode(self):
        p = self.cleaned_data['to_pincode']
        if not str(p).isdigit() or len(str(p)) != 6:
            raise forms.ValidationError('Enter a valid 6-digit pincode')
        return str(p)


class StockRequisitionForm(forms.ModelForm):
    MANAGER_CHOICES = [
        ('Shrikant', 'Shrikant'),
        ('Rushikesh', 'Rushikesh'),
        ('Sagar K', 'Sagar K'),
        ('Tanaji', 'Tanaji'),
        ('Arun', 'Arun'),
        ('Vinayak', 'Vinayak'),
        ('Nikhil', 'Nikhil'),
        ('Ramesh', 'Ramesh'),
        ('Bhuvan', 'Bhuvan'),
        ('Sanjay', 'Sanjay'),
        ('Sandeep', 'Sandeep'),
        ('Sagar W', 'Sagar W'),
        ('Mohit', 'Mohit'),
        ('Mukesh', 'Mukesh'),
        ('Jayesh', 'Jayesh'),
        ('Kankan', 'Kankan'),
        ('Pranav', 'Pranav'),
        ('Vishal', 'Vishal'),
        ('Vivek', 'Vivek'),
        ('Rahul', 'Rahul'),
        ('Harihara', 'Harihara'),
        ('Ranjan', 'Ranjan'),
        ('Harpreet', 'Harpreet'),
    ]
    
    REQUIRED_TO_CHOICES = [
        ('AE', 'AE - Alternative Energy'),
        ('APS', 'APS - Aps'),
        ('ARKAY', 'ARKAY - Arkay Solar'),
        ('AVIRAT', 'AVIRAT - Avirat Energy'),
        ('BWEW', 'BWEW - Brither World Engineering Works'),
        ('CEYONE', 'CEYONE - Ceyone Solar'),
        ('CT', 'CT - Chetanbhai Trimandir'),
        ('DEYE', 'DEYE - Deye'),
        ('ECOACTIVE', 'ECOACTIVE - Eco Active Energy & Solution'),
        ('ENVEST', 'ENVEST - Envest Energy Solutions Llp'),
        ('EVAANTA', 'EVAANTA - Evaanta Solar'),
        ('EVVO', 'EVVO - Evvo'),
        ('FERUS', 'FERUS - Ferus Solar Energy Solution'),
        ('FESTON', 'FESTON - Feston'),
        ('FVRPL', 'FVRPL - Fine Vibes Renewable Pvt Ltd (Cg)'),
        ('GLOWX', 'GLOWX - Glowx'),
        ('GE', 'GE - Green Energy'),
        ('GERA', 'GERA - Green Era'),
        ('GWE', 'GWE - Green Watt Energy'),
        ('GREANEDGE', 'GREANEDGE - Greenedge'),
        ('GUJARAT', 'GUJARAT - Gujarat Energy'),
        ('INVERGY', 'INVERGY - Invergy'),
        ('JAFFINS', 'JAFFINS - Jaffins Enterprise'),
        ('JAS', 'JAS - Jay Aditya Solar'),
        ('KSOLARE', 'KSOLARE - Ksolare'),
        ('MADHAV', 'MADHAV - Madhav Enterprise'),
        ('MPS9', 'MPS9 - Madhya Pradesh Solar9'),
        ('MINDRA', 'MINDRA - Mindra'),
        ('MPE', 'MPE - Mp Engineering'),
        ('NAVI', 'NAVI - Navi Energy'),
        ('NTSE', 'NTSE - Next Tech Solar Energy'),
        ('NILE', 'NILE - Nil Electronics'),
        ('NKC', 'NKC - Nk Construction'),
        ('POWERONE', 'POWERONE - Powerone'),
        ('PREPL', 'PREPL - Pushan Renewable Energy Pvt Ltd'),
        ('RSE', 'RSE - Radiant Sun Energy'),
        ('RSD', 'RSD - Railway Station Dhanera'),
        ('ROSHNI', 'ROSHNI - Roshni Solar'),
        ('RUDRA', 'RUDRA - Rudra Solar'),
        ('SAAN', 'SAAN - Saan Electrical'),
        ('SHANTIMANI', 'SHANTIMANI - Shantimani Enterprises'),
        ('SSBSP', 'SSBSP - Smart Solar Bidgely Solution Pvt Ltd'),
        ('SOLARYAAN', 'SOLARYAAN - Solaryaan'),
        ('SUNTECH', 'SUNTECH - Suntech Energy'),
        ('SWAMI', 'SWAMI - Swami Solar'),
        ('SYMBROZ', 'SYMBROZ - Symbroz Solar Pvt Ltd'),
        ('TECNOGOODS', 'TECNOGOODS - Tecnogoods Energy'),
        ('TRAMBAKA', 'TRAMBAKA - Trambaka Solar Pvt Ltd'),
        ('URJASTROT', 'URJASTROT - Urja Strot'),
        ('UTL', 'UTL - Utl'),
        ('UTLSOLAR', 'UTLSOLAR - Utl Solar'),
        ('VSOLE', 'VSOLE - Vsole'),
        ('WAAREE', 'WAAREE - Waaree'),
        ('WATERSUN', 'WATERSUN - Water Sun Solar'),
        ('WATTHUT', 'WATTHUT - Watthut'),
        ('YAMAS', 'YAMAS - Yamas Solar'),
        ('For Self', 'For Self'),
    ]
    
    manager_name = forms.ChoiceField(choices=MANAGER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    required_to = forms.ChoiceField(choices=REQUIRED_TO_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    # Component type as selectable but dynamically populated from StockItem
    component_type = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = StockRequisition
        fields = ['serial_number', 'component_type', 'description', 'manager_name', 'quantity_required', 'required_to']
        widgets = {
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter PCBA Serial Number'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter component description'
            }),
            'quantity_required': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Enter quantity required'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate component types from StockItem distinct values
        try:
            from .models import StockItem
            types = list(StockItem.objects.values_list('component_type', flat=True).distinct().order_by('component_type'))
            types = [t for t in types if t]
            # Prepend a placeholder option
            choices = [(t, t) for t in types]
            if not choices:
                choices = [('Other', 'Other')]
            self.fields['component_type'].choices = choices
        except Exception:
            self.fields['component_type'].choices = [('Other', 'Other')]


# Bulk requisition: header and item forms
class StockRequisitionHeaderForm(forms.Form):
    MANAGER_CHOICES = [
        ('Shrikant', 'Shrikant'),
        ('Rushikesh', 'Rushikesh'),
        ('Sagar K', 'Sagar K'),
        ('Tanaji', 'Tanaji'),
        ('Arun', 'Arun'),
        ('Vinayak', 'Vinayak'),
        ('Nikhil', 'Nikhil'),
        ('Ramesh', 'Ramesh'),
        ('Bhuvan', 'Bhuvan'),
        ('Sanjay', 'Sanjay'),
        ('Sandeep', 'Sandeep'),
        ('Sagar W', 'Sagar W'),
        ('Mohit', 'Mohit'),
        ('Mukesh', 'Mukesh'),
        ('Jayesh', 'Jayesh'),
        ('Kankan', 'Kankan'),
        ('Pranav', 'Pranav'),
        ('Vishal', 'Vishal'),
        ('Vivek', 'Vivek'),
        ('Rahul', 'Rahul'),
        ('Harihara', 'Harihara'),
        ('Ranjan', 'Ranjan'),
        ('Harpreet', 'Harpreet'),
    ]

    REQUIRED_TO_CHOICES = [
        ('AE', 'AE - Alternative Energy'),
        ('APS', 'APS - Aps'),
        ('ARKAY', 'ARKAY - Arkay Solar'),
        ('AVIRAT', 'AVIRAT - Avirat Energy'),
        ('BWEW', 'BWEW - Brither World Engineering Works'),
        ('CEYONE', 'CEYONE - Ceyone Solar'),
        ('CT', 'CT - Chetanbhai Trimandir'),
        ('DEYE', 'DEYE - Deye'),
        ('ECOACTIVE', 'ECOACTIVE - Eco Active Energy & Solution'),
        ('ENVEST', 'ENVEST - Envest Energy Solutions Llp'),
        ('EVAANTA', 'EVAANTA - Evaanta Solar'),
        ('EVVO', 'EVVO - Evvo'),
        ('FERUS', 'FERUS - Ferus Solar Energy Solution'),
        ('FESTON', 'FESTON - Feston'),
        ('FVRPL', 'FVRPL - Fine Vibes Renewable Pvt Ltd (Cg)'),
        ('GLOWX', 'GLOWX - Glowx'),
        ('GE', 'GE - Green Energy'),
        ('GERA', 'GERA - Green Era'),
        ('GWE', 'GWE - Green Watt Energy'),
        ('GREANEDGE', 'GREANEDGE - Greenedge'),
        ('GUJARAT', 'GUJARAT - Gujarat Energy'),
        ('INVERGY', 'INVERGY - Invergy'),
        ('JAFFINS', 'JAFFINS - Jaffins Enterprise'),
        ('JAS', 'JAS - Jay Aditya Solar'),
        ('KSOLARE', 'KSOLARE - Ksolare'),
        ('MADHAV', 'MADHAV - Madhav Enterprise'),
        ('MPS9', 'MPS9 - Madhya Pradesh Solar9'),
        ('MINDRA', 'MINDRA - Mindra'),
        ('MPE', 'MPE - Mp Engineering'),
        ('NAVI', 'NAVI - Navi Energy'),
        ('NTSE', 'NTSE - Next Tech Solar Energy'),
        ('NILE', 'NILE - Nil Electronics'),
        ('NKC', 'NKC - Nk Construction'),
        ('POWERONE', 'POWERONE - Powerone'),
        ('PREPL', 'PREPL - Pushan Renewable Energy Pvt Ltd'),
        ('RSE', 'RSE - Radiant Sun Energy'),
        ('RSD', 'RSD - Railway Station Dhanera'),
        ('ROSHNI', 'ROSHNI - Roshni Solar'),
        ('RUDRA', 'RUDRA - Rudra Solar'),
        ('SAAN', 'SAAN - Saan Electrical'),
        ('SHANTIMANI', 'SHANTIMANI - Shantimani Enterprises'),
        ('SSBSP', 'SSBSP - Smart Solar Bidgely Solution Pvt Ltd'),
        ('SOLARYAAN', 'SOLARYAAN - Solaryaan'),
        ('SUNTECH', 'SUNTECH - Suntech Energy'),
        ('SWAMI', 'SWAMI - Swami Solar'),
        ('SYMBROZ', 'SYMBROZ - Symbroz Solar Pvt Ltd'),
        ('TECNOGOODS', 'TECNOGOODS - Tecnogoods Energy'),
        ('TRAMBAKA', 'TRAMBAKA - Trambaka Solar Pvt Ltd'),
        ('URJASTROT', 'URJASTROT - Urja Strot'),
        ('UTL', 'UTL - Utl'),
        ('UTLSOLAR', 'UTLSOLAR - Utl Solar'),
        ('VSOLE', 'VSOLE - Vsole'),
        ('WAAREE', 'WAAREE - Waaree'),
        ('WATERSUN', 'WATERSUN - Water Sun Solar'),
        ('WATTHUT', 'WATTHUT - Watthut'),
        ('YAMAS', 'YAMAS - Yamas Solar'),
        ('For Self', 'For Self'),
    ]

    manager_name = forms.ChoiceField(choices=MANAGER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    required_to = forms.ChoiceField(choices=REQUIRED_TO_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))


class StockRequisitionItemForm(forms.Form):
    serial_number = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control serial-number-input',
        'placeholder': 'Enter PCBA Serial Number'
    }))
    component_type = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 3,
        'placeholder': 'Enter component description'
    }))
    quantity_required = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control qty-required',
            'min': '0',
            'placeholder': 'Enter required qty'
        })
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate component types from StockItem distinct values
        try:
            from .models import StockItem
            types = list(StockItem.objects.values_list('component_type', flat=True).distinct().order_by('component_type'))
            types = [t for t in types if t]
            choices = [(t, t) for t in types] or [('Other', 'Other')]
            self.fields['component_type'].choices = choices
        except Exception:
            self.fields['component_type'].choices = [('Other', 'Other')]

        # Auto-fill quantity_required initial value from StockItem if available
        data = self.data or self.initial
        serial = data.get('serial_number') if data else None
        if serial:
            try:
                from .models import StockItem
                item = StockItem.objects.filter(pcba_sn_new=serial).order_by('-year').first()
                if item:
                    self.fields['quantity_required'].initial = item.quantity
            except Exception:
                pass
