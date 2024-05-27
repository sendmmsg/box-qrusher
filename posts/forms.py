from django import forms
from .models import Post, PostImage

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            # 'description',
            'tags',
        ]

class PostImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields = [
            'image',
        ]
