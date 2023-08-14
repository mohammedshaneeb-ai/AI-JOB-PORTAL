from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def chat_home(request):
    return render(request,'chat/chat.html')


def chat(request):
    if request.method == "POST":
        msg = request.POST.get("msg")
        print(msg)
        response : {
            'welcome': 'hai'
        }
        return JsonResponse({"response": response})

