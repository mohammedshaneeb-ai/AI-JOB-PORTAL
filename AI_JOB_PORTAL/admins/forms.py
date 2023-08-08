from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    # ...
    DOMAIN_CHOICES = [
        ('MERN', 'MERN'),
        ('Data Science', 'Data Science'),
        ('Java', 'Java'),
        ('Machine Learning', 'Machine Learning'),
        ('Data Analytics', 'Data Analytics'),
        ('Data Engineer', 'Data Engineer'),
        ('Dev Ops', 'Dev Ops'),
        ('MEAN', 'MEAN'),
        ('Flutter', 'Flutter'),
        # Add more choices as needed
    ]
    domain = forms.ChoiceField(choices=DOMAIN_CHOICES)
    
    class Meta:
        model = Job
        fields = ['title', 'content', 'job_description', 'domain']

