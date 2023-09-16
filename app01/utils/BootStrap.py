from django import forms

class BootStrapModelForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        #循环找到所有插件，添加class=form-control
        for name, field in self.fields.items():
            #字段中有属性，保留原属性，没有属性则增加属性
            if field.widge.attrs:
                field.widget.attrs["class"]="form-control"
                field.widget.attrs["placeholder"]=field.label
            else:
         		field.widget.attrs = {
                    "class":"form-control",
                    "placeholder":field.label
                              }