import csv
import array
import shutil
import sys
import os

#athlete = '000_test'
#experiment = 'jump_jo 1'
#athlete = '001_lomakina'
#experiment = 'jump_jo 2'
#athlete = '002_anufriev'
#experiment = 'jump_j 2'
#athlete = '003_khoroshilov'
#experiment = 'jump_jo 1'
#athlete = '004_rakhimova'
#experiment = 'jump_j300 2'

if (len(sys.argv)!=3):
	print("Usage: python osim_processing_prep.py athlete experiment")
	print("Example: python osim_processing_prep.py 001_lomakina \"jump_jo 2\"")	
	exit(0)

athlete = sys.argv[1]
experiment = sys.argv[2]

# no need to change variables below
data_source = 'data/'+athlete+'/'+experiment+'.tsv'
data_target = 'data/'+athlete+'/'+experiment+'.trc'

antropometry = 'data/'+athlete+'/antrop.txt'

scale_config_template = '1_scale_config_template.xml'
ik_config_template = '2_ik_config_template.xml'
id_config_template = '3_id_config_template.xml'
external_forces_template = 'external_forces_template.xml'
analyze_config_template = '4_analyze_config_template.xml'
scale_config = 'data/'+athlete+'/'+'1_scale_config.xml'
ik_config = 'data/'+athlete+'/'+'2_ik_config.xml'
id_config = 'data/'+athlete+'/'+'3_id_config.xml'
external_forces = 'data/'+athlete+'/'+'external_forces.xml'
analyze_config = 'data/'+athlete+'/'+'4_analyze_config.xml'

model_file = 'gait_with_arms.osim'
model_target_file = 'data/'+athlete+'/'+model_file

left_force_source = 'data/'+athlete+'/'+experiment+'_f_1.tsv'
right_force_source = 'data/'+athlete+'/'+experiment+'_f_2.tsv'
forces_target = 'data/'+athlete+'/'+experiment+'_ext_forces.mot'

batch_target = 'data/'+athlete+'/run_opensim.bat'


