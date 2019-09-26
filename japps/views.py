import os
import json
from collections import OrderedDict
import requests
import urllib3.contrib.pyopenssl
import certifi
import urllib3
import magic
import base64
import string

from django import forms
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator, URLValidator
from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.core.mail import EmailMessage, BadHeaderError
from django.contrib import messages
from django.utils.html import escape
from smtplib import SMTPAuthenticationError

from .forms import AppForm, ContactForm


#request.session["token"]=""
#request.session["username"]=""
urllib3.contrib.pyopenssl.inject_into_urllib3()
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
CLIENT_SECRET=os.environ.get('CLIENT_SECRET')
CLIENT_ID=os.environ.get('CLIENT_ID')
RED_URI=os.environ.get('RED_URI')
auth_link="https://agave.iplantc.org/authorize/?client_id="+CLIENT_ID+"&response_type=code&redirect_uri="+RED_URI+"&scope=PRODUCTION"

################the following are the functions for the views###################

def create_form(request, application):
    """
    this function retrieve the json of the given app from the cyverseUK system
    and make it into a user friendly form for submitting the job.
    """
    #request.session["fields"]
    #request.session["job_time"]
    #request.session["ex_json"]
    #request.session["token"]
    #request.session["job_id"]
    #request.session["username"]
    global auth_link
    if request.session.get("token","")=="":
        """
        deal with the posssibility that an user try to access an url in the form
        submission/<app_name> directly from his browser history
        """
        risposta="user needs to authenticate"
        return render(request, "japps/index.html", {"risposta": risposta, "logged": False, "auth_link": auth_link})
        ######fix here
    header={"Authorization": "Bearer "+request.session["token"]}
    r=requests.get("https://agave.iplantc.org/apps/v2/"+application+"?pretty=true", headers=header)
    ex_json=r.json()
    if ex_json.has_key("fault"):
        """
        expired token during browser session, return user to main page
        """
        risposta=ex_json["fault"]["message"]
        return render(request, "japps/index.html", {"risposta": risposta, "logged": False, "auth_link": auth_link})
        #######fix here
    nameapp=ex_json["result"]["name"]
    request.session["job_time"]=str(timezone.now().date())+"-"+str(timezone.now().strftime('%H%M%S'))
    if request.method=='POST':
        """
        form is filled in
        """
        nice_form=AppForm(request.POST, request.FILES,ex_json=ex_json, token=request.session["token"], job_time=request.session["job_time"])
        if nice_form.is_valid():
            """
            if the form is valid the user is addressed to the
            following page.
            take the compiled form and create a json to uplfrom django.utils.html import escapeoad the files
            to the storage system and submit the job via agave.
            """
            request.session["job_time"]=str(timezone.now().date())+"-"+str(timezone.now().strftime('%H%M%S'))
            request.session["json_run"]={}
            request.session["json_run"]["name"]=nice_form.cleaned_data["name_job"]
            #print "*************************************************************"
            #print nice_form.cleaned_data["name_job"]
            #print bool(nice_form.cleaned_data["name_job"])
            request.session["json_run"]["appId"]=ex_json['result']["id"]
            #print json_run
            request.session["json_run"]["inputs"]={}
            request.session["json_run"]["parameters"]={}
            request.session["json_run"]["archive"]=True
            request.session["json_run"]["archiveSystem"]="cyverseUK-Storage2"
            #token=nice_form.cleaned_data["user_token"]
            header={"Authorization": "Bearer "+request.session["token"]}
            for field in request.POST:
                if field!="csrfmiddlewaretoken" and field!="name_job" and field!="user_token" and field!="email" and not field.startswith("django_upload_method"):
                        if nice_form.cleaned_data.get(field) not in [None, ""]:
                            request.session["json_run"]["parameters"][field]=nice_form.cleaned_data.get(field)
                            #print field, nice_form.cleaned_data.get(field)
                        else:
                            if request.POST[field] not in [None, ""]:
                                #print "************", field, request.POST[field]
                                for url in str(request.POST[field]).replace(';',' ').replace(',',' ').split():
                                    #print url
                                    try:
                                        URLValidator()(url)
                                        #print 'success'
                                        #create a temporary directory to uploads the file to (if it doesn't exist already) ####move it from here
                                        request.session["json_run"]["inputs"].setdefault(field,[])
                                        niceurl=str(url).split('/')[-1]
                                        request.session["json_run"]["inputs"][field].append("agave://cyverseUK-Storage2//mnt/data/"+request.session["username"]+"/temp/"+request.session["job_time"]+"/"+niceurl)
                                        requests.put("https://agave.iplantc.org/files/v2/media/system/cyverseUK-Storage2/"+request.session["username"]+"?pretty=true", data={"action":"mkdir","path":"temp"}, headers=header)
                                        requests.put("https://agave.iplantc.org/files/v2/media/system/cyverseUK-Storage2/"+request.session["username"]+"/temp/?pretty=true", data={"action":"mkdir","path":request.session["job_time"]}, headers=header)
                                        requests.post("https://agave.iplantc.org/files/v2/media/system/cyverseUK-Storage2/"+request.session["username"]+"/temp/"+request.session["job_time"]+"/?pretty=true", data={"urlToIngest": url}, headers=header)
                                    except ValidationError, e: ###that's not a valid url
                                        print e
                elif field=="email":
                    if nice_form.cleaned_data.get(field, "").strip()!="":
                        request.session["json_run"]["notifications"]=[]
                        request.session["json_run"]["notifications"].append({})
                        request.session["json_run"]["notifications"][0]["event"]="*"
                        request.session["json_run"]["notifications"][0]["persistent"]=True
                        request.session["json_run"]["notifications"][0]["url"]=nice_form.cleaned_data.get(field)
            if len(request.FILES)>0:
                #create a temporary directory to uploads the files to
                requests.put("https://agave.iplantc.org/files/v2/media/system/cyverseUK-Storage2/"+request.session["username"]+"?pretty=true", data={"action":"mkdir","path":"temp"}, headers=header)
                requests.put("https://agave.iplantc.org/files/v2/media/system/cyverseUK-Storage2/"+request.session["username"]+"/temp/?pretty=true", data={"action":"mkdir","path":request.session["job_time"]}, headers=header)
            for field in request.FILES:
                request.session["json_run"]["inputs"][field]=[]
                for fie in request.FILES.getlist(field):
                    request.session["json_run"]["inputs"][field].append("agave://cyverseUK-Storage2//mnt/data/"+request.session["username"]+"/temp/"+request.session["job_time"]+"/"+fie.name)
                    rr=requests.post("https://agave.iplantc.org/files/v2/media/system/cyverseUK-Storage2/"+request.session["username"]+"/temp/"+request.session["job_time"]+"/?pretty=true", files={"fileToUpload": (fie.name, fie.read())}, headers=request.session["header"])
                    print rr.json()
            request.session["json_run"]=json.dumps(request.session["json_run"])
            request.session["header"]={"Authorization": "Bearer "+request.session["token"], 'Content-Type': 'application/json'}
            r=requests.post("https://agave.iplantc.org/jobs/v2/?pretty=true", data=request.session["json_run"], headers=request.session["header"])
            risposta=r.json()
            if risposta.has_key("fault"):
                #the token is not valid or expired during the process
                risposta=risposta["fault"]["message"]
                #print "****************here***************"
                return render(request, "japps/index.html", {"risposta": risposta, "logged": False, "auth_link": auth_link})
                ##########fix here
            elif risposta["status"]!="success":
                #the user submitted an invalid string, reload the previous page with a warning
                risposta=risposta["message"] ####this will be the warning
                if request.META.get("HTTP_REFERER","")!="":
                    messages.error(request, risposta)
                    return HttpResponseRedirect(request.META.get("HTTP_REFERER",""))
                else:
                    #i think this is needed for users in incognito mode
                    return render(request, "japps/index.html", {"risposta": risposta, "logged": False, "auth_link": auth_link})
                    #########fix here
            else:
                print "B"
                request.session["job_id"]="job-"+str(risposta["result"]["id"])
            return redirect('japps:job_submitted')
        else:
            #print nice_form.errors.as_data()
            print "the form is not valid"
            #get captured in the last render

    else:
        """
        dynamically create a form accordingly to the json file
        """
        nice_form=AppForm(ex_json=ex_json, token=request.session["token"], job_time=request.session["job_time"])
    return render(request, 'japps/submission.html', { "title": nameapp, "description": ex_json["result"]["longDescription"], "nice_form": nice_form, "username": request.session["username"] } )

