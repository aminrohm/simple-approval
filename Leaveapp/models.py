from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import AbstractUser
from river.models.fields.state import StateField
from djmoney.models.fields import MoneyField
from django_fsm import transition, FSMIntegerField
from crum import get_current_user
from django.utils import timezone
from enum import Enum
import datetime
#from audit_log.models import AuthStampedModel
# Create your models here.
class OrgUnit(MPTTModel):
    TYPES = (
        ('Corp', 'Corporation'),
        ('Dir', 'Directorate'),
        ('Div', 'Division'),
        ('Dept', 'Department'),
        ('Unit', 'Unit'),
    )
    entity_name = models.CharField(max_length=50,blank=False,unique=True)
    entity_type = models.CharField(max_length=50,choices=TYPES)
#    entity_head = models.ForeignKey(Employee,related_name='entity_head',on_delete=models.CASCADE,null=False,blank=False)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    def __str__(self):
        return self.entity_name


class Employee(AbstractUser):
    ROLES = (
        ('Presdir', 'President Director'),
        ('Director', 'Director'),
        ('Division Head', 'Division Head'),
        ('Department Head', 'Department Head'),
        ('Unit Head', 'Unit Head'),
        ('Staff','Staff'),
    )
    username = models.CharField(max_length=200,blank=False,unique=True)
    email = models.EmailField(max_length=200,unique=False,blank=False)
    role = models.CharField(max_length=50,choices=ROLES,blank=False)
    is_admin = models.BooleanField(default=False)
    org_unit = models.ForeignKey(OrgUnit,on_delete=models.CASCADE,null=True,blank=False)
    def __str__(self):
        return self.username


class LeaveApplication(models.Model):
    LeaveDateStart = models.DateField()
    LeaveDateEnd = models.DateField()
#   state_field = StateField()
    
    class Meta:
        permissions = (("can_approve_level1","Can approve level 1"),
                       ("can_reject_level1","Can reject level 1(unit deparment level level)"),
                       ("can_approve_level2","Can approve level 2"),
                       ("can_reject_level2","Can reject level 2(division level)"),
                       ("can_approve_level3","Can approve level 3"),
                       ("can_reject_level3","Can reject level 3(directorat level)"),                       
                       )

class RevisionComment(models.Model):
    created_by       = models.ForeignKey(Employee,related_name='%(class)s_createdby',on_delete=models.CASCADE)
    modified_by      = models.ForeignKey(Employee,related_name='%(class)s_modifiedby',null=True,blank=True,on_delete=models.CASCADE)
    created_on       = models.DateTimeField(auto_now_add=True)
    modified_on      = models.DateTimeField(auto_now=True)
    related_application = models.ForeignKey('ProcurementApplication',related_name='%(class)s_application',on_delete=models.CASCADE)
    comment          = models.TextField()


class StateEnum(Enum):
    CANCELLED = 0
    CREATED = 1
    REJECTED = 2
    DIRS_APPROVED =3
    PD_APPROVED = 4
    
STATES = ('CANCELLED', 'CREATED', 'CHECKED','RETURNED', 'APPROVED', 'REJECTED')
STATES = list(zip(STATES, STATES))

class ProcurementApplication(models.Model):
    CANCELLED = 0
    CREATED = 1
    REVISED = 2
    CHECKED = 3
    RETURNED = 4
    APPROVED = 5
    STATUS_CHOICES = (
        (CANCELLED, 'cancelled'),
        (CREATED, 'created'),
        (REVISED,'revised'),
        (CHECKED, 'checked'),
        (RETURNED, 'returned'),
        (APPROVED, 'approved'),
    )
    created_by       = models.ForeignKey(Employee,related_name='%(class)s_createdby',on_delete=models.CASCADE)
    modified_by      = models.ForeignKey(Employee,related_name='%(class)s_modifiedby',null=True,blank=True,on_delete=models.CASCADE)
    created_on       = models.DateTimeField(auto_now_add=True)
    modified_on      = models.DateTimeField(auto_now=True)
    purpose          = models.CharField(max_length=200,blank=False,unique=False)
    amount           = MoneyField(max_digits=15,decimal_places=0,default_currency='IDR')
    document         = models.FileField(max_length=100,upload_to='documents')
    status = FSMIntegerField(choices=STATUS_CHOICES,default=CREATED,protected=True)
    #status = FSMIntegerField(default=StateEnum.CREATED,protected=True) 
    #status = FSMField(default=STATES[1], choices=STATES)
    
    def __str__(self):
        return self.purpose    
    

    class Meta:
        permissions = (("can_cancel","Can cancel"),
                       ("can_check","Can check and return"),
                       ("can_approve","can approve and reject"),                     
                       )
    
    def is_dir(self):
        current_user = get_current_user()
        return current_user.role=='Director'
    
    def is_presdir(self):
        current_user = get_current_user()
        return current_user.role=='Presdir'
        
    @transition(field=status,source=[CREATED,RETURNED],target=CANCELLED,permission='can_cancel')
    def do_cancel(self):
        pass
        
    @transition(field=status,source=RETURNED,target=REVISED,permission='can_cancel')
    def do_revise(self):
        self.modified_by=get_current_user()
        self.modified_on=datetime.datetime.now()
        pass
        
    @transition(field=status,source=[CREATED,REVISED],target=CHECKED,permission='can_check')
    def do_check(self):
        self.modified_by=get_current_user()
        self.modified_on=datetime.datetime.now()
        pass
        
    
    @transition(field=status,source=[CREATED,REVISED],target=RETURNED,permission='can_check')
    def do_return(self):
        self.modified_by=get_current_user()
        self.modified_on=datetime.datetime.now()
        pass
    
    @transition(field=status,source=CHECKED,target=APPROVED,permission='can_approve')
    def do_approve(self):
        self.modified_by=get_current_user()
        self.modified_on=datetime.datetime.now()
        pass
        
    @transition(field=status,source=CHECKED,target=RETURNED,permission='can_approve')
    def do_reject(self):
        self.modified_by=get_current_user()
        self.modified_on=datetime.datetime.now()
        pass
        

        

