from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import Context, Template
from django.urls import reverse

from .models import GeneratedWebsite
from .utils import generate_website_with_gemini


@login_required
def DashboardView(request):
    topic = ''
    generated = None
    if request.method == 'POST':
        topic = request.POST.get('topic', '').strip()
        if topic:
            html_content = generate_website_with_gemini(topic)
            generated = GeneratedWebsite.objects.create(
                user=request.user,
                topic=topic,
                html_content=html_content,
            )
            return HttpResponseRedirect(reverse('ai_builder:render_website', args=[generated.id]))

    generated_websites = GeneratedWebsite.objects.filter(user=request.user, deleted_at__isnull=True).order_by('-created_at')
    return render(request, 'ai_builder/dashboard.html', {
        'topic': topic,
        'generated_websites': generated_websites,
    })


@login_required
def RenderWebsiteView(request, website_id):
    generated_website = get_object_or_404(GeneratedWebsite, id=website_id, user=request.user)
    raw_html = generated_website.html_content

    template = Template(raw_html)
    context = Context({'user': request.user})
    rendered_html = template.render(context)

    return HttpResponse(rendered_html)


@login_required
def delete_website(request, pk):
    website = get_object_or_404(GeneratedWebsite, id=pk, user=request.user, deleted_at__isnull=True)
    website.soft_delete()
    messages.success(request, 'Website đã được xóa nhẹ thành công.')
    return redirect('ai_builder:dashboard')
