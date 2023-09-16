"""
自定义的分页组件
"""

class Pagination(object):

    def __init__(self,request,page_param="page"):
        page = request.GET.get(page_param, "1")
        if page.isdecimal():
            page = int(page)
        else:
            page = 1
        self.page = page
        print(page,type(page))
