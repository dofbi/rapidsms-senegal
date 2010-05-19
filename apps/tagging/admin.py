from django.contrib import admin
from tagging.models import Tag, TaggedItem ,BasicTag
from tagging.forms import TagAdminForm

class TagAdmin(admin.ModelAdmin):
    form = TagAdminForm
    fields = ('name', '_children')

admin.site.register(TaggedItem)
admin.site.register(Tag, TagAdmin)
admin.site.register(BasicTag)
# ideally, the admin menu would only show options 
# for 'children' which are themselves tags. (not sure how to do this yet)


