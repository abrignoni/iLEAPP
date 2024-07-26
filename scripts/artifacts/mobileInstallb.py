import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def month_converter(month):
  months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ]
  month = months.index(month) + 1
  if month < 10:
    month = f"{month:02d}"
  return month

def day_converter(day):
  day = int(day)
  if day < 10:
    day = f"{day:02d}"
  return day

def line_splitting(line):
  splitline = line.split(' ',6)
  notice = splitline.pop(6)
  weekday, month, space, day, time, year = splitline
  if space == '':
    pass
  else:
    splitline = line.split(' ',5)
    notice = splitline.pop(5)
    weekday, month, day, time, year = splitline
  if 'Reboot detected' in notice:
    notice = notice.split('main: ')[1]
  else:
    notice = notice.split(':]: ')[1] 
  day = day_converter(day)
  month = month_converter(month)
  timestamp = (str(year) + "-" + str(month) + "-" + str(day) + " " + str(time))
  return((timestamp,notice))


def get_mobileInstallb(files_found, report_folder, seeker, wrap_text, timezone_offset):
    iosversion = scripts.artifacts.artGlobals.versionf
    if (version.parse(iosversion) >= version.parse("17")):
      data_list = []
      data_list_reboot = []
      for file_found in files_found:
        filename = os.path.basename(file_found)
        
        with open(file_found, 'r') as f:
          data = f.readlines()
        
        for line in data:
          if 'Attempting Delta patch update' in line:
            desc = 'Update'
            values = line_splitting(line)
            data_list.append((values[0],desc,values[1],filename))
          elif 'Installing <MIInstallableBundle' in line:
            desc = 'Install'
            values = line_splitting(line)
            data_list.append((values[0],desc,values[1],filename))
          elif 'Data container for' in line:
            desc = 'Container'
            values = line_splitting(line)
            data_list.append((values[0],desc,values[1],filename))
          elif 'Made container live for' in line:
            desc = 'Container Live'
            values = line_splitting(line)
            data_list.append((values[0],desc,values[1],filename))
          elif 'Reboot detected' in line: #anadir un data_list_reboot para esta data
            desc = 'Reboot'
            values = line_splitting(line)
            data_list_reboot.append((values[0],desc,values[1],filename))
            data_list.append((values[0],desc,values[1],filename))
          elif 'Install Successful for' in line: 
            desc = 'Install Successful'
            values = line_splitting(line)
            data_list.append((values[0],desc,values[1],filename))
          elif 'Running installation as' in line: 
            desc = 'Running Installation'
            values = line_splitting(line)
            data_list.append((values[0],desc,values[1],filename))
          elif 'Attempting Parallel patch update' in line: 
            desc = 'Parallel Update'
            values = line_splitting(line)
            data_list.append((values[0],desc,values[1],filename))
          elif 'Uninstalling identifier' in line: 
            desc = 'Uninstalling'
            values = line_splitting(line)
            data_list.append((values[0],desc,values[1],filename))
          elif 'Destroying container' in line: 
            desc = 'Destroying'
            values = line_splitting(line)
            data_list.append((values[0],desc,values[1],filename))
          else:
            pass
      
      if len(data_list) > 0:
        description = 'Mobile Installation Logs. All timestamps are in Local Time'
        report = ArtifactHtmlReport(f'Mobile Installation Logs History')
        report.start_artifact_report(report_folder, f'Mobile Installation Logs History', description)
        report.add_script()
        data_headers = ('Timestamp','Type','Notice','Source File')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=[''])
        report.end_artifact_report()
        
        tsvname = f'Mobile Installation Logs History'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Mobile Installation Logs History'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
      else:
        logfunc(f'No Mobile Installation Logs History')
        
      
      if len(data_list_reboot) > 0:
        description = 'Reboots - Mobile Installation Logs. All timestamps are in Local Time'
        report = ArtifactHtmlReport(f'Reboots - Mobile Installation Logs')
        report.start_artifact_report(report_folder, f'Reboots - Mobile Installation Logs', description)
        report.add_script()
        data_headers = ('Timestamp','Type','Notice','Source File')
        report.write_artifact_data_table(data_headers, data_list_reboot, file_found, html_no_escape=[''])
        report.end_artifact_report()
        
        tsvname = f'Reboots - Mobile Installation Logs History'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Reboots - Mobile Installation Logs History'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
      else:
        logfunc(f'No Reboots - Mobile Installation Logs')
    
__artifacts__ = {
    "mobileInstallb": (
        "Mobile Installation Logs",
        ('*/mobile_installation.log.*'),
        get_mobileInstallb)
}
