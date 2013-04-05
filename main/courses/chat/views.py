from django.http import Http404
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response

from c2g.models import *
from courses.common_page_data import get_common_page_data
import settings

def prototype(request, course_prefix, course_suffix): # FIXME rename from prototype
    """Provide context for a fullscreen Candy client"""
    user = request.user
    if not request.common_page_data:
        try:
            request.common_page_data = get_common_page_data(request, course_prefix, course_suffix)
        except:
            raise Http404
    jabber_base = getattr(settings, 'JABBER_DOMAIN', '')
    if not jabber_base:
        raise Http404
    if user.is_authenticated():
        chat_name = getattr(user.userprofile, 'chat_name', 'unknown') # DEBUG
        chat_pass = getattr(user.userprofile, 'chat_pass', '')
        if not chat_pass:
            import random
            chat_pass = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789_') for i in range(16)])
            user.userprofile.chat_pass = chat_pass
            user.userprofile.save()
        environment = {
            'request': request,
            'course_prefix': course_prefix,
            'course_suffix': course_suffix,
            'jabber_base': jabber_base,
            'user': user,
            #'nick': user.username + '@' + jabber_base,
            #'nick': user.userprofile.piazza_name + '@' + jabber_base, # DEBUG
            #'pass': user.userprofile.piazza_email,
            'nick': '@'.join((chat_name, jabber_base)),
            'pass': chat_pass,
            'course': request.common_page_data['course'],
        }
        print 'DEBUG: ' + environment['nick']
        return render_to_response('chat/prototype.html', environment, context_instance=RequestContext(request))
    else:
        return redirect('courses.views.main', course_prefix, course_suffix)

