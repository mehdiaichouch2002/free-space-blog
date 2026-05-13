from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'tags', 'excerpt', 'content', 'featured_image', 'status', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter a catchy title…'}),
            'excerpt': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief summary of your post (auto-generated if blank)'}),
            'content': forms.Textarea(attrs={'rows': 14, 'placeholder': 'Write your post content here…'}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 3:
            raise forms.ValidationError('Title must be at least 3 characters.')
        return title
