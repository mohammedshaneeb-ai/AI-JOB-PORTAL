from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from admins.models import Job
from markupsafe import Markup
from django.utils.safestring import mark_safe
from django.template.defaultfilters import linebreaksbr
import firebase_admin
from firebase_admin import credentials, storage
import requests
import fitz  
from datetime import datetime, timedelta
import pyshorteners
import os
from werkzeug.utils import secure_filename
import PyPDF2
import re
# Create your views here.

cred = credentials.Certificate("/home/mohammed_shaneeb/Desktop/AI-JOB-PORTAL/firebasecrediantials.json")
firebase_admin.initialize_app(cred, {"storageBucket": "resume-qa-4de39.appspot.com"})
bitly_shortener = pyshorteners.Shortener(api_key="1e11476d96a20bbd9924ad6ced6ba426f90039da",timeout=10)
api_key = 'JuFDoAhCjQj9XnLZKiJ7VwHMpoaWGUbYRNBNmLATQPQOfx2f4fnmFyT7Viqi'

@login_required(login_url="signin")
def home(request):
    jobs = Job.objects.all()
    return render(request,'home/index.html',{'jobs':jobs})


def submit_job(request,job_id):
    job = Job.objects.get(pk=job_id)
    print(job.title)
    print(type(job))
    job_description = job.job_description
    domain = job.domain
    # job_description = n2br(job_description)
    # job_description = job_description.replace("\\r", "")
    job_description = job_description.replace("\r\n", "\n").replace("\r", "")
    print(job_description)
    # marked_content = Markup(job_description)
    formatted_description = mark_safe(linebreaksbr(job_description))
    job = {
        'job_description':job_description,
        'domain':domain
    }
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # extracted_text = ""
        # for page_num in range(len(pdf_reader.pages)):
        #     extracted_text += pdf_reader.pages[page_num].extract_text()

        #text extraction
        def extract_text_from_pdf(pdf_file_path):
            text = ''
            with fitz.open(pdf_file_path) as pdf:
                for page_num in range(pdf.page_count):
                    page = pdf[page_num]
                    text += page.get_text()
                    text = text.strip().lower()
                    text = ' '.join(text.split())
            return text
        
        # Save the PDF file to the 'resumes' folder
        file_name = pdf_file.name
        file_path = os.path.join('/home/mohammed_shaneeb/Desktop/AI-JOB-PORTAL/resumes', file_name)
        with open(file_path, 'wb') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        resume_content = extract_text_from_pdf(file_path)
        job_description = re.sub(r'\s+|[•&]', ' ', job_description).lower()
        job_description = job_description.replace("\\r\\n", "")


        print('\n')
        print("Resume Content")
        print(resume_content)
        print('\n')
        print("Job Description")
        print(job_description)

       

    return render(request,'home/submit_job.html',{'job':job})