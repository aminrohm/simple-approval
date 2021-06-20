from django.urls import path
from .views import Dashboard,ProcurementApplicationCreate,ProcurementApplicationDetail,ProcurementApplicationUpdate,ProcurementApplicationDelete


app_name ='twx'

urlpatterns = [
#    path('', TemplateView.as_view(template_name='ahinventoryhome.html'),name='search'),
    path('',Dashboard.as_view(),name='home'),
    path('create', ProcurementApplicationCreate.as_view(),name='application-create'),
    path('app/<int:pk>', ProcurementApplicationDetail.as_view(), name='application-detail'),
    path('app/<int:pk>/', ProcurementApplicationUpdate.as_view(), name='application-update'),
    path('app/<int:pk>/delete/', ProcurementApplicationDelete.as_view(), name='application-delete'),
    ]

