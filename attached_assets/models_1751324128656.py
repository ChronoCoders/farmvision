from django.db import models
from user_registration.models import Users




class Projects(models.Model):

    id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    kat_user = models.ForeignKey('user_registration.Users', on_delete=models.CASCADE)
    Farm = models.CharField(max_length=250, verbose_name='Farm')
    Field = models.CharField(max_length=250, verbose_name='Field')
    Title = models.CharField(max_length=250, verbose_name='Title')
    State = models.CharField(max_length=250, verbose_name='State')
    Data_time = models.DateTimeField(auto_now_add=True)
    picture = models.FileField(upload_to='assets/images',blank=True, null=True,verbose_name='image')
    hashing_path = models.CharField(max_length=250, verbose_name='Hashing Path')
    
    #class Meta:
        #abstract = True

    def __str__(self):
        return self.Farm