with open(data_source, 'r') as infile, open(data_target, 'w') as outfile, open(antropometry, 'r') as antropometry_file, open(scale_config_template, 'r') as scale_config_template_file, open(ik_config_template, 'r') as ik_config_template_file, open(analyze_config_template, 'r') as analyze_config_template_file, open(id_config_template, 'r') as id_config_template_file, open(analyze_config, 'w') as analyze_config_file, open(scale_config, 'w') as scale_config_file, open(ik_config, 'w') as ik_config_file, open(id_config, 'w') as id_config_file, open(left_force_source, 'r') as left_force_infile,  open(right_force_source, 'r') as right_force_infile, open(forces_target, 'w') as forces_outfile, open(external_forces_template, 'r') as external_forces_template_file, open(external_forces, 'w') as external_forces_file:
	
	# copying the source model (.osim file)
	shutil.copy(model_file, model_target_file)
	
	# generating .xml configs
	SEX = ''
	WEIGHT = ''
	HEIGHT = ''

	STOP_TIME = ''

	antrop_reader = csv.reader(antropometry_file, delimiter=',', quotechar='"', skipinitialspace=True)
	for row in antrop_reader:
		if row[0].lower() == 'sex':
			SEX = row[1]
		if row[0].lower() == 'weight':
			WEIGHT = row[1]
		if row[0].lower() == 'height':
			HEIGHT = row[1]

	# generating the tsv -> trc files
	reader = csv.reader(infile, delimiter='\t', quotechar='"', skipinitialspace=True)
	writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')

	i = 1
	NO_OF_FRAMES = 0
	NO_OF_CAMERAS = 0
	NO_OF_MARKERS = 0
	FREQUENCY = 0
	MARKER_NAMES = ''
	EXTRA_COLUMNS_TO_BE_REMOVED = 0

	for row in reader:
	    if i <= 10:
	    	print(row)
	    if i == 1:
	    	NO_OF_FRAMES = row[1]
	    if i == 2:
	    	NO_OF_CAMERAS = row[1]
	    if i == 3:
	    	NO_OF_MARKERS = row[1]
	    if i == 4:
	    	FREQUENCY = row[1]
	    
	    if i == 10:
	    	MARKER_NAMES = row

	    	print("writing header to output")
	    	
	    	writer.writerow(['PathFileType', 4,	'(X/Y/Z)', data_target])
	    	writer.writerow(['DataRate','CameraRate','NumFrames','NumMarkers','Units','OrigDataRate','OrigDataStartFrame','OrigNumFrames'])
	    	writer.writerow([FREQUENCY, FREQUENCY, NO_OF_FRAMES, NO_OF_MARKERS, "mm", FREQUENCY, "1", NO_OF_FRAMES])
	    	
	    	print(MARKER_NAMES)

	    	MARKERS_LINE_1 = ['Frame#', 'Time']
	    	MARKERS_LINE_2 = ['', '']
	    	
	    	for x in range(1,int(NO_OF_MARKERS)+1):
	    		MARKERS_LINE_1.append(MARKER_NAMES[x].lower())
	    		MARKERS_LINE_1.append('')
	    		MARKERS_LINE_1.append('')
	    		MARKERS_LINE_2.append('X'+str(x))
	    		MARKERS_LINE_2.append('Y'+str(x))
	    		MARKERS_LINE_2.append('Z'+str(x))

	    	writer.writerow(MARKERS_LINE_1)
	    	writer.writerow(MARKERS_LINE_2)

	    if i == 11:
	    	if row[1] == "Frame":
	    		EXTRA_COLUMNS_TO_BE_REMOVED = EXTRA_COLUMNS_TO_BE_REMOVED + 1
	    	if row[1] == "Time":
	    		EXTRA_COLUMNS_TO_BE_REMOVED = EXTRA_COLUMNS_TO_BE_REMOVED + 1
	    	if row[2] == "Frame":
	    		EXTRA_COLUMNS_TO_BE_REMOVED = EXTRA_COLUMNS_TO_BE_REMOVED + 1
	    	if row[2] == "Time":
	    		EXTRA_COLUMNS_TO_BE_REMOVED = EXTRA_COLUMNS_TO_BE_REMOVED + 1
	    	if row[0] == "Frame":
	    		EXTRA_COLUMNS_TO_BE_REMOVED = EXTRA_COLUMNS_TO_BE_REMOVED + 1
	    	if row[0] == "Time":
	    		EXTRA_COLUMNS_TO_BE_REMOVED = EXTRA_COLUMNS_TO_BE_REMOVED + 1
	    		
	    	print("EXTRA_COLUMNS_TO_BE_REMOVED:")
	    	print(EXTRA_COLUMNS_TO_BE_REMOVED)

	    if i >= 12:
	    	STOP_TIME = "{0:.4f}".format(1.00/float(FREQUENCY)*(i-12.00))
	    	VALUES = [i-11, "{0:.4f}".format(1.00/float(FREQUENCY)*(i-12.00))]
	    	for x in range(1,int(NO_OF_MARKERS)+1):
	    		#VALUES.append("{0:.3f}".format(- float(row[(x-1)*3 + EXTRA_COLUMNS_TO_BE_REMOVED]) + 370.0)) # X_opensim = -X_QTM
	    		#VALUES.append("{0:.3f}".format(float(row[(x-1)*3+2 + EXTRA_COLUMNS_TO_BE_REMOVED]) - 398.0)) # Y_opensim = Z_QTM
	    		#VALUES.append("{0:.3f}".format(float(row[(x-1)*3+1 + EXTRA_COLUMNS_TO_BE_REMOVED]) - 972.0)) # Z_opensim = Y_QTM
	    		VALUES.append("{0:.3f}".format(- float(row[(x-1)*3 + EXTRA_COLUMNS_TO_BE_REMOVED]))) # X_opensim = -X_QTM
	    		VALUES.append("{0:.3f}".format(float(row[(x-1)*3+2 + EXTRA_COLUMNS_TO_BE_REMOVED]))) # Y_opensim = Z_QTM
	    		VALUES.append("{0:.3f}".format(float(row[(x-1)*3+1 + EXTRA_COLUMNS_TO_BE_REMOVED]))) # Z_opensim = Y_QTM
	    	writer.writerow(VALUES)	
	    i = i+1


	# now generating the forces
	# generating the tsv -> trc files
	
	force_left_reader = csv.reader(left_force_infile, delimiter='\t', quotechar='"', skipinitialspace=True)
	force_right_reader = csv.reader(right_force_infile, delimiter='\t', quotechar='"', skipinitialspace=True)
	force_writer = csv.writer(forces_outfile, delimiter='\t', lineterminator='\n')
	
	i = 1
	FORCE_NO_OF_SAMPLES = 0
	FORCE_FREQUENCY = 0
	FORCE_EXTRA_COLUMNS_TO_BE_REMOVED = 0
	
	while True:
		try:
		    row = next(force_left_reader)
		    row_right = next(force_right_reader)
			
		    if i <= 10:
		    	print(row)
		    if i == 1:
		    	FORCE_NO_OF_SAMPLES = row[1]
		    if i == 2:
		    	FORCE_FREQUENCY = row[1]
		    if i == 3:
		    	NO_OF_MARKERS = row[1]
		    if i == 24:
		    	print("writing header to force output")
		    	print(row)
		    	force_writer.writerow(['Coordinates'])
		    	force_writer.writerow(['version=1'])
		    	force_writer.writerow(['nRows='+str(int(FORCE_NO_OF_SAMPLES))])
		    	force_writer.writerow(['nColumns=19'])
		    	force_writer.writerow(['inDegrees=yes'])
		    	force_writer.writerow([])
		    	force_writer.writerow(['Units are S.I. units (second, meters, Newtons, ...)'])
		    	force_writer.writerow(['Angles are in degrees.'])
		    	force_writer.writerow([])
		    	force_writer.writerow(['endheader'])
		    	
		    	force_writer.writerow(['time','1_Force_X','1_Force_Y','1_Force_Z','1_Moment_X','1_Moment_Y','1_Moment_Z','1_COP_X','1_COP_Y','1_COP_Z','2_Force_X','2_Force_Y','2_Force_Z','2_Moment_X','2_Moment_Y','2_Moment_Z','2_COP_X','2_COP_Y','2_COP_Z'])

		    	if row[0] == "SAMPLE":
		    		FORCE_EXTRA_COLUMNS_TO_BE_REMOVED = FORCE_EXTRA_COLUMNS_TO_BE_REMOVED + 1
		    	if row[1] == "SAMPLE":
		    		FORCE_EXTRA_COLUMNS_TO_BE_REMOVED = FORCE_EXTRA_COLUMNS_TO_BE_REMOVED + 1
		    	if row[0] == "TIME":
		    		FORCE_EXTRA_COLUMNS_TO_BE_REMOVED = FORCE_EXTRA_COLUMNS_TO_BE_REMOVED + 1
		    	if row[1] == "TIME":
		    		FORCE_EXTRA_COLUMNS_TO_BE_REMOVED = FORCE_EXTRA_COLUMNS_TO_BE_REMOVED + 1
	    		
	    		print("FORCE_EXTRA_COLUMNS_TO_BE_REMOVED:")
	    		print(FORCE_EXTRA_COLUMNS_TO_BE_REMOVED)
		    	
		    if i >= 25:
		    	VALUES = ["{0:.4f}".format(1.00/float(FORCE_FREQUENCY)*(i-25.00))]
		    	for x in range(1,3):
		    		VALUES.append("{0:.3f}".format(- float(row[(x-1)*3+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED])))
		    		VALUES.append("{0:.3f}".format(float(row[(x-1)*3+2+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED])))
		    		VALUES.append("{0:.3f}".format(float(row[(x-1)*3+1+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED])))
		    	
		    	#VALUES.append("{0:.3f}".format(- float(row[6+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED]) + 370.0)) # X_opensim = -X_QTM
		    	#VALUES.append("{0:.3f}".format(float(row[8+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED]) - 398.0)) # Y_opensim = Z_QTM
		    	#VALUES.append("{0:.3f}".format(float(row[7+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED]) - 972.0)) # Z_opensim = Y_QTM
		    	VALUES.append("{0:.3f}".format(- float(row[6+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED]))) # X_opensim = -X_QTM
		    	VALUES.append("{0:.3f}".format(float(row[8+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED]))) # Y_opensim = Z_QTM
		    	VALUES.append("{0:.3f}".format(float(row[7+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED]))) # Z_opensim = Y_QTM
		    	#now the other file
		    	for x in range(1,3):
		    		VALUES.append("{0:.3f}".format(- float(row_right[(x-1)*3+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED])))
		    		VALUES.append("{0:.3f}".format(float(row_right[(x-1)*3+2+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED])))
		    		VALUES.append("{0:.3f}".format(float(row_right[(x-1)*3+1+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED])))
		    	
		    	#VALUES.append("{0:.3f}".format(- float(row_right[6+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED]) + 370.0)) # X_opensim = -X_QTM
		    	#VALUES.append("{0:.3f}".format(float(row_right[8+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED]) - 398.0)) # Y_opensim = Z_QTM
		    	#VALUES.append("{0:.3f}".format(float(row_right[7+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED]) - 972.0)) # Z_opensim = Y_QTM
		    	VALUES.append("{0:.3f}".format(- float(row_right[6+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED]))) # X_opensim = -X_QTM
		    	VALUES.append("{0:.3f}".format(float(row_right[8+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED]) )) # Y_opensim = Z_QTM
		    	VALUES.append("{0:.3f}".format(float(row_right[7+FORCE_EXTRA_COLUMNS_TO_BE_REMOVED]))) # Z_opensim = Y_QTM
		    	force_writer.writerow(VALUES)
		    i = i+1
		except StopIteration:
		    break

	template = scale_config_template_file.read()
	content = template.replace("<mass></mass>","<mass>"+WEIGHT+"</mass>").replace("<marker_file></marker_file>", "<marker_file>"+experiment+'.trc'+"</marker_file>")
	scale_config_file.write(content)
	
	template = ik_config_template_file.read()
	content = template.replace("<marker_file></marker_file>", "<marker_file>"+experiment+'.trc'+"</marker_file>").replace("<output_motion_file></output_motion_file>", "<output_motion_file>"+experiment+'.mot'+"</output_motion_file>").replace("STOP_TIME", STOP_TIME)
	ik_config_file.write(content)
	
	template =id_config_template_file.read()
	content = template.replace("<coordinates_file></coordinates_file>","<coordinates_file>"+experiment+'.mot'+"</coordinates_file>").replace("<output_gen_force_file></output_gen_force_file>","<output_gen_force_file>"+experiment+'_inverse_dynamics.sto'+"</output_gen_force_file>").replace("<output_body_forces_file></output_body_forces_file>","<output_body_forces_file>"+experiment+'_body_forces_at_joints.sto'+"</output_body_forces_file>").replace("STOP_TIME", STOP_TIME)
	id_config_file.write(content)

	template =external_forces_template_file.read()
	content = template.replace("<datafile></datafile>","<datafile>"+experiment+'_ext_forces.mot'+"</datafile>")
	external_forces_file.write(content)
		
	template =analyze_config_template_file.read()
	content = template.replace("<coordinates_file></coordinates_file>","<coordinates_file>"+experiment+'.mot'+"</coordinates_file>").replace("STOP_TIME", STOP_TIME)
	analyze_config_file.write(content)

print(" ")
print("complete preprocessing.")


with open(batch_target, 'w') as batch_file:
	batch_file.write("cd data\\"+athlete+"\n")
	batch_file.write("scale -S 1_scale_config.xml\n")
	batch_file.write("ik -S 2_ik_config.xml\n")
	batch_file.write("id -S 3_id_config.xml\n")
	batch_file.write("analyze -S 4_analyze_config.xml\n")
	batch_file.write("cd ..\n")
	batch_file.write("cd ..\n")
	batch_file.write("pause\n")
	
print("executing batchfile")
os.startfile(batch_target)
#os.system("cmd /k " + batch_target)
