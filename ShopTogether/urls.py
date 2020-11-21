from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url


handler404 = 'main.views.handler_404'
handler403 = 'main.views.handler_403'
handler500 = 'main.views.handler_500'

admin.site.site_header =  "ErrandsForMe Administration"
admin.site.site_title = "ErrandsForMe Administration"
admin.site.index_title = "Welcome to the ErrandsForMe Administration portal."


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('account/', include('users.urls')),
    url('', include('social_django.urls', namespace='social'))
]
