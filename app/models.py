from django.db import models
from accounts.models import CustomUser
from django.utils import timezone


class Room(models.Model):
    name=models.CharField('会議室', max_length=100)
    
    def __str__(self):
        return self.name


class Staff(models.Model):
    user = models.OneToOneField(CustomUser,  verbose_name = '利用者', on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.user}'


class Booking(models.Model):
    staff = models.ForeignKey(Staff, verbose_name='利用者', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, verbose_name='会議室', on_delete=models.CASCADE)
    first_name =models.CharField('姓', max_length=100, null=True, blank=True)
    last_name =models.CharField('名', max_length=100, null=True, blank=True)
    remarks =models.TextField('備考', default="", blank=True)
    start = models.DateTimeField('開始時間', default=timezone.now)
    end = models.DateTimeField('終了時間', default=timezone.now)

    def __str__(self):
        start = timezone.localtime(self.start).strftime('%Y/%m/%d %H:%M')
        end = timezone.localtime(self.end).strftime('%Y/%m/%d %H:%M')

        return f'{self.first_name}{self.last_name} {start} ~ {end} {self.staff}'
    

