import plistlib
import os
from pathlib import Path

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_icloudSharedalbums(files_found, report_folder, seeker, wrap_text, timezone_offset):
	data_list_sharedemails = []
	data_list_sharedpersoninfos = []
	data_list_sharedinfos = []
	data_list_cloudinfo = []
	
	for file_found in files_found:
		file_found = str(file_found)
		pathedhead, pathedtail = os.path.split(file_found)
		
		if os.path.isfile(file_found):
			if pathedtail == 'cloudSharedEmails.plist':
				with open(file_found, "rb") as fp:        
					pl = plistlib.load(fp)
					for x, y in pl.items():
						data_list_sharedemails.append((x, y))

			elif pathedtail == 'cloudSharedPersonInfos.plist':
				with open(file_found, "rb") as fp:        
					pl = plistlib.load(fp)
					for x, y in pl.items():
						
						email = ''
						firstname = ''
						lastname = ''
						fullname = ''

						for a, b in y.items():	
							if a == 'email':
								email = b
							if a == 'firstName':
								firstname = b
							if a == 'fullName':
								fullname = b
							if a == 'emails':
								email = b[0]
							if a == 'lastName':
								lastname = b
						
						file_found_persons = file_found
						data_list_sharedpersoninfos.append((email, firstname, lastname, fullname, x))	
		
			elif pathedtail == 'Info.plist':
				albumid = (os.path.basename(os.path.dirname(file_found)))
				albumpath = file_found
				#print(f'Info.plist album ID: {albumid}')
				
				cloudOwnerEmail = ''
				
				with open(file_found, "rb") as fp:        
					pl = plistlib.load(fp)
					
					cloudOwnerEmail = ''
					cloudownerfirstname = ''
					cloudownerlastname  = ''
					cloudpublicurlenabled  = ''
					cloudsubscriptiondate = ''
					cloudrelationshipstate  = ''
					cloudownerhashedpersonid = ''
					clowdoenweremail = ''
					title = ''
					
					for x, y in pl.items():
						#print(f'{x}: {y}')
						if x == 'cloudOwnerEmail':
							clowdoenweremail = y
						if x == 'cloudOwnerFirstName':
							cloudownerfirstname = y
						if x == 'cloudOwnerLastName':
							cloudownerlastname = y
						if x == 'cloudPublicURLEnabled':
							cloudpublicurlenabled = y
						if x == 'cloudSubscriptionDate':
							cloudsubscriptiondate = y
						if x == 'cloudRelationshipState':
							cloudrelationshipstate = y
						if x == 'title':
							albumtitle = y	
						if x == 'cloudOwnerHashedPersonID':
							cloudownerhashedpersonid = y
						
				data_list_sharedinfos.append((albumtitle, albumid, clowdoenweremail, cloudownerfirstname, cloudownerlastname, cloudpublicurlenabled, cloudsubscriptiondate, cloudrelationshipstate, cloudownerhashedpersonid, albumpath))

			elif pathedtail == 'DCIM_CLOUD.plist':
				albumid = (os.path.basename(os.path.dirname(file_found)))
				albumpath = file_found
				#print(f'Info.plist album ID: {albumid}')
				with open(file_found, "rb") as fp:        
					pl = plistlib.load(fp)
					for x, y in pl.items():
						if x == 'DCIMLastDirectoryNumber':
							dcimlastdictnum = y
						if x == 'DCIMLastFileNumber':
							dcimlastfilenum = y
					data_list_cloudinfo.append((albumid, dcimlastdictnum, dcimlastfilenum, albumpath))
				
		else:
			pass
			
	if len(data_list_sharedinfos) > 0:
		location = 'See report entry'
		report = ArtifactHtmlReport('iCloud Shared Owner Info')
		report.start_artifact_report(report_folder, 'iCloud Shared Owner Info')
		report.add_script()
		data_headers = ('Album Title','Album ID','Clowd Owner Email','Cloud Owner First Name','Clowd Owner Lastname','Cloud Public URL Enabled?','Cloud Subscription Date','Cloud Relationship State','Cloud Ownewr Hashed Person ID', 'File location' )     
		report.write_artifact_data_table(data_headers, data_list_sharedinfos, location)
		report.end_artifact_report()
		
		tsvname = 'iCloud Shared Owner Info'
		tsv(report_folder, data_headers, data_list_sharedinfos, tsvname)
	else:
		logfunc('No iCloud Shared Owner Info')
		
	if len(data_list_cloudinfo) > 0:
		location = 'See report entry'
		report = ArtifactHtmlReport('iCloud Shared Album data')
		report.start_artifact_report(report_folder, 'iCloud Shared Album Data')
		report.add_script()
		data_headers = ('Album Name', 'DCIM Last Directory Number','DCIM LAst File Number', 'File location' )     
		report.write_artifact_data_table(data_headers, data_list_cloudinfo, location)
		report.end_artifact_report()
		
		tsvname = 'iCloud Shared Album Data'
		tsv(report_folder, data_headers, data_list_cloudinfo, tsvname)
	else:
		logfunc('No iCloud Shared Album Data')

	if len(data_list_sharedpersoninfos) > 0:
		location = file_found_persons
		report = ArtifactHtmlReport('iCloud Shared Album Persons Info')
		report.start_artifact_report(report_folder, 'iCloud Shared Person Info')
		report.add_script()
		data_headers = ('Email', 'Firstname','Lastname', 'Fullname', 'Identification' )     
		report.write_artifact_data_table(data_headers, data_list_sharedpersoninfos, location)
		report.end_artifact_report()
		
		tsvname = 'iCloud Shared Person Info'
		tsv(report_folder, data_headers, data_list_sharedpersoninfos, tsvname)
	else:
		logfunc('No iCloud Shared Album Persons Info')
		
	if len(data_list_sharedemails) > 0:
		location = file_found
		report = ArtifactHtmlReport('iCloud Shared Albums Emails')
		report.start_artifact_report(report_folder, 'iCloud Shared Emails')
		report.add_script()
		data_headers = ('Key', 'Value' )     
		report.write_artifact_data_table(data_headers, data_list_sharedemails, location)
		report.end_artifact_report()
		
		tsvname = 'iCloud Shared Albums Emails'
		tsv(report_folder, data_headers, data_list_sharedemails, tsvname)
	else:
		logfunc('No iCloud Shared Emails')
	
__artifacts__ = {
    "icloudSharedalbums": (
        "iCloud Shared Albums",
        ('*/mobile/Media/PhotoData/PhotoCloudSharingData/*'),
        get_icloudSharedalbums)
}