from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from admins.models import Job
from markupsafe import Markup
from django.utils.safestring import mark_safe
from django.template.defaultfilters import linebreaksbr

# Create your views here.

def n2br(value):
    value = r_clearning(value)
    return tuple(item.replace('\n', '<br/>') for item in value)


def r_clearning(value):
    return tuple(item.replace('\r', '') for item in value)


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
    return render(request,'home/submit_job.html',{'job':job})