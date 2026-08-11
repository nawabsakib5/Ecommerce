from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from item.models import Item
from .models import Conversation, ConversationMessage


@login_required
def new_conversation(request, item_pk):
    item = get_object_or_404(Item, pk=item_pk)

    if item.user == request.user:
        return redirect('dashboard:index')

    # existing conversation থাকলে সেখানে redirect করো
    existing = Conversation.objects.filter(
        item=item,
        members=request.user
    ).first()

    if existing:
        return redirect('conversation:detail', pk=existing.id)

    # নতুন conversation তৈরি করো (first message ছাড়াই)
    conversation = Conversation.objects.create(item=item)
    conversation.members.add(request.user)
    conversation.members.add(item.user)
    conversation.save()

    return redirect('conversation:detail', pk=conversation.id)


@login_required
def inbox(request):
    """WhatsApp-style — সব conversations একটা sidebar এ"""
    conversations = (
        Conversation.objects
        .filter(members=request.user)
        .select_related('item', 'item__category')
        .prefetch_related('members', 'messages')
        .order_by('-modified_at')
    )

    # প্রতিটা conversation এ unread count যোগ করো
    for conv in conversations:
        conv.unread = conv.messages.filter(
            is_read=False
        ).exclude(created_by=request.user).count()
        conv.last_message = conv.messages.last()
        conv.other_member = conv.members.exclude(id=request.user.id).first()

    return render(request, 'conversation/inbox.html', {
        'conversations': conversations,
    })


@login_required
def detail(request, pk):
    """WhatsApp-style chat detail — WebSocket ready"""
    conversation = get_object_or_404(
        Conversation.objects.filter(members=request.user),
        pk=pk
    )

    # সব messages read mark করো
    conversation.messages.filter(
        is_read=False
    ).exclude(created_by=request.user).update(is_read=True)

    # Sidebar এর জন্য সব conversations
    all_conversations = (
        Conversation.objects
        .filter(members=request.user)
        .select_related('item')
        .prefetch_related('members', 'messages')
        .order_by('-modified_at')
    )

    for conv in all_conversations:
        conv.unread = conv.messages.filter(
            is_read=False
        ).exclude(created_by=request.user).count()
        conv.last_message = conv.messages.last()
        conv.other_member = conv.members.exclude(id=request.user.id).first()

    messages = conversation.messages.select_related('created_by').order_by('created_at')
    other_member = conversation.members.exclude(id=request.user.id).first()

    return render(request, 'conversation/detail.html', {
        'conversation': conversation,
        'messages': messages,
        'other_member': other_member,
        'all_conversations': all_conversations,
    })