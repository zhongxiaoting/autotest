# autotest项目说明
这是一个X86服务器的自动化产测项目，以测试工厂生产的X86服务器的质量。

## 用户使用手册
1、将后端部署到服务器上，前端部署到服务器或者本机都可以
2、直接下载库包：pip install -r requirements.txt
3、直接运行系统：python manage.py runserver 0.0.0.0:8000
4、创建用户之后登录用户测试
5、输入服务器的序列号之后可以对服务器进行测试，
    4.1 测试项包括：服务器的基本信息查询、信息校验、性能测试、一键自动化测试
    4.2 基本信息查询包括：CPU信息查询、内存信息查询、硬盘信息查询、网卡信息查询
    4.3 信息校验包括：系统信息校验、CPU信息校验、内存信息校验、硬盘信息校验
    4.4 性能查询包括：CPU MCE检查、内存CEE检查、CPU压力测试、内存压力测试、硬盘压力测试、网卡压力测试
    4.5 黑名单检查包括：PCIE检查、网口误码率检查、硬盘读写检查等项
6、一键自动化测试是从头到尾进行信息检验、性能测试、黑名单检查，测试通过之后可以将日志上传到远程文件服务器存储，以方便文件上传、下载，
    我写了几篇博客如何利用FastDFS技术上传、下载文件：
    1）docker搭建FastDFS及遇到的问题解决：https://blog.csdn.net/qq_45758854/article/details/124704320
    2）FastDFS下载文件自定义命名：https://blog.csdn.net/qq_45758854/article/details/124726359
7、前端代码：https://github.com/zhongxiaoting/autotest_vue

## 系统页面效果
![image](https://user-images.githubusercontent.com/49242954/169977723-a99ae52d-4e3d-4b6f-b4ea-ba79637809d9.png)
![image](https://user-images.githubusercontent.com/49242954/169977865-f91796e0-3ea8-413f-b28f-30e8f48f6fe2.png)
![image](https://user-images.githubusercontent.com/49242954/169977932-03c45db0-c6ff-48d1-a073-3d0f6bc652b5.png)
![image](https://user-images.githubusercontent.com/49242954/169978021-7fb52dce-d40e-4d86-a59f-d28a32e93934.png)
![image](https://user-images.githubusercontent.com/49242954/169978060-ba9c8f88-0b07-4aed-a31d-b07c30d6b12b.png)
![image](https://user-images.githubusercontent.com/49242954/169978131-bfca13a2-39b6-47c5-8f4d-ab6379b15f5e.png)
![image](https://user-images.githubusercontent.com/49242954/169978275-917068cf-95f5-4ea8-8330-53bea04526c2.png)
![image](https://user-images.githubusercontent.com/49242954/169978294-259cfca2-7138-4770-9327-b8501bdf74ae.png)
![image](https://user-images.githubusercontent.com/49242954/169978342-f7a553fe-9562-4630-8628-9003383e377e.png)
![image](https://user-images.githubusercontent.com/49242954/169978360-eddf0f64-aa02-4f40-89b4-8ea3b94594d6.png)
![image](https://user-images.githubusercontent.com/49242954/169978412-0964dfe5-9bd6-4119-b7d0-5d8ed4199e2d.png)
![image](https://user-images.githubusercontent.com/49242954/169978450-90dc02a8-149b-4f5d-a7ca-b72391113dad.png)
![image](https://user-images.githubusercontent.com/49242954/169978485-d6f521a0-a83a-45aa-913c-78c7569e59d6.png)
![image](https://user-images.githubusercontent.com/49242954/169978569-91ba3fce-f9cf-4941-9fa9-4515f3f8c28f.png)
![image](https://user-images.githubusercontent.com/49242954/169978632-b7a8ea8e-6af6-490a-8b16-41a91fe7df4f.png)
![image](https://user-images.githubusercontent.com/49242954/169978693-a50dd33c-850f-4259-9751-c59aff7ac3f4.png)
![image](https://user-images.githubusercontent.com/49242954/169979006-8da12464-8387-426c-a763-6979cf5352ea.png)
![image](https://user-images.githubusercontent.com/49242954/169979048-2e3dee07-5107-4a85-b593-a798dd23f331.png)
![image](https://user-images.githubusercontent.com/49242954/169979086-3d822ac9-7da1-4d64-ada8-0bb6bd85825a.png)
![image](https://user-images.githubusercontent.com/49242954/169979134-50476551-4591-479a-a5d6-0268f3817551.png)
![image](https://user-images.githubusercontent.com/49242954/169979196-aba0e88f-d254-437a-ae6f-8c2e46d733f6.png)
![image](https://user-images.githubusercontent.com/49242954/169979225-662d9ebc-89f0-428f-966e-6a777ef8561d.png)
![image](https://user-images.githubusercontent.com/49242954/169979593-e4dde983-0b4a-4ed4-98fa-4769d3392500.png)
![image](https://user-images.githubusercontent.com/49242954/169979627-aa3e4c96-afc9-422f-be61-e3ac2015edb5.png)
![image](https://user-images.githubusercontent.com/49242954/169979695-7161665c-9d33-48ef-b906-19cc7874ded2.png)
![image](https://user-images.githubusercontent.com/49242954/169979729-e8d291e2-da06-4ab9-84a3-be082c84dded.png)








