
from django.db import models

# Create your models here.

from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.html import format_html


class Servers(models.Model):
    """
    测试前提交的服务器SN、工号等信息
    """
    sn = models.CharField(max_length=30, unique=True, verbose_name="服务器SN")
    worker = models.CharField(max_length=30, verbose_name="工号")
    ip = models.CharField(max_length=30, verbose_name="IP号")
    submission_date = models.DateTimeField(default=timezone.now, verbose_name="提交时间")

    class Meta:
        verbose_name = "服务器信息"
        verbose_name_plural = verbose_name
        ordering = ['-submission_date']
        db_table = "Servers"

    def __str__(self):
        return self.sn


class SubmitLog(models.Model):
    """
    上传测试完成的log日志
    """
    server = models.ForeignKey("Servers", on_delete=models.CASCADE, verbose_name="服务器SN")
    # log = models.FileField(upload_to='./autotest_log', null=True, blank=True, verbose_name="日志")
    file_path = models.CharField(max_length=255, null=True, blank=True, verbose_name="文件存放路径")
    log_date = models.DateTimeField(default=timezone.now, verbose_name="提交时间")

    def __str__(self):
        return self.server.sn

    def download(self):
        path = self.file_path
        button_html = "<a href='{}'>下载文件</a>".format(path)
        return format_html(button_html)
    download.short_description = format_html("""<a  href='#' style="position: relative;left: -12px;">下载文件</a>""")

    def server_worker(self):
        return '%s' % self.server.worker
    server_worker.short_description = '操作员'

    def server_name(self):
        return '%s' % self.server.sn
    server_name.short_description = "日志文件名"

    class Meta:
        verbose_name = "日志信息"
        verbose_name_plural = verbose_name
        ordering = ['-log_date']
        db_table = "SubmitLog"


