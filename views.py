from django.http import HttpResponse
from plotr.dataimport import create_model, fix_data, readcsv
from plotr.plotrviz import render_viz, create_viz, check_viz_var_string, variables_by_plot_type
from plotr.models import Dataset
from plotr.forms import UploadForm
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from filelocations import IMAGE_OUTPUT_DIRECTORY

import os
import tempfile

def trigger_http_500(request):
	response = render_to_response('500.html', {},
    	                          context_instance=RequestContext(request))
	response.status_code = 500
	return response

def trigger_http_404(request):
	#return HttpResponse(status=404)
	response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
	response.status_code = 404
	return response

def get_sharelink(request):
	return request.build_absolute_uri()

def viz_specify_var(request, dataset_id, viz_type):
	try:
		d = Dataset.objects.get(pk=dataset_id)
		f = d.fields.all()
		variables = [g.fieldName for g in f if g.fieldType=="numeric"]		
		n = -1
		if viz_type in variables_by_plot_type.keys():
			n = variables_by_plot_type[viz_type]
			n = range(1, n + 1)
		return render_to_response('plotr/viz_specify.html',
									{"title" 			: d.title, 
									 "data_id"			: dataset_id, 
									 "viz_type"			: viz_type,
									 "variables"		: variables,  
									 "n"				: n,
									 "requestpath"		: request.path,  },
									context_instance=RequestContext(request))
	except Dataset.DoesNotExist:
		return HttpResponse("No data exists for id %s, or it was deleted. Please check your link. " % dataset_id)
	
	

def viz_image(request, dataset_id, viz_type, var_string):
	fName = '%s-%s-%s.png' % (dataset_id, viz_type, var_string)
	fPath = os.path.join(IMAGE_OUTPUT_DIRECTORY, fName)
	try:
		d = Dataset.objects.get(pk=dataset_id)
	except Dataset.DoesNotExist:
		return HttpResponse("No data exists for id %s, or it was deleted. Please check your link. " % dataset_id)
 	try:
		f = open(fPath,'rb')
		return HttpResponse(f.read(), content_type="image/png")
	except IOError:
		pass
	# File has not yet been rendered, so we must create it.
	try:
		v = create_viz(dataset_id, viz_type, var_string)
		if(v):
			render_viz(v)
			f = open(fPath,'rb')
			return HttpResponse(f.read(), content_type="image/png")
		else:
			return render_to_response('plotr/vizerr.html',
									{"title" 			: d.title, 
									 "data_id"			: dataset_id, 
									 "errmsg"			: "Unknown in variable specifier %s for %s" % (var_string, d.title),  
									 "sharelink"		: get_sharelink(request),
									 },context_instance=RequestContext(request)) 
	except IOError:
		pass	
	return HttpResponse("Invalid Request")

def viz_page(request, dataset_id, viz_type, var_string):
	fName = '%s-%s-%s.png' % (dataset_id, viz_type, var_string)
	fPath = os.path.join(IMAGE_OUTPUT_DIRECTORY, fName)	
	try:
		d = Dataset.objects.get(pk=dataset_id)		
	except Dataset.DoesNotExist:
		return HttpResponse("No data exists for id %s, or it was deleted. Please check your link. " % dataset_id)
	if not check_viz_var_string(dataset_id, viz_type, var_string):
		return render_to_response('plotr/vizerr.html',
									{"title" 			: d.title, 
									 "data_id"			: dataset_id, 
									 "errmsg"			: "Unknown in variable specifier %s for %s" % (var_string, d.title),  
									 "sharelink"		: get_sharelink(request),
									}, context_instance=RequestContext(request))
	else:
		return render_to_response('plotr/viz.html',
									{"title" 			: d.title, 
									 "data_id"			: dataset_id, 
									 "viz_type"			: viz_type,
									 "var_string"		: var_string,
									 "img_path"			: "%si" % request.path ,
									 "sharelink"		: get_sharelink(request), },
									context_instance=RequestContext(request))
	


def index(request):
	latest = {}	
	try:
		latestDatasets = Dataset.objects.order_by('pk')[0:6]
		for d in latestDatasets:
			latest[d.data_id] = d.title
	except:	
		pass
	return render_to_response('plotr/home.html',
								{"sharelink"		: get_sharelink(request), 
								 "latest"			: latest,
								},
								context_instance=RequestContext(request))

def summary(request, dataset_id):
	try:
		d = Dataset.objects.get(pk=dataset_id)		
	except Dataset.DoesNotExist:
		return HttpResponse("No data exists for id %s, or it was deleted. Please check your link. " % dataset_id)
	return render_to_response('plotr/summary.html',
									{"title" 			: d.title, 
									 "contents_json"	: d.to_json(),
									 "data_id"			: dataset_id, 
									 "sharelink"		: get_sharelink(request), },
									context_instance=RequestContext(request))	

def tabular(request, dataset_id):		
	try:
		d = Dataset.objects.get(pk=dataset_id)		
	except Dataset.DoesNotExist:
		return HttpResponse("No data exists for id %s, or it was deleted. Please check your link. " % dataset_id)
	return render_to_response('plotr/tabular.html',
									{"title" 			: d.title, 
									 "contents_json"	: d.to_json(),
									 "data_id"			: dataset_id,   
									 "sharelink"		: get_sharelink(request), },
									context_instance=RequestContext(request))

def upload(request):
	if request.method == 'POST':		#Form submitted
		form = UploadForm(request.POST, request.FILES)				
		#TODO: move this file save piece to utility function in dataimport
		try:
			t = tempfile.mkstemp()
			f = os.fdopen(t[0], 'w')
			for chunk in request.FILES['docfile'].chunks():
				f.write(chunk)
			f.close()
			filepath = t[1]			
			raw_data = fix_data(readcsv(filepath))
			if raw_data and raw_data['n'] > 0:
				#print "n > 0"
				title = "Uploaded Data"
				if 'title' in request.POST.keys() and request.POST['title']:
					title = request.POST['title']
				m = create_model(raw_data, title)					
				return render_to_response('plotr/uploaded.html',
										{ 'warnings' 	:	raw_data['warnings'],
										  'data_id'		:	m.data_id if m else '',  
										  "sharelink"		: get_sharelink(request), },
										context_instance=RequestContext(request))
			else:
				#print "n <= 0"
				return render_to_response('plotr/uploaded.html',
									{ 'warnings' 	:	raw_data['warnings'],
									  'data_id'		:	'',  
									  "sharelink"		: get_sharelink(request), },
									context_instance=RequestContext(request))
		except Exception as e:				
			#print e
			return render_to_response('plotr/uploaded.html',
									{ 'warnings' 	:	["Exception Importing File. Please verify correctness of file."],
									  'data_id'		:	'',  
									  "sharelink"		: get_sharelink(request), },
									context_instance=RequestContext(request))

	else:
		form = UploadForm()		
		return render_to_response('plotr/upload.html',
									{"form" : form, 
									"sharelink"		: get_sharelink(request), }, 
									context_instance=RequestContext(request))
		