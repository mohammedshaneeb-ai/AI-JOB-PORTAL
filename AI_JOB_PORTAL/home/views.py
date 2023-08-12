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
import spacy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import quote
from django.views.decorators.csrf import csrf_protect
from .forms import ContactForm
import json
from django.http import JsonResponse
from .models import Candidate
# Create your views here.

cred = credentials.Certificate("/home/mohammed_shaneeb/Desktop/AI-JOB-PORTAL/firebasecrediantials.json")
firebase_admin.initialize_app(cred, {"storageBucket": "resume-qa-4de39.appspot.com"})
bitly_shortener = pyshorteners.Shortener(api_key="1e11476d96a20bbd9924ad6ced6ba426f90039da",timeout=10)
api_key = 'JuFDoAhCjQj9XnLZKiJ7VwHMpoaWGUbYRNBNmLATQPQOfx2f4fnmFyT7Viqi'

nlp = spacy.load('/home/mohammed_shaneeb/Desktop/AI-JOB-PORTAL/training_Custom_NER/output/model-best')

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

        # Making Fire base link
        pdf_file.seek(0)

        bucket = storage.bucket()
        blob = bucket.blob(pdf_file.name)
        blob.upload_from_file(pdf_file)

        expiration = datetime.utcnow() + timedelta(days=30)

        # Get the download URL (link) of the uploaded file
        download_url = blob.generate_signed_url(expiration)
        print(download_url)
        long_url = download_url
        api_url = f'http://tinyurl.com/api-create.php?url={long_url}&apikey={api_key}'
        response = requests.get(api_url)
        short_url = response.text
        print(short_url)

        resume_content = extract_text_from_pdf(file_path)
        job_description = re.sub(r'\s+|[•&]', ' ', job_description).lower()
        job_description = job_description.replace("\\r\\n", "")


        print('\n')
        print("Resume Content")
        print(resume_content)
        print('\n')
        print("Job Description")
        print(job_description)

        def unique_skills(doc):
            skills = []
            unique_skills = []
            for ent in doc.ents:
                if ent.label_ == "SKILL" or ent.label_ == "LANGUAGE":
                    skills.append(ent.text)
                    unique_skills = list(set(skills))
            return unique_skills
        
        def get_name(doc):
            name = ""
            for ent in doc.ents:
                if ent.label_ == "NAME":
                    name = ent.text
            return name
        
        def get_email(doc):
            email = ""
            for ent in doc.ents:
                if ent.label_ == "EMAIL":
                    email = ent.text
            return email
        
        def get_phone(doc):
            phone = ""
            for ent in doc.ents:
                if ent.label_ == "PHONE":
                    phone = ent.text
            return phone
        
        def get_education(doc):
            education = ""
            for ent in doc.ents:
                if ent.label_ == "EDUCATION":
                    education = ent.text
            return education
        def get_place(doc):
            place = ""
            for ent in doc.ents:
                if ent.label_ == "PLACE":
                    place = ent.text
            return place
        
        def similarity_score(resume_skills,job_description_skills):
            
            # Combine both lists to create a corpus
            corpus = resume_skills + job_description_skills

            # Initialize the TF-IDF vectorizer
            vectorizer = TfidfVectorizer()

            # Compute the TF-IDF vectors for the corpus
            tfidf_matrix = vectorizer.fit_transform(corpus)

            # Separate the TF-IDF vectors for resume and job description skills
            resume_tfidf = tfidf_matrix[:len(resume_skills)]
            job_description_tfidf = tfidf_matrix[len(resume_skills):]


            # Compute the Cosine similarity between resume and job description skills
            cosine_similarities = cosine_similarity(resume_tfidf, job_description_tfidf)

            # Get the similarity score for each skill in the resume with respect to job description skills
            resume_scores = cosine_similarities.max(axis=1)

            # Calculate the average similarity score for the entire resume
            resume_similarity_score = np.mean(resume_scores)

            return resume_similarity_score
        
        doc_resume = nlp(resume_content)
        doc_job = nlp(job_description)

            
        resume_skills = unique_skills(doc_resume)
        job_skills = unique_skills(doc_job)

        name = get_name(doc_resume)
        email = get_email(doc_resume)
        place = get_place(doc_resume)
        phone = get_phone(doc_resume)
        education = get_education(doc_resume)

        request.session['nm'] = name
        request.session['em'] = email
        request.session['pl'] = place
        request.session['ph'] = phone
        request.session['ed'] = education
        request.session['resume'] = short_url
        request.session['domain'] = domain

        print(resume_skills)
        print(job_skills)
        print("Name :",name,"Email :",email,"Phone :",phone, "Education :",education, "Place :",place)


        resume_score = similarity_score(resume_skills,job_skills)
        resume_score_10 = round((((resume_score + 1) / 2) * 9 + 1),1)
        print("resume score before :",resume_score)
        resume_score = (resume_score + 1) * 50
        
        
        request.session['sr'] = resume_score
        print(resume_score)

        #resume_skills converting to comma seperated string to save in mysql database
        resume_skills  = ','.join(map(str, resume_skills))
        request.session['skills'] = resume_skills
        request.session['score_10'] = resume_score_10
        


        return redirect('edit_info')
       

    return render(request,'home/submit_job.html',{'job':job})

@csrf_protect
def edit_info(request):
    name = request.session.get('nm')
    email = request.session.get('em')
    place = request.session.get('pl')
    phone = request.session.get('ph')
    education = request.session.get('ed')
    score = request.session.get('sr')
    skills = request.session.get('skills')
    resume_link = request.session.get('resume')
    domain = request.session.get('domain')
    score_10 = request.session.get('score_10')

    print("score is :",score)
    print("new name is ::",name)
    print("skills :",skills)
    details ={
        'name' : name,
        'email' : email,
        'place' : place,
        'phone' : phone,
        'education':education,
        'score':score
    }
    score = round(score,1)
    print("score after round",score)

    if request.method == "POST":
        form = ContactForm(request.POST)

        print(request.POST)
        if form.is_valid():
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            place = request.POST.get('place')
            education = request.POST.get('education')
            experience = request.POST.get('experience')
            age = request.POST.get('age')
            

            applicant = Candidate(
            name=name,
            place=place,
            resume_link=resume_link,
            email=email,
            phone=phone,
            education=education,
            skills=skills,
            age = age,
            experience = experience,
            score = score_10,
            domain = domain
            )
            applicant.save()

            print(name,age,experience,email,phone,place,education)
            # return redirect('/')
            
        else:
            errors = form.errors.as_json()
            print("working errorrrrrrrrrrrr")
            return JsonResponse({"errors": errors}, status=400)
        

    return render(request,'home/edit_information.html',{'details':details})

def success(request):
    return render(request,'home/success.html')