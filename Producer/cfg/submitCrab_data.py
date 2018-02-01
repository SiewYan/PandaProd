from CRABClient.UserUtilities import config, getUsernameFromSiteDB
from subprocess import call, check_output

import sys, os
from re import findall

### CHECK THAT CMS env and it is correct
pwd = os.environ['PWD']
if 'CMSSW_VERSION' not in os.environ:
		print "Do cmsenv!"
		exit(0)
version = os.environ['CMSSW_VERSION']
ok = False
for dir in reversed(pwd.split('/')):
		if version == dir : 
				ok = True
				break
if not ok:
		print "Do (redo) cmsenv (2) !"
		exit(0)


config = config()

config.General.requestName = 'PandaProd_request_XXX'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = False

## JobType
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'prod.py'
config.JobType.pyCfgParams=['config=Prompt2017']
config.JobType.outputFiles = ['panda.root']

### DATA configuration
#config.Data.inputDataset = '/HplusToTauNu-M500/amarini-amarini_PrivateMC_HPlusToTauNu_June2015-16aa19d591b8b49c55c4508e7a7c9233/USER'
config.Data.inputDBS = 'global'
#config.Data.ignoreLocality = True

config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 10
config.Data.totalUnits = -1

config.Site.storageSite = 'T3_US_FNALLPC' 
#config.Data.outLFNDirBase = '/store/user/shoh/pandaprod/80X' #Please change USER to yours
config.Data.outLFNDirBase = '/store/group/lpcmetx/pandaprod/92X_test'
config.Data.publication = False
config.Data.outputDatasetTag ='PandA'

config.Site.whitelist = ['T3_US_FNALLPC']
config.Site.ignoreGlobalBlacklist = True

if __name__ == '__main__':

	from CRABAPI.RawCommand import crabCommand
	from CRABClient.ClientExceptions import ClientException
	from httplib import HTTPException

	# We want to put all the CRAB project directories from the tasks we submit here into one common directory.
	# That's why we need to set this parameter (here or above in the configuration file, it does not matter, we will not overwrite it).
	config.General.workArea = 'Submission'

	def submit(config):
		### for some reason only the first dataset is submitted correctly, work around
		if len(sys.argv) ==1:
			## book the command and run python
			cmd = "python " + sys.argv[0] + " '" + config.General.requestName + "'"
			print "calling: "+cmd
			call(cmd,shell=True)
			return
		if len(sys.argv) > 1:
			## if it is not in the request try the next
			if sys.argv[1] !=	config.General.requestName: return
			###
			#if split[1] == "uscms_data":
			print "--- Submitting " + "\033[01;32m" + config.General.requestName + "\033[00m"   + " ---"
			#else:
			#	print "--- Submitting " + "\033[01;32m" + config.Data.inputDataset.split('/')[1] + "\033[00m"	+ " ---"
			
			config.Data.outputDatasetTag = config.General.requestName
			try:
				crabCommand('submit', config = config)
			except HTTPException as hte:
				print "Failed submitting task: %s" % (hte.headers)
			except ClientException as cle:
				print "Failed submitting task: %s" % (cle)

	def setdata(value="True"):
		if value=='True':
			config.Data.splitting = 'LumiBased'
			#config.Data.lumiMask=None
			url = "https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/ReReco/Final/"
			config.Data.lumiMask = url + "Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt"
		else:
			config.Data.lumiMask = None
			config.Data.splitting = 'FileBased'

		for idx,par in enumerate(config.JobType.pyCfgParams):
			if "isData" in par:
				config.JobType.pyCfgParams[idx] = "isData=" + value
				return 

	def setsignal(value):
		for idx,par in enumerate(config.JobType.pyCfgParams):
			if "isSignal" in par:
				config.JobType.pyCfgParams[idx] = "isSignal=" + value
				return 

			
	def submitList(l):
		for ll in l: # looooping on submitlist filelist
			print "Reading filelist : ", ll
			inputfile= file(ll,'r')
			for line in inputfile:
				split = line.split('/')
				config.Data.inputDataset = line #/SingleMuon/Run2017H-PromptReco-v1/MINIAOD
				config.General.requestName = split[1]+'_'+split[2] #SingleMuon_Run2017H-PromptReco-v1
#				submit(config)
				print "config.Data.inputDataset = %s" %(config.Data.inputDataset)
				print "config.General.requestName = %s" %(config.General.requestName)
				print "SUBMIT!!"
			print "Finish reading filelists"

	'''
		for ll in l:
			split = ll.split('/')
			if split[1] == "uscms_data":
				config.Data.userInputFiles = open(ll).readlines()
				config.Data.outputPrimaryDataset = split[-1].split('.')[0]
			else:
				config.Data.inputDataset = ll
			if split[-1]=='MINIAOD':
				config.General.requestName = split[1]+'_'+split[2]
			elif 'ext' in split[-2]:
				ext = findall('ext[0-9]+',split[-2])
				if len(ext)>0:
					config.General.requestName = split[1] + '_' + ext[0]
				else:
					config.General.requestName = split[1]
			else:
				#private file
				config.General.requestName = split[-1].split('.')[0]
			submit(config)
			'''
	#############################################################################################
	## From now on that's what users should modify: this is the a-la-CRAB2 configuration part. ##
	#############################################################################################
	###################################################
	setdata("False")
	###################################################
	
	#config.Data.splitting = 'EventAwareLumiBased'
	config.Data.unitsPerJob = 50
	# /uscms_data/d1/shoh/filelists/DarkHiggs/BBbarDM_LO_MZprime_test.txt
	submitList([
			'/uscms_data/d3/naina25/Panda_2018/Panda_Prod/CMSSW_9_2_6/src/PandaProd/Producer/cfg/file_lists2017/data/SingleMuon.txt'
			])

