from django.db import models
from django.db.models import Max
import dataimport
import json
import plotrviz


class DataValues(models.Model):    
    order = models.IntegerField()
    value = models.CharField(max_length=200, default='')
    def __str__(self):
        return "\'%s\' ==> \'%s\'" % (self.order, self.value)

class DataFields(models.Model):    
    values = models.ManyToManyField(DataValues)
    fieldName = models.CharField(max_length=200, default='')
    fieldType = models.CharField(max_length=50, default='text')
    list_json_cache = models.TextField(default='')
    stats_json_cache = models.TextField(default='')
    
    def __str__(self):
        return "DataField %s" % (self.fieldName)
    
    def is_num(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def num(self, s):
        try:
            return float(s)
        except ValueError:
            return None

    def infer_type(self):
        """
            Iterates through values and determines whether the field is likely
            to be numeric or text.
            Returns a string: 'numeric' or 'text'
        """
        nTotal = 0.0
        nScore = 0.0
        for v in self.values.all().order_by('order'):
            nTotal = nTotal + 1
            if (   self.is_num(v.value) 
                    or v.value == "" 
                    or v.value.lower() == "na"):
                nScore = nScore + 1
        nRatio =  nScore / nTotal
        if  nRatio >= 0.8:
            return "numeric"
        return "text"

    def as_list(self):
        """
            Returns an ordered list representing the vector of values
        """
        if self.list_json_cache:
            return json.loads(self.list_json_cache)
        self.fieldType = self.infer_type()
        listval = []
        for v in self.values.all().order_by('order'):
            if self.fieldType == "numeric":
                listval.append(self.num(v.value))
            else:
                listval.append(v.value)
        self.list_json_cache = json.dumps(listval)
        self.save()
        return listval

    def get_stats(self):
        """
            Returns dictionary of stats about the values in the field
            Numeric:
                mean
                median
                min
                max
                NA count
            Text:
                distinct count
        """
        if self.stats_json_cache:
            return json.loads(self.stats_json_cache)
        stats = {}
        v0 = self.as_list()
        if self.fieldType == "numeric":            
            v = [i for i in v0 if i != None] #filter out the Nones
            if len(v) > 0:
                stats['max'] = max(v)
                stats['min'] = min(v)                                
                stats['mean'] = float(sum(v))/len(v)
                vSorted = sorted(v)
                i = (len(vSorted) - 1) // 2
                if len(vSorted) % 2 == 0:
                    stats['median'] = (vSorted[i] + vSorted[i+1])/2
                else:
                    stats['median'] =  vSorted[i]
                stats['NAs'] = len(v0) - len(v)
        else:       #non-numeric field
            distinct = set(v0)
            stats['distinct'] = len(distinct)
            stats['levels']   = list(distinct)
        self.stats_json_cache = json.dumps(stats)
        self.save()
        return stats

class Dataset(models.Model):
    data_id = models.CharField(max_length=40, primary_key=True)
    json_cache = models.TextField(default='')
    title = models.CharField(max_length=200, default="Uploaded Dataset")
    fields = models.ManyToManyField(DataFields)
    
    def __str__(self):
        return "Dataset (%s)" % (self.title)
    
    def to_json_raw(self):
        r =  {  'data_id'   : self.data_id,
                'title'     : self.title,
                'fields'    : [],
            }        
        for f in self.fields.all():
            r['fields'].append( {   'name' : f.fieldName,
                                    'values' :  [] } )
            for v in f.values.all().order_by('order'):
                r['fields'][-1]['values'].append(v.value)
        return json.dumps(r)
    
    def to_json(self):                
        if self.json_cache:
            return self.json_cache 
        nValues = self.fields.all()[0].values.all().count()
        r = []
        headers = []
        values = {}
        stats = {}
        for f in self.fields.all():
            headers.append(f.fieldName)
            stats[f.fieldName] = f.get_stats()
        for n in range(nValues):
            v = {}
            for f in self.fields.all():
                if not f.fieldName in values:
                    values[f.fieldName] = f.as_list()
                v[f.fieldName] = values[f.fieldName][n] 
            r.append(v)
        final_object = {'headers'   : headers,
                        'data'      : r ,
                        'stats'     : stats,   }
        json_data = json.dumps(final_object)
        self.json_cache = json_data
        self.save()
        return json_data

class Visualization(models.Model):
    dataset = models.ForeignKey(Dataset)
    viz_type = models.CharField(max_length=40)
    var_string = models.CharField(max_length=200)
    filename = models.CharField(max_length=200)    
    def __str__(self):
        return self.filename
    def render(self):
        pass