def submitted(request):
    #request.session["username"]
    try:
      # request.session["job_id"]
      return render(request, "japps/job_submitted.html", {"job_id": request.session.get("job_id",""), "username": request.session["username"]})
    except NameError:
      return redirect('japps:index')

def list_apps(request):
    """
    this function will retrieve the apps available on our system
    cyverseUK-Batch2 and create a list with their names and version. each of
    the item list will be a link calling the create_form() function for that
    specific application.
    """
    #request.session["token"]
    #request.session["username"]
    #request.session["auth_link"]
    if request.session.get("token","")=="":
        risposta="user needs to authenticate"
        request.session["code"]=request.GET.get('code', '')
        #print code
        if request.session.get("code","")!="":
            r=requests.post("https://agave.iplantc.org/token", data={"grant_type": "authorization_code", "code": request.session.get("code",""), "redirect_uri": RED_URI, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET})
            request.session["token"]=r.json()["access_token"]
            #print r.json()
            #print request.session["token"]
            request.session["header"]={"Authorization": "Bearer "+request.session["token"]}
            print request.session["header"]
            r=requests.get("https://agave.iplantc.org/apps/v2?publicOnly=true&executionSystem.eq=cyverseUK-Batch2&pretty=true", headers=request.session["header"])
            #print r.status_code, r.ok, r.text
            userreq=requests.get("https://agave.iplantc.org/profiles/v2/me?pretty=true&naked=true", headers=request.session["header"])
            print userreq.status_code, userreq.ok, userreq.text
            request.session["username"]=userreq.json()["username"]
            print request.session["username"]
            display_list=[]
            request.session["risposta"]=r.json()
            if request.session["risposta"].has_key("fault"):
                message=request.session["risposta"]["fault"]["message"]
                request.session["token"]=""
                return render(request, "japps/index.html", {"risposta": message, "logged": False, "auth_link": auth_link})
            else:
                for el in request.session["risposta"]["result"]:
                    display_list.append(el["id"])
                display_list.sort(key=string.lower)
                print request.META.get('HTTP_REFERER','')
                print request.build_absolute_uri()
                print display_list
                if request.META.get('HTTP_REFERER','')!=request.build_absolute_uri():
                    print "*********************************"
                    return render(request, "japps/index.html", {"risposta": display_list, "logged": True, "username": request.session["username"]})
                    #return HttpResponseRedirect(request.META.get('HTTP_REFERER',''))
                else:
                    return render(request, "japps/index.html", {"risposta": display_list, "logged": True, "username": request.session["username"]})
            #return render(request, "japps/index.html", {"risposta": "ciao ciao", "logged": False}) ########no
        else:
            return render(request, "japps/index.html", {"risposta": risposta, "logged": False, "auth_link": auth_link})
    else:
        print "user is authenticated, getting list of apps"
        request.session["header"]={"Authorization": "Bearer "+request.session["token"]}
        r=requests.get("https://agave.iplantc.org/apps/v2?publicOnly=true&executionSystem.eq=cyverseUK-Batch2&pretty=true", headers=request.session["header"])
        display_list={}
        request.session["risposta"]=r.json()
        if request.session["risposta"].has_key("fault"):
            print "2"
            message=request.session["risposta"]["fault"]["message"]
            request.session["token"]=""
            return render(request, "japps/index.html", {"risposta": message, "logged": False, "auth_link": auth_link})
        else:
            print "3"
            for el in request.session["risposta"]["result"]:
                labeltu=el["label"]
                idtu=el["id"]
                if labeltu is not None:
                    display_list[labeltu[0].upper()+labeltu[1:]]=idtu ####
                else:
                    display_list[idtu[0].upper()+idtu[1:-2]]=idtu
            #print request.META.get('HTTP_REFERER','')
            #print request.build_absolute_uri()
            print display_list
            finaldis=OrderedDict(sorted(display_list.items()))
            return render(request, "japps/index.html", {"risposta": finaldis, "logged": True, "username": request.session["username"]})

