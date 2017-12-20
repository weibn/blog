from django.shortcuts import render,HttpResponse,redirect
from app02 import models
from django.db.models import Count

# Create your views here.
def seek(request):
    user_id = request.session.get('user_id')
    l = request.session.get('user_permission_dict')
    print(l)
    if not user_id:
        return redirect('/')
    role_list = models.Role.objects.filter(users__user_id=user_id)
    obj = models.Permission2Action2Role.objects.filter(role__in=role_list).values("permission__url","action__code").distinct()
    res = {}
    for row in obj:
        if row['permission__url'] not in res.keys():
            res[row['permission__url']] = []
        res[row['permission__url']].append(row['action__code'])

    request.session['user_permission_dict'] = res
    return HttpResponse('ok!')