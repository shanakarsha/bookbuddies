from django.contrib import admin
from django.utils.html import format_html
from . models import Genre,Book
# Register your models here.

class BookAdmin(admin.ModelAdmin):
    list_display=['title', 'author', 'price','cover_pic','genres']

    def cover_pic(self,obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />',obj.image.url)
        return None    
    cover_pic.short_description='Image'   

admin.site.register(Book,BookAdmin)   

class GenreAdmin(admin.ModelAdmin):
    list_display = ('id','name')

admin.site.register(Genre, GenreAdmin)