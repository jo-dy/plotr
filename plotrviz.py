
import plotr.models
import os
from pylab import *
from filelocations import IMAGE_OUTPUT_DIRECTORY
from filelocations import PLOT_LOGO_PATH

tableau20_RGB = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),  
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),  
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),  
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),  
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]  

tableau20 = [(0.12156862745098039, 0.4666666666666667, 0.7058823529411765), (0.6823529411764706, 0.7803921568627451, 0.9098039215686274), (1.0, 0.4980392156862745, 0.054901960784313725), (1.0, 0.7333333333333333, 0.47058823529411764), (0.17254901960784313, 0.6274509803921569, 0.17254901960784313), (0.596078431372549, 0.8745098039215686, 0.5411764705882353), (0.8392156862745098, 0.15294117647058825, 0.1568627450980392), (1.0, 0.596078431372549, 0.5882352941176471), (0.5803921568627451, 0.403921568627451, 0.7411764705882353), (0.7725490196078432, 0.6901960784313725, 0.8352941176470589), (0.5490196078431373, 0.33725490196078434, 0.29411764705882354), (0.7686274509803922, 0.611764705882353, 0.5803921568627451), (0.8901960784313725, 0.4666666666666667, 0.7607843137254902), (0.9686274509803922, 0.7137254901960784, 0.8235294117647058), (0.4980392156862745, 0.4980392156862745, 0.4980392156862745), (0.7803921568627451, 0.7803921568627451, 0.7803921568627451), (0.7372549019607844, 0.7411764705882353, 0.13333333333333333), (0.8588235294117647, 0.8588235294117647, 0.5529411764705883), (0.09019607843137255, 0.7450980392156863, 0.8117647058823529), (0.6196078431372549, 0.8549019607843137, 0.8980392156862745)]

# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
# for i in range(len(tableau20_RGB)):  
#     r, g, b = tableau20_RGB[i]  
#     tableau20[i] = (r / 255., g / 255., b / 255.) 

variables_by_plot_type = { 'histogram' : 1, 
						'scatterplot' : 2,}



def check_viz_var_string(data_id, viz_type, var_str):
	d = plotr.models.Dataset.objects.get(pk=data_id)
	variables = var_str.split("+")
	if not viz_type in variables_by_plot_type:
		return False
	if not len(variables) == variables_by_plot_type[viz_type]:
		return False
	for var in variables:
		try:
			l = d.fields.get(fieldName = var)
		except plotr.models.DataFields.DoesNotExist:
			return False
	return True

def create_viz(data_id, viz_type, var_str):
	v = plotr.models.Visualization()
	d = plotr.models.Dataset.objects.get(pk=data_id)
	if not check_viz_var_string(data_id, viz_type, var_str):
		return None
	v.dataset = d
	v.viz_type = viz_type
	v.var_string = var_str
	v.save()	
	return v

def render_viz(v, out_folder=IMAGE_OUTPUT_DIRECTORY):	
	#Default style stuff:
	close()	 #This resets the parameters of pylab's chart area. important!
	tick_params(axis="both", which="both", bottom="off", top="off",  
		labelbottom="on", left="off", right="off", labelleft="on")
	ax = subplot(111)  
	ax.spines["top"].set_visible(False)  
	ax.spines["bottom"].set_visible(False)  
	ax.spines["right"].set_visible(False)  
	ax.spines["left"].set_visible(False)
	logo = imread(PLOT_LOGO_PATH)
	figimage(logo)

	if v.viz_type == "histogram":		
		vName = v.var_string				#single variable for histogram
		field = v.dataset.fields.get(fieldName = vName)
		vector = field.as_list()
		outFileName = "%s-histogram-%s.png" % (v.dataset.data_id, vName)
		v.filename = outFileName
		v.save()		
		hist(vector, color=tableau20[1], linewidth = 0)		
		suptitle('Histogram of %s' % vName, fontsize=30)
		savefig('%s' % os.path.join(out_folder, v.filename))		
	elif v.viz_type == "scatterplot":
		vName = v.var_string				#single variable for histogram
		vNames = vName.split("+")
		fields = [v.dataset.fields.get(fieldName = vv) for vv in vNames]
		vectors = [ field.as_list() for field in fields]
		outFileName = "%s-scatterplot-%s.png" % (v.dataset.data_id, vName)
		v.filename = outFileName
		v.save()
		scatter(vectors[1],vectors[0], color=tableau20[0])
		ylabel(vNames[0])
		xlabel(vNames[1])
		suptitle("%s vs %s" % (vNames[0], vNames[1]), fontsize=25)
		savefig('%s' % os.path.join(out_folder, v.filename))				
	else:
		raise NotImplementedError()
	pass