from django.db import models

# Create your models here.
from django.utils import timezone


class Server(models.Model):
    """
    测试前提交的服务器SN、工号等信息
    """
    sn = models.CharField(max_length=30, verbose_name="服务器SN")
    worker = models.CharField(max_length=10, verbose_name="工号")
    ip = models.CharField(max_length=30, verbose_name="IP号")
    submission_date = models.DateTimeField(default=timezone.now, verbose_name="提交时间")

    class Meta:
        verbose_name = "服务器信息"
        verbose_name_plural = verbose_name
        ordering = ['-submission_date']
        db_table = "Server"

    def __str__(self):
        return self.sn