def contact(request):
    #request.session["username"]
    contact_form=ContactForm
    if request.method=='POST':
        form=forms.Form(request.POST)
        if form.is_valid():
            """
            if the form is valid the user is addressed to the
            following page.
            """
            name=request.POST.get("name", "")
            email=request.POST.get("email", "")
            subject=request.POST.get("subject", "")
            content=request.POST.get("message","")
            template=get_template('japps/contact_template.txt')
            context={ "name": name, "email": email, "subject": subject, "content": content}
            mail_content=template.render(context)
            email_this=EmailMessage(
                "New contact form submission: "+subject, #subject
                mail_content, #body
                #email, #from email
                #"CyverseUK website" +'', #from_email
                to=[os.environ.get('ALIAS_MAIL')], #to
                headers = {'Reply-To': email } #Reply-To adresses
            )
            try:
                email_this.send(fail_silently=False)
                messages.success(request, "Your request has been submitted. We'll reply as soon as possible. Need more help?")
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            except SMTPAuthenticationError:
                return HttpResponse('Ops! We are having problems, please get in touch throught the Earlham Institute or our Twitter @cyverseuk!')
            return render(request, "japps/contact.html", {"form": contact_form, "username": request.session.get("username","")})
    else:
        return render(request, "japps/contact.html", {"form": contact_form, "username": request.session.get("username","")})

