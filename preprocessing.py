import os,csv
from os.path import join
import axmlparserpy.apk as apk

import numpy as np
from sklearn.externals import joblib

extractedDir = os.getcwd() + "/pulled-apks/"
print extractedDir

#selectedfiles = [u'ringtoneBR.apk', u'DefaultContainerService.apk', u'SecFactoryPhoneTest.apk', u'FmmDS.apk', u'SecContacts_ENTRY.apk', u'SecGallery_ESS.apk', u'FotaClient.apk', u'FmmDM.apk']

OUTPUT = "permissions.csv"

apkscore = list()


# input: directory with apks and selected apk name
# output: permissions.csv that will all extracted permissions and if unscessfull a log file will be created

def extractPermissions(extractedDir, selectedApks):
	# open csv file
	resultFile = open(OUTPUT,'wb')
	error = open("permission_extraction_log.txt",'wb')
	wr = csv.writer(resultFile, delimiter=',')
	#os.chdir("pulled-apks")
	for filename in selectedApks:
    		#reading and parsing apk file
          # print (join(extractedDir, filename))

    		try:
               #print extractedDir, filename
        		ap = apk.APK(join(extractedDir, filename))
			package = ap.get_package().encode("utf-8")
			androidversion_name = ap.get_androidversion_name().encode("utf-8")
    		except:
			error.write(filename)
			error.write('\n')
    		else:
        		permissions= ap.get_permissions()
			PCount = len(permissions)
        		wr.writerow(permissions +  [filename,package,androidversion_name,PCount])

	resultFile.close()
	error.close()

def get_permission(fullpermission):
    return fullpermission.split('.')[-1]

def createFeatureSet(selectedApks):
     #print selectedApks
	extractPermissions(extractedDir,selectedApks)
	fscore= open("score.csv", "rb")
	features=list()
	benign_fscore={}
	malware_fscore={}
	effective_fscore={}

	score_reader = csv.reader(fscore)

	#Skipping the header
	next(score_reader)


	for row in score_reader:
		features.append(row[0])
		benign_fscore[row[0]]=row[3]
		malware_fscore[row[0]]=row[4]
		effective_fscore[row[0]]=row[5]

	fscore.close()

	f = open("featureset.csv", "wb")
	writer = csv.writer(f, delimiter=',')
	writer.writerow(features + ["total"])
	fp =  open("permissions.csv", "rb")
	reader = csv.reader(fp)
	next(reader)

	for row in reader:
		apk_feature=list()
		apk_permission = [ get_permission(p) for p in row[0:-4]]
		#print apk_permission
		for feature in features:
			if feature in apk_permission:
				#apk_feature.append(float(benign_fscore[feature]))
				apk_feature.append(float(effective_fscore[feature]))
			else:
				apk_feature.append(0)
		result = apk_feature +[sum(apk_feature)]
		tmp = (row[-4],row[-3],row[-2],row[-1],str(sum(apk_feature)))
		apkscore.append(tmp)
		#print result
		writer.writerow(result)
	#print apkscore
	fp.close()
	f.close()


def assignClassLabel(selectedApks):
    print "I am in preprocessing"
    print selectedApks
    result = list()
    createFeatureSet(selectedApks)
    forest = joblib.load('./classifiers/RFClassifier.pkl')
    # reading in test data into a NumPy array
    test_data = np.loadtxt(open("featureset.csv", "r"), delimiter=",", skiprows=1, dtype=np.float64)
    # Checking class label for test data
    pred_test_RF = forest.predict(test_data)
    classes = {2: "Benign", 3: "Suspicious"}
    # report = zip(selectedApks,pred_test_RF)
    # print len(report)
    # print len(apkscore)
    # print report
    for index, meta in enumerate(apkscore):
        result.append((meta + (classes[pred_test_RF[index]],)))
    # Cleaning : Deleting all the temp files
    os.remove("permissions.csv")
    os.remove("featureset.csv")
    if os.path.getsize("permission_extraction_log.txt") == 0:
        os.remove("permission_extraction_log.txt")
    return result

# extractPermissions(extractedDir,selectedfiles)
# createFeatureSet()
# print assignClassLabel(selectedfiles)