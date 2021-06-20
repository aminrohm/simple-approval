from django.shortcuts import render,redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.views.generic.detail import DetailView
from .models import ProcurementApplication,Employee,RevisionComment
from django.contrib.auth.models import User,Permission
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from crum import get_current_user
from django.db.models import Q
from guardian.shortcuts import assign_perm,get_objects_for_user,get_user_perms,get_perms_for_model
from django.http import HttpResponseRedirect
import datetime
# Create your views here.
class Dashboard(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, *args, **kwargs):
        context = super(Dashboard, self).get_context_data(*args, **kwargs)
        

        context['application']=ProcurementApplication.objects.all()
        return context
        
class ProcurementApplicationUpdate(UpdateView):
    model = ProcurementApplication
    fields = ['purpose','amount','document']
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('twx:home')
    
    #def post(self,request,*args,**kwargs):
        #pk = self.kwargs.get('pk')
        #related_object = ProcurementApplication.objects.get(pk=pk)
        
    #    related_object.do_revise()
    #    related_object.save()
    #    return redirect(reverse_lazy('twx:home'))
        
    def form_valid(self, form):
        self.object = form.save()
        self.object.modified_on = datetime.datetime.now()
        self.object.modified_by = Employee.objects.get(username=self.request.user)
        self.object.do_revise()
        self.object.save()
        return redirect(reverse_lazy('twx:home'))
        
        
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        related_object = ProcurementApplication.objects.get(pk=pk)
        try:
            comment = RevisionComment.objects.filter(related_application=related_object)
        except RevisionComment.DoesNotExist:
            comment = None
        context['comment'] = comment
        return context
    
    
    
class ProcurementApplicationDelete(DeleteView):
    model = ProcurementApplication
    success_url = reverse_lazy('twx:home')
    
        
        
class ProcurementApplicationDetail(DetailView):
    model = ProcurementApplication
    
    def post(self, request, *args, **kwargs):
        revision_comment = request.POST.get('comment')
        checked = request.POST.get('check')
        returned = request.POST.get('return')
        approved = request.POST.get('approve')
        rejected = request.POST.get('reject')
        pk = self.kwargs.get('pk')

        related_object = ProcurementApplication.objects.get(pk=pk)
        #related_object.modified_by=get_current_user()
        #related_object.modified_on=datetime.datetime.now()
        app_revision = RevisionComment.objects.create(created_by=get_current_user(),related_application=related_object,comment=revision_comment)

        if checked:
            related_object.do_check()
            related_object.save()
        elif returned:
            related_object.do_return()
            related_object.save()
        elif approved:
            related_object.do_approve()
            related_object.save()
        elif rejected:
            related_object.do_reject()
            related_object.save()

        return redirect(reverse_lazy('twx:home'))
        
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        
        return context




class ProcurementApplicationCreate(LoginRequiredMixin,CreateView):
    login_url = 'login'
    model = ProcurementApplication
    fields = ['purpose','amount','document']
    template_name_suffix = '_create_form'
    success_url = reverse_lazy('twx:home')
    

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        #return super().form_valid(form)
        self.object = form.save()
        #print("self.request ",get_current_user())
        
        ## Set 'can_cancel' permission to user who posted this application
        perm = Permission.objects.get(codename='can_cancel')
        current_user = Employee.objects.get(username=self.request.user)
        assign_perm(perm,current_user,self.object)
        #

        
        # Find out his superior whose designation is 'Director' then assign permission 'can_check' to him
        ancestor_dir = current_user.org_unit.get_ancestors(ascending=True).filter(entity_type='Dir')
        director = Employee.objects.filter(role='Director',org_unit__in=ancestor_dir)
        perm = Permission.objects.get(codename='can_check')
        assign_perm(perm,director,self.object)
        
        # Find out who the director of this company and assign permission 'can_approve' to him
        presdir = Employee.objects.filter(role='Presdir')
        perm = Permission.objects.get(codename='can_approve')
        assign_perm(perm,presdir,self.object)
        
         
        #print("permission ..=",assigned_to.has_perm('can_cancel',self.object))
        return HttpResponseRedirect(self.get_success_url())
        
    #def post(self,request):
    #    perm = Permission.objects.get(codename='can_cancel')
    #    assigned_to = Employee.objects.get(pk=self.request[id])
    #    assigned_object = ProcurementApplication.object.create(created_by= 
    #    assign_perm(perm,assigned_to,assigned
