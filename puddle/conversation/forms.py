from django import forms
from .models import ConversationMessage

class ConversationMessagesForm(forms.ModelForm):
    class Meta:
        model = ConversationMessage
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full py-4 px-6 rounded-xl border border-gray-200 outline-none focus:border-teal-500',
                'placeholder': 'Type your message...',
                'rows': '1'
            })
        }