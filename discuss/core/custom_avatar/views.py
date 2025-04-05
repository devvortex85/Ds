from avatar.views import change, delete, add
from avatar.forms import PrimaryAvatarForm, DeleteAvatarForm, UploadAvatarForm
from avatar.models import Avatar
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib import messages
from django.template.loader import render_to_string

def custom_change(request, template_name='avatar/change.html'):
    """
    A customized version of the avatar change view to fix display issues.
    """
    if request.method == "POST":
        # Check if a form with 'choice' is submitted (selecting primary avatar)
        if 'choice' in request.POST:
            primary_avatar_form = PrimaryAvatarForm(request.POST, user=request.user)
            if primary_avatar_form.is_valid():
                primary_avatar_form.save()
                messages.success(request, _("Successfully updated your avatar."))
                return HttpResponseRedirect(reverse('avatar:change'))
        else:
            # Pass to the original change view for other POST operations
            return change(request, template_name=template_name)
    
    # Get the user's avatars
    avatars = Avatar.objects.filter(user=request.user).order_by('-primary')
    
    # Create the upload form
    upload_avatar_form = UploadAvatarForm(user=request.user)
    
    return render(request, template_name, {
        'avatars': avatars,
        'upload_avatar_form': upload_avatar_form,
    })

def custom_delete(request, template_name='avatar/confirm_delete.html'):
    """
    A customized version of the avatar delete view.
    """
    if request.method == "POST":
        form = DeleteAvatarForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Successfully deleted your avatar."))
            return HttpResponseRedirect(reverse('avatar:change'))
        else:
            # If the form is not valid, still handle the delete operation
            return delete(request)
    
    return render(request, template_name)