from django.db import models

# Create your models here.


# mes 服务器表
class Mes_server(models.Model):
    product_name = models.CharField(max_length=30, unique=True, verbose_name="产品系列")
    input_date = models.DateTimeField(verbose_name="入库日期")
    output_date = models.DateTimeField(verbose_name="出库日期")

    class Meta:
        verbose_name = "Mes产品系列信息"
        verbose_name_plural = verbose_name
        ordering = ['-input_date']
        db_table = "Mes_server"

    def __str__(self):
        return self.product_name


# mes固件表
class Fireware(models.Model):
    product = models.ForeignKey("Mes_server", on_delete=models.CASCADE, verbose_name="产品系列")
    sn = models.CharField(max_length=30, unique=True, verbose_name="服务器SN")
    system_sn = models.CharField(max_length=50, verbose_name="系统序列号")
    system_vendor = models.CharField(max_length=30, verbose_name="系统制造商")
    system_version = models.CharField(max_length=25, verbose_name="系统版本")
    bois_version = models.CharField(max_length=25, verbose_name="BIOS版本")
    bmc_version = models.CharField(max_length=25, verbose_name="BMC版本")

    class Meta:
        verbose_name = "固件信息"
        verbose_name_plural = verbose_name
        db_table = "Fireware"

    def __str__(self):
        return self.product.product_name


# CPU信息表
class Cpu(models.Model):
    product = models.ForeignKey("Mes_server", on_delete=models.CASCADE, verbose_name="产品系列")
    sn = models.CharField(max_length=50, unique=True, verbose_name="服务器SN")
    type = models.CharField(max_length=50, verbose_name="CPU型号")
    architecture = models.CharField(max_length=20, verbose_name="CPU架构")
    core_number = models.IntegerField(max_length=10, verbose_name="CPU核数")
    thread_number = models.IntegerField(max_length=10, verbose_name="CPU线程数")
    speed = models.CharField(max_length=20, verbose_name="CPU主频")

    class Meta:
        verbose_name = "CPU信息"
        verbose_name_plural = verbose_name
        db_table = "CPU"

    def __str__(self):
        return self.product.product_name
