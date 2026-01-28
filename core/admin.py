from django.contrib import admin
from .models import Xray, Prediction

# admin.site.register(Xray)
# admin.site.register(Prediction)
               
class PredictionInline(admin.TabularInline):
    model = Prediction
    extra = 0
    fields = ("label", "score", "x1", "y1", "x2", "y2")
    readonly_fields = fields

@admin.register(Xray)
class XrayAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at")
    search_fields = ("user__username", "user__email")   
    list_filter = ("status", "user")    
    search_help_text = "Kullanıcı arayın"
    inlines = [PredictionInline]
