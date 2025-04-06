from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import UserGuideStep

def get_guide_steps(request, guide_type='new_user'):
    """
    Return the steps for a specific guide type as JSON
    """
    steps = UserGuideStep.objects.filter(guide_type=guide_type).order_by('order')
    
    # Convert steps to a list of dictionaries
    steps_data = []
    for step in steps:
        steps_data.append({
            'order': step.order,
            'title': step.title,
            'content': step.content,
            'element_selector': step.element_selector,
            'position': step.position,
        })
    
    return JsonResponse({
        'guide_type': guide_type,
        'steps': steps_data
    })

def user_guide_view(request, guide_type='new_user'):
    """
    Render a page that displays a user guide
    """
    # Get the steps for this guide type
    steps = UserGuideStep.objects.filter(guide_type=guide_type).order_by('order')
    
    context = {
        'guide_type': guide_type,
        'steps': steps,
    }
    
    return render(request, 'user_guide/user_guide.html', context)