def applications(request):
    #request.session["username"]
    return render(request,'japps/static_description.html', {"username": request.session.get("username", "")})

def app_description(request, app_name):
    #request.session["username"]
    return render(request, 'japps/%(app_name)s.html' % {"app_name": app_name}, {"username": request.session.get("username","")})

def logout(request):
    #request.session["username"]
    #request.session["token"]
    request.session["username"]=""
    request.session["token"]=""
    print request.META.get("HTTP_REFERER", "")
    print request.META.get("HTTP_REFERER", "").split("?")[0]
    if request.META.get("HTTP_REFERER","")!="":
        return HttpResponseRedirect(request.META.get("HTTP_REFERER","").split("?")[0])
    else:
        return redirect('japps:index')

def archive(request):
    #request.session["username"]
    #request.session["token"]
    if request.session.get("username","")=="":
        return redirect('japps:index')
    request.session["header"]={"Authorization": "Bearer "+request.session["token"]}
    download=request.GET.get('download','')
    preview=request.GET.get("preview",'')
    if download!='':
        response=HttpResponse(requests.get("https://agave.iplantc.org/files/v2/media/system/cyverseUK-Storage2/"+request.session["username"]+"/archive/jobs/"+download, headers=request.session["header"]).content, content_type='application/text')
        response['Content-Disposition']='attachment; filename='+download.split('/')[-1]
        return response
    elif preview!='':
        data=requests.get("https://agave.iplantc.org/files/v2/media/system/cyverseUK-Storage2/"+request.session["username"]+"/archive/jobs/"+preview, headers=request.session["header"])
        content_type=magic.from_buffer(data.content, mime=True)
        print content_type
        if content_type=="text/plain" or content_type=="text/x-shellscript":
            response=HttpResponse("<pre>"+escape(data.content)+"</pre>")
            return response
        elif content_type in ["image/png", "image/jpeg", "image/x-portable-bitmap", "image/x-xbitmap"]:
            image=data.content
            b64_img=base64.b64encode(image)
            response=HttpResponse('<img src="data:'+content_type+';base64,'+b64_img+'">')
            return response
        else:
            response="File preview for "+str(content_type)+" files is not yet supported."
            return HttpResponse(response)
    else:
        path=request.GET.get('path', '')+"/"
        print path
        diclinks=OrderedDict()
        if path.strip('/')!='':
            splitpath=path.strip('/').split('/')
        else:
            splitpath=[]
        print splitpath
        for n,key in enumerate(splitpath):
            diclinks[key]=('/').join(splitpath[:n+1])
        print diclinks
        request.session["r"]=requests.get("https://agave.iplantc.org/files/v2/listings/system/cyverseUK-Storage2/"+request.session["username"]+"/archive/jobs/"+path+"?pretty=true", headers=request.session["header"])
        request.session["r"]=request.session["r"].json()
        subdir_list=[]
        file_list=[]
        print request.session["r"]
        if request.session["r"].get("result")!=None:
            for el in request.session["r"]["result"]:
                if el["name"][0]!=".":
                    if el["type"]=="dir":
                        subdir_list.append(el["name"])
                    elif el["type"]=="file":
                        file_list.append(el["name"])
            return render(request, 'japps/archive.html', {"username": request.session["username"], "subdir_list": subdir_list, "file_list": file_list, "path": path, "diclinks": diclinks })
        else:
            messages.error(request, "Oops, something didn't work out!")
            messages.error(request, request.session["r"].get("message"))
            return render(request, 'japps/archive.html', {"username": request.session["username"]})
