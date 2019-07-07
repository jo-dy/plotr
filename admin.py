from django.contrib import admin
from plotr.models import Dataset, DataFields, DataValues, Visualization

# Register models here

admin.site.register(Dataset)
admin.site.register(DataValues)
admin.site.register(DataFields)
admin.site.register(Visualization)