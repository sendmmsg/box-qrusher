from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


from .models import Post, PostImage
from .forms import PostForm, PostImageForm
from .qrgen import render_svg

from taggit.models import Tag
from django.template.defaultfilters import slugify
from django.http import HttpResponse
from django_htmx.http import HttpResponseClientRedirect
from django.db import connection
import base64
import uuid
import os

def auth_view(request):
    username = request.POST["username"]
    password = request.POST["password"]
    next_url = request.POST["next"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # redirect to start page
        return redirect(next_url)
    else:
        # use HX-Events to trigger a modal view on login page
        # informing about authentication error
        return redirect(f"/accounts/login?next={next_url}&msg=error")

def login_view(request):
    n = request.GET.get("next","/")
    msg = request.GET.get("msg", None)
    context = {"next":n, "msg":msg}
    print(f"context: {context}")
    return render(request, 'login.html', context)

def logout_view(request):
    logout(request)
    return redirect("/")

def qrgen_view(request):
    prefix = request.GET.get("prefix","fail")
    startnum = int(request.GET.get("startnum","0"))
    return HttpResponse(render_svg(prefix,startnum))

def qr_view(request):
    context = {}
    return render(request, 'qr.html', context)

def get_tags_popularity():
    clear_unused_tags()
    tags = []
    with connection.cursor() as cursor:
        stmt ="SELECT a.id as pk, name AS tag, count(*) AS freq FROM taggit_tag a LEFT JOIN taggit_taggeditem b ON a.id = b.tag_id GROUP BY b.tag_id ORDER BY freq DESC;"
        pks = []
        cursor.execute(stmt)
        try:
            while True:
                pk, name, freq = cursor.fetchone()
                tags.append({"tag":Tag.objects.get(pk=pk), "freq":freq})
                pks.append(pk)
        except TypeError:
            pass
    #a = Tag.objects.filter(pk__in=pks)
    #print(a)
    return tags



def clear_unused_tags():
    with connection.cursor() as cursor:
        stmt = "DELETE FROM taggit_tag WHERE id in (SELECT a.id FROM taggit_tag a LEFT JOIN taggit_taggeditem b ON a.id = b.tag_id WHERE b.tag_id IS NULL);"
        cursor.execute(stmt)

@login_required
def home_view(request):
    popular = get_tags_popularity()
    posts = Post.objects.all()
    common_tags = Tag.objects.all()
    context = {
        'posts':posts,
        'common_tags':common_tags,
        'popular_tags':popular
    }
    return render(request, 'home.html', context)

@login_required
def upload_view(request, slug):
    form =  PostImageForm(request.POST, request.FILES)
    if form.is_valid():
        print("Valid form!")
        #form.save()
        post = Post.objects.get(title=slug)
        postimage = PostImage.objects.create(image=form.cleaned_data['image'], post=post)
        postimage.save()
        #form.post = post
    else:
        print("Invalid form!")
        print(form.errors)
        for key, value in request.POST.items():
            print('Key: %s' % (key) )
            print("Value:")
            print(value)
            print(type(value))

    return HttpResponse(status=204)

@login_required
def image_view(request):
    posts = Post.objects.all()
    images = PostImage.objects.all
    context = {
        'posts':posts,
        'images':images
    }
    return render(request, 'images.html', context)

@login_required
def tag_image_view(request):
    popular = get_tags_popularity()
    print(popular)
    posts = Post.objects.all()
    images = PostImage.objects.all()
    context = {
        'posts':posts,
        'images':images
    }
    return render(request, 'images.html', context)

@login_required
def rawupload_view(request, slug):
    post = Post.objects.get(title=slug)
    binary = base64.b64decode(request.body)
    print(f"Recieved image size: { len(binary) }")
    print(f"Image belongs to box: {slug}")
    imageName = f"{str(uuid.uuid4().hex)}.jpg"
    filePath = os.path.join(settings.MEDIA_ROOT, imageName)
    print(f"Should write to {filePath}")
    with open(filePath, "wb+") as fp:
        fp.write(binary)
        pi = PostImage()
        pi.image = imageName
        pi.post=post
        pi.save()
        print("Created PostImage and linked to post")
        res=HttpResponse(status=200)
        res.headers['HX-Trigger'] = "wire-reload"
        return res

    return HttpResponse(status=500)

@login_required
def detail_view(request, slug, ws):
    form = PostForm(request.POST)
    images = []
    slug = slug.strip()
    if form.is_valid():
        print("  valid form found")
        print(f" {form.cleaned_data}")
        t = form.cleaned_data['title']
        post = Post.objects.get(slug=slug)
        print(f"  Original tags: {post.tags}")
        post.tags.set(form.cleaned_data['tags'], clear=True)

        print(f"  updated tags: {post.tags}")
        post.save()

    try:
        post = Post.objects.get(slug=slug)
        print("Found existing post")
        print(f"title: {post.title}")
        print(f"tags: {post.tags.all()}")
        images = PostImage.objects.filter(post=post)
    except Post.DoesNotExist as e:
        print("Creating empty post")
        post = Post.objects.create(slug=slug, title=slug)

    common_tags = Post.tags.most_common()
    context = {
        'post':post,
        'common_tags':common_tags,
        'apa':PostImageForm(),
        'images' : images
    }

    clear_unused_tags()
    return render(request, 'detail.html', context)

@login_required
def delimage_view(request,slug):
    print(request.headers)
    pi = PostImage.objects.get(pk=slug)
    if pi.hidden == False:
        print(f"PostImage {pi}  settings to Hidden") 
        pi.hidden = True
    else:
        print(f"PostImage {pi}  settings to Visible") 
        pi.hidden = False
    pi.save()
    url = request.headers["Hx-Current-Url"]
    return HttpResponseClientRedirect(url)

@login_required
def tagged_view(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags=tag)
    #popular = Tag.objects.all()
    popular =  get_tags_popularity()
    print(popular)
    context = {
        'tag':tag,
        'tags':popular,
        'posts':posts,
    }
    return render(request, 'tagged.html', context)
