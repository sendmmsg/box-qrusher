from django.db import models
from taggit.managers import TaggableManager


    #uploaded = models.DateField(auto_now_add=True)

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.IntegerField()
    #description = models.TextField(blank=True, null=True)
    published = models.DateField(auto_now_add=True)
    slug = models.SlugField(unique=True, allow_unicode=True, max_length=300)
    tags = TaggableManager()

    def __str__(self):
        return f"{self.title}"

class PostImage(models.Model):
    pi_id = models.AutoField(primary_key=True)
    image = models.ImageField()
    hidden = models.BooleanField(default=False)
    post = models.ForeignKey(Post,blank = True, null = True, on_delete=models.CASCADE)
