from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from .models import Post, PostImage
from .forms import PostForm, PostImageForm

from taggit.models import Tag
from django.template.defaultfilters import slugify
from django.http import HttpResponse
from django.db import connection
import base64
import uuid
import os

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

def home_view(request):
    popular = get_tags_popularity()
    print(popular)
    posts = Post.objects.all()
    common_tags = Tag.objects.all()
    #Post.tags.most_common()
    # form = PostForm(request.POST)
    # if form.is_valid():

    #     newpost = form.save(commit=False)
    #     newpost.slug = slugify(newpost.title)
    #     newpost.save()
    #     form.save_m2m()
    # else:
    #     print("home_view: form is not valid!")
    #     print(form.errors)
    context = {
        'posts':posts,
        'common_tags':common_tags,
        'popular_tags':popular
    }
    return render(request, 'home.html', context)

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

def image_view(request):
    posts = Post.objects.all()
    images = PostImage.objects.all
    context = {
        'posts':posts,
        'images':images
    }
    return render(request, 'images.html', context)

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
        return HttpResponse(status=200)

    return HttpResponse(status=500)

def detail_view(request, slug):
    form = PostForm(request.POST)
    images = []
    if form.is_valid():
        t = form.cleaned_data['title']
        post = Post.objects.get(title=t)
        post.tags.set(form.cleaned_data['tags'], clear=True)
        #post.description = form.cleaned_data['description']
        post.save()

    try:
        post = Post.objects.get(slug=slug)
        print("Found existing post")
        print(f"title: {post.title}")
        print(f"tags: {post.tags.all()}")
        #print(f"desc: {post.description}")
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
