# -*- coding:utf-8 -*-
"""iCalendar (RFC5545, RFC2445) parser/validator/generator/events enumerator :  Parse, Generate and enumerate events (support of RRULE, EXRULE, RDATE, EXDATE)

About
-----

This module is an iCalendar parser for iCalendar file (ical or ics) defined by rfc5545 
(http://tools.ietf.org/html/rfc5545), which obsoleted rfc2445 
(http://www.ietf.org/rfc/rfc2445.txt), which had previously replaced vcal 1.0
(http://www.imc.org/pdi/vcal-10.txt).

The iCalendar file, once parsed, will be available as a typed structure. 
Events dates can be computed (including rrule, rdate exrule and exdates). 

iCalendar module and dateutils both provide some of the functionalities of this module but
do not provide it in an integrated way.

Usage
-----
* Enumerator of iCalendar file:

    mycal = icalendar.ics()
    mycal.local_load(icsfile)
    mycal.parse_loaded()
    dates = mycal.get_event_instances(start,end)
    #dates will contain the json with all explicit dates of the events spec'ed by the iCalendar file

* Validator:
    mycal = icalendar.ics()\n
    mycal.local_load(icalendarfile.ics)\n
    #icalendarfile.ics is the local path\n
    mycal.parse_loaded(conformance=True)\n
    #When conformance is True it displays on console critical & non critical error from icalendar file\n

To come
-------
* 0.6.1y: add support for no dtstart and/or not dtend + add support for RDATE after UNTIL
* 0.6.1z: add unittest support
* 0.6.2a: add code for event_instances (including support for overlapping), event.instances.isbounded, event.instances.walk,
    add code for multiple rrule, exrule, add code for event_instances['day']
* 0.6.2b: add code for property parameters, property values, delimiters (linear, wlsp), ENCODING, character sets, language, binary values,XAPIA’s CSA RRULE,
    x-components and x-properties parsing + for x-properties adding the type of data
* 0.6.2c: add code for x-components and x-properties generation
* 0.6.2d: add loader and generator for todo, alarm
* 0.7.x: add datetime and tzinfo 
* 0.8.x: add support for non-standard compliance: no tzoneinfo, escaped characters, ...
* Extend support to new x-properties for iCalendar like events related to religious dates or celestial events

Next:
-----
* add CUA capability + CalDAV support

History
-------
Created on Aug 4, 2011

@author: oberron
@change: to 0.4 - passes all unit test in ical_test v0.1
@change: 0.4 to 0.5 adds EXDATE support
@change: 0.5 to 0.6 adds support for no DTEND and DTEND computation from DURATION or DTSTART
@version: 0.6.x
"""

import datetime 
from icalendar_SCM import RFC5545_SCM, ESCAPEDCHAR,RFC5545_Properties

CRLF= "\r\n"

class vevent:
    
    """ Parses a vevent (object from vcalendar as defined by the iCalendar standard (RFC5545)
    """
#    vevent_load = { "uid": self.string_load}
    def _icalindex_to_pythonindex(self,indexes):
        ret_val = []
        for index in indexes:
            index = int(index)
            if index > 0:
                #ical sees the first as a 1 whereas python sees the 0 as the first index for positives
                index = index -0
            ret_val.append(index)
        return ret_val
    def line_wrap(self,newline):
        if len(newline)<75:
            ret_val = newline
        else:
            #FIXME: about the utf-8 and mid-octet splitting
            NnewLine = int(len(newline)/73.0)
            ret_val = newline[0:74]+CRLF
            for i in range(1,NnewLine):
                ret_val+=" "+newline[i*73+1:(i+1)*73+1]+CRLF
            ret_val+=" "+newline[(NnewLine)*73+1:]
            
        return ret_val

    def string_write(self,string):
        for esc in ESCAPEDCHAR:
            string = string.replace(ESCAPEDCHAR[esc],esc)
        return string
    def string_load(self,propval,param="",LineNumber = 0):
        #TODO add here escaped characters
        ret_val = propval
        for esc in ESCAPEDCHAR:
            ret_val= ret_val.replace(esc,ESCAPEDCHAR[esc])

        return ret_val
    def date_write(self,date2w,param=""):
        """ takes date or datetime and returns icalendar date or datetime"""
        dt = datetime.datetime(year=2013,month=1,day=26)
        
        if type(dt)==type(date2w):
            datestring = self.string_write(date2w.strftime("%Y%m%dT%H%M%S").upper())
        else :
            datestring = self.string_write(date2w.strftime("%Y%m%d").upper())
        return datestring
    def date_load(self,propval,param="",LineNumber = 0):
        """ loads the date-time or date value + optional TZID into UTC date-time or date"""
        
        #DTSTART, DTEND, DTSTAMP, UNTIL,
        self.mycal4log = ics()
        #TODO: handle params properly http://www.kanzaki.com/docs/ical/dtstart.html

        retdate=datetime.datetime(1970,1,1) #FIXME: this is temporary 
        yeardate = int(propval[0:4])
        
        if yeardate<1970:
            self.mycal4log.Validator("3.3.5_1", line_count = LineNumber,line = propval,alttxt="1970 however is often a computer epoch limit prior validation should be undertaken before keeping such a past date", show = True)
        elif yeardate<1875:
            self.mycal4log.Validator("3.3.5_1", line_count = LineNumber,line = propval,show= True)
        elif yeardate<1582: #retdate<datetime.datetime(year=1582,month=10,day=15):
            self.mycal4log.Validator("3.3.5_1", line_count = LineNumber,line = propval,alttext = "dates prior to 1582/oct/15 might be in julian calendar, prior validation should be undertaken", show = True,prio=1)
        else:
            if len(propval)>8:
                retdate = datetime.datetime.strptime(propval[:8],"%Y%m%d")
            else:
                retdate = datetime.datetime.strptime(propval,"%Y%m%d")
        
        return retdate
    def duration_write(self,duration):
        return duration
    def duration_load(self,duration,param="",conformance=False,LineNumber = 0):
        self.mycal4log = ics()
        #FIXME: check that datetime.timdelta supports timeoffsets
        """
        FIXME: get below addressed and fixed when adding datetime
        The duration of a week or a day depends on its position in the
      calendar.  In the case of discontinuities in the time scale, such
      as the change from standard time to daylight time and back, the
      computation of the exact duration requires the subtraction or
      addition of the change of duration of the discontinuity.  Leap
      seconds MUST NOT be considered when computing an exact duration.
      When computing an exact duration, the greatest order time
      components MUST be added first, that is, the number of days MUST
      be added first, followed by the number of hours, number of
      minutes, and number of seconds.
        """
#        print "line 79",duration
        if duration[0]=="P":
            duration = duration[1:]
        tdelta = datetime.timedelta()
        years =0
        months =0
        sign =1
        if duration[0:1]=="-":
            duration = duration[1:]
            sign = -1
#            print "sign",sign
        if duration.find("T")>=0:
            [date,time]=duration.split("T")
#            print "line 89, date time", date,time
#            date = date[1:]
        else:
            [date , time] = [duration,""]
        pos = date.find("W")
        if pos>0:
            tdelta += datetime.timedelta(weeks= sign*int(date[:pos]))
        pos = date.find("Y")
        if (pos)>0:
            years = sign*int(date[:pos])
            date = date[pos+1:]
            if conformance: 
                self.mycal4log.Validator("3.3.6_1",level=1) #raise Exception("VEVENT VALIDATOR","encountered a Y parameter in a DURATION field which is prohibited by RFC5545")
            else:
                self.mycal4log.Validator("3.3.6_1",level=0)
        pos = date.find("M")
        if pos>0:
            months = sign*int(date[:pos])
            date = date[pos+1:]
#            if conformance: raise Exception("VEVENT VALIDATOR","encountered a M parameter in a DURATION field which is prohibited by RFC5545")
            if conformance: 
                self.mycal4log.Validator("3.3.6_1",level=1)
            else:
                self.mycal4log.Validator("3.3.6_1",level=0)

        pos = date.find("D")
        if (pos)>0:
            tdelta += datetime.timedelta(days = sign*int(date[:pos]))
        pos = time.find("H")
        if (pos)>0:
            tdelta += datetime.timedelta(hours = sign*int(time[:pos]))
            time = time[pos+1:]
        pos = time.find("M")
        if (pos)>0:
            tdelta += datetime.timedelta(minutes = sign*int(time[:pos]))
#            print "line 129 tdelta minute",tdelta
            time = time[pos+1:]
        pos = time.find("S")
        if (pos)>0:
            tdelta += datetime.timedelta(seconds = sign*int(time[:pos]))
        return [years,months,tdelta]
    
    def datelist_write(self,dtlist):
        return  dtlist
    def datelist_load(self,sDatelist,param="",LineNumber = 0):
#        if sDatelist.find(",")>=0:
        sDatelist=sDatelist.split(",")
        lDatelist = []
        for value in sDatelist:
            lDatelist.append(self.date_load(value,LineNumber = LineNumber))
#        else:
#            raise Exception("ICALENDAR WARNING", RFC5545_SCM["3.1.1_1"] + "\nline information: %s - %s"%("NA",sDatelist))
        return lDatelist
        
    def rrule_load(self,sRrule,param="",LineNumber = 0):
        #FIXME: add logs
        rules = {}
#        self._log("rrule is:",[line])
        rrule = sRrule.split(";")
        for rule in rrule:
#            self._log("120 rule out rules is:",[rule])
            if len(rule)>0:
                #FIXME: this is to cater for line ending with ; which is probably not valid
                [param, value] = rule.split("=")
                if (param == "FREQ"):
                    rules[param] = value
                elif (param == "UNTIL"):
                    rules[param] = self.date_load(value)
                    #TODO: check if that no "COUNT" is defined
                elif (param == "COUNT"):
                    rules[param] = int(value)
                    #TODO: check if that no "UNTIL" is defined
                elif (param == "INTERVAL"):
                    #( ";" "INTERVAL" "=" 1*DIGIT )          /
                    rules[param] = int(value)
                elif (param == "BYSECOND"):
                    #( ";" "BYSECOND" "=" byseclist )        /
                    #byseclist  = seconds / ( seconds *("," seconds) )
                    #seconds    = 1DIGIT / 2DIGIT       ;0 to 59
                    byseclist = value.split(",")
                    rules[param]=[]
                    for seconds in byseclist:
                        rules[param].append(int(seconds))
                elif (param == "BYMINUTE"):
                    rules[param] = value
                elif (param == "BYHOUR"):
                    rules[param] = value
                elif (param == "BYDAY"):
                    #( ";" "BYDAY" "=" bywdaylist )          /
                    #bywdaylist = weekdaynum / ( weekdaynum *("," weekdaynum) )
                    #weekdaynum = [([plus] ordwk / minus ordwk)] weekday
                    #plus       = "+"
                    #  minus      = "-"
                    #  ordwk      = 1DIGIT / 2DIGIT       ;1 to 53
                    #  weekday    = "SU" / "MO" / "TU" / "WE" / "TH" / "FR" / "SA"
                    #;Corresponding to SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY,
                    #;FRIDAY, SATURDAY and SUNDAY days of the week.
                    #bywdaylist = split(value,",")
                    #for weekdaynum in bywdaylist:
                    rules[param] = {}
                    ldow = {}   #dictionnary with dow and list of index
                    #{'MO': [0], 'TU': [1], 'WE': [-1]} means every monday, first tuesday
                    # last wednesday, .. 
                    bywdaylist = value.split(",")
                    dow = ["MO","TU","WE","TH","FR","SA","SU"]
                    for weekdaynum in bywdaylist:
                        #get the position of the DOW
                        #weekdaynum of type: MO , 1MO, 2TU or -2WE
                        for d in dow:
                            if weekdaynum.find(d) >=0:
                                pos_dow = weekdaynum.find(d)
                        #extract position of dow to split its index from it.
                        if pos_dow == 0:
                            index = 0
                        else:
                            index = int(weekdaynum[0:pos_dow])
                        ddow = weekdaynum[pos_dow:]
                        if ddow in ldow:
                            ldow[ddow].append(index)
#                                    print "238"
                        else:
#                                    print "240", ldow, ddow, index
                            ldow[ddow] = [index]
#                                print "ldow is now:",ldow
                    rules[param] = ldow
#                    self._log("175",[rules[param],param])
                elif (param == "BYMONTHDAY"):
                    # ( ";" "BYMONTHDAY" "=" bymodaylist )    /
                    # bymodaylist = monthdaynum / ( monthdaynum *("," monthdaynum) )
                    # monthdaynum = ([plus] ordmoday) / (minus ordmoday)
                    # ordmoday   = 1DIGIT / 2DIGIT       ;1 to 31
                    bymodaylist = value.split(",")
                    rules[param] = self._icalindex_to_pythonindex(bymodaylist)
                elif (param == "BYYEARDAY"):
                    byyeardaylist = value.split(",")
                    rules[param] = self._icalindex_to_pythonindex(byyeardaylist)
                elif (param == "BYWEEKNO"):
                    bywklist = value.split(",")
                    rules[param] = self._icalindex_to_pythonindex(bywklist)
                elif (param == "BYMONTH"):
                    #";" "BYMONTH" "=" bymolist )
                    #bymolist   = monthnum / ( monthnum *("," monthnum) )
                    #monthnum   = 1DIGIT / 2DIGIT       ;1 to 12
                    bymolist = value.split(",")
                    rules[param] = self._icalindex_to_pythonindex(bymolist)
                elif (param == "BYSETPOS"):
                    #( ";" "BYSETPOS" "=" bysplist )         /
                    # bysplist   = setposday / ( setposday *("," setposday) )
                    # setposday  = yeardaynum
                    bysplist = value.split(",")
                    rules[param] = self._icalindex_to_pythonindex(bysplist)
                elif (param == "WKST"):
                    rules[param] = value
                else:
                    rules[param] = value
        return rules
    def rrule_write(self,sRRULE):
        return sRRULE
    def validate_event(self,event):
#        self._log("193 validate_event", event, 0)
#        print "line 71",event
        self.mycal4log = ics()
        addsummary = ""
        adduid = ""
        if "SUMMARY" in event:
            addsummary = " event summary:"+event["SUMMARY"]["val"]
        if "UID" not in event:
            print event["UID"]
            self.mycal4log.Validator("3.6.1_3",alttxt = addsummary) #raise Exception("VEVENT VALIDATOR","mandatory property UID not set"+addsummary)
        else:
            adduid = " event UID:"+event["UID"]["val"]
#        if "DTSTART" not in event:
#            #FIXME no DTSTART is valid, but should raise a warning
#            raise Exception("VEVENT VALIDATOR","mandatory property DTSTART not set"+adduid+addsummary)            
        if "DTEND" in event:
            if "DURATION" in event:
                self.mycal4log.Validator("3.6.1_4",alttxt = adduid+addsummary)
            if event["DTSTART"] > event["DTEND"]:
                self.mycal4log.Validator("3.8.2.2_1",level=1,alttxt=adduid+addsummary)#raise Exception("VEVENT VALIDATOR","DTSTART > DTEND"+adduid+addsummary)

class ics:
    
    """ iCalendar (RFC5545, RFC2445) parser/validator/generator/events enumerator 
    
    Parse, Generate and enumerate events (support of RRULE, EXRULE, RDATE, EXDATE) usage:

    Enumerator:
        mycal = icalendar.ics()\n
        mycal.local_load(icalendarfile.ics)\n
        #icalendarfile.ics is the local path\n
        dates = mycal.get_event_instances(sDate,eDate)\n
        #start end end are strings in yyyymmdd format\n
        #dates will contain the json with all explicit dates of the events spec'ed by the iCalendar file\n

    Validator:
        mycal = icalendar.ics()\n
        mycal.local_load(icalendarfile.ics)\n
        #icalendarfile.ics is the local path\n
        mycal.parse_loaded(conformance=True)\n
        #When conformance is True it displays on console non critical error from icalendar file\n


    """
    version = "0.6.1x9"
    MaxInteger = 2147483647
    _weekday_map = {"MO":0,"TU":1,"WE":2,"TH":3,"FR":4,"SA":5,"SU":6}
    OccurencesWindowStartDate = ""
    """ Date from which occurences of iCalendar events should be returned by the enumerator"""
    OccurencesWindowEndDate = ""
    """ Date until which occurences of iCalendar events should be returned by the enumerator"""
#    path = ""
#    """ path where the file is located """
    sVCALENDAR = [] #the VCALENDAR as a string
    dVCALENDAR = {} #the VCALENDAR as a typed object
    lVEVENT = [] #the current VEVENT being loaded from iCalendar file, array of strings each string is an unfolded
    #line
#    ical_flat = []
    conformance = False
    ical_loaded = 0
    ical_error =0
    invevent = 0
    events = []
    """ object holding all the vevent objects (with typed data) from the parsed iCalendar """
#    flat_events = []
    debug_mode = 0
    debug_level = 0
    LogFilePath = "./log.txt"
    LogData = ""
    def inf(self):
        """ Returns generic info """
        info = "Follows:\n"
        info += "http://www.kanzaki.com/docs/ical/vevent.html \n"
        info += "http://www.kanzaki.com/docs/ical/rrule.html \n"
        info += "http://www.kanzaki.com/docs/ical/recur.html \n"
        info += "version: %s \n"%(self.version)
    def __init__(self):
        self.ical_loaded = 0
        self.debug_mode= 0
    def __del__(self):
        self.ical_datelist = []
        self.events_instances = []
    def debug(self,TrueFalse,LogPath="",debug_level=0):
        """ enables logging when executing (warning severe slow down)"""
        self.debug_mode = TrueFalse
        self._log("self debug is now",[TrueFalse])
        self.debug_level = debug_level
        self.LogFilePath = LogPath
        if len(LogPath)>0:
            try:
                log = open(self.LogFilePath,'w')
            except:
                raise Exception("File IO error","Could not open with write rights on log file:"+LogPath)
            log.write("Icalendar module version: %s, date/time running: %s"%(str(self.version),str(datetime.datetime.now())))
            log.close()
    def _log(self,title,listtodisplay,level=0):
#        print "___log",title,"\t list is:", listtodisplay
        if self.debug_mode == True:
            if level >= self.debug_level:
                line = "**"+title+"\n"
                for el in listtodisplay:
                    if len(str(el))<1000:
                        line = line + "\t"+str(el)
                    else:
                        line = line + "\t"+str(el)[0:1000]
                line +="\n"
#                print "\t\t ____log",line.replace("\n",""),"***********************"
                if len(self.LogFilePath)>0:
                    log=open(self.LogFilePath,'a')
                    log.write(line)
                    log.close()
                else:
                    self.LogData += line
    def GenRRULEstr(self,rules):
        """ Generates RRULE string from rules dictionary
        
        Used by generator. 
        """
        
        RRULE="RRULE:"
        if "FREQ" in rules:
            RRULE+="FREQ="+rules["FREQ"]+";"
            if "INTERVAL" in rules:
                RRULE += "INTERVAL="+str(rules["INTERVAL"])+";"
            if "COUNT" in rules:
                RRULE += "COUNT="+str(rules["COUNT"])+";"
            bylist = ["BYWEEKNO","BYMONTH","BYMONTHDAY","BYDAY","BYYEARDAY","BYSETPOS"]
            for bys in bylist:
                if bys in rules:
                    numlist = rules[bys]
                    icallist = self._pythonindex_to_icalindex(numlist)
                    RRULE+=bys+"="+icallist+";"
        if "WKST" in rules:
            RRULE+="WKST="+rules["WKST"]+";"
        if "UNTIL" in rules:
            RRULE+= "UNTIL"+rules["UNTIL"]+";"
        if RRULE[-1]==";":
            RRULE = RRULE[:-1]
        return RRULE
    def Validator(self,RFC_SCM,line_count=0,line="",level=0, alttxt = "", show = False):
        if show or self.conformance:
            if level ==0:
                if line_count==0 and line =="" and alttxt != "":
                    print "Warning: RFC5545 specifies \'%s\', %s"%(RFC5545_SCM[RFC_SCM],alttxt)
                else:
                    print "Warning: RFC5545 specifies \'%s\', following line is not compliant \n line: %s - %s"%(RFC5545_SCM[RFC_SCM],str(line_count),line)
            if level ==1:
                raise Exception("RFC5545 non compliance","RFC5545 specifies: \'%s\', following line is not compliant \n line: %s - %s"%(RFC5545_SCM[RFC_SCM],str(line_count),line))        
    def local_load(self,sLocalFilePath,conformance=False,append=False):
        """loads iCalendar file from local path
        
        conformance will force / or not checking ics file for conformance (not supported yet)
        """
        if not append:
            self.sVCALENDAR = []
            self.events = []
            self.events_instances = []
            
        self.conformance = conformance
        self._log("\t\t entering local load:",[sLocalFilePath])
#        self.local_path = path
        #here check local path
        string = open(sLocalFilePath,'r').readlines()
        #FIXME: add here the CRLF check and remove the \n from strings_load
        #RFC5545_SCM["3.1_1"]
        self.strings_load(string,conformance,append)
    def strings_load(self,strings,conformance=False,append = False):
        """Loads iCalendar from array of strings

        conformance will force / or not checking ics file for conformance (not supported yet)
        """
        line_count = 0
        if not (strings[0].replace("\n","").replace("\r","") == "BEGIN:VCALENDAR"):
            self.Validator("3.4_1", line_count =0, line = strings[0])
        if not (strings[-1].replace("\n","").replace("\r","") == "END:VCALENDAR"):
            self.Validator("3.4_1",line_count =len(strings),line = strings[-1])
        for line in strings:
            self._log("sVCALENDAR", [self.sVCALENDAR,line], 0)
            line_count +=1
            if line[-2:-1] == "\n\r":
                pass
            else:
                #FIXME: check why the local files are not conformant
#                self.Validator("VCALENDAR VALIDATOR: WARNING",RFC5545_SCM['3.1_1']+ "%s : %s"%(line_count,line),0)
                pass
            if line[0]==" " and len(self.sVCALENDAR)>0:
                self._log("line wrapper before",[line,self.sVCALENDAR])
                self.sVCALENDAR[-1]=self.sVCALENDAR[-1]+line[1:].replace("\n","").replace("\r","")
                self._log("line wrapper after",[line,self.sVCALENDAR])
            elif line[0]==" ":
                self.Validator("3.1_2",line = line,line_count = line_count, level =0)
            elif line.find(":")>0:
                self._log("line legnth",[len(line)])
                if  len(line)<76:
                    self.sVCALENDAR.append(line.replace("\n","").replace("\r",""))
                    self._log("sVCALENDAR added ?", [self.sVCALENDAR,line], 0)
                elif len(line)>75:
                    self.Validator("3.1_3",line = line,line_count = line_count,level = 0,show = conformance)
                    self.sVCALENDAR.append(line.replace("\n","").replace("\r",""))
                    self._log("sVCALENDAR added ?", [self.sVCALENDAR,line], 0)
                elif len(line)> 75 and len(line)<1000:
                    self.Validator("3.1_3",line = line,line_count = line_count,level = 0,show = conformance)
                    self.sVCALENDAR.append(line.replace("\n","").replace("\r",""))
                else :
                    self.Validator("3.1_4",line = line,line_count = line_count,level = 1,show = conformance)
            else:
                self.Validator('3.1_2',line = line,line_count = line_count,level =0)

        self.ical_loaded = 1
        if not append:
            self.events = []
            self.events_instances = []
    def _validate(self):
        """ Will secure UID only present once at least in the file"""
        uidlist = {}
        for event in self.events:
            if event["UID"]["val"] not in uidlist:
                uidlist[event["UID"]["val"]]=""
            else:
                self.Validator("3.8.4.7_1", alttxt = "this UID was found more than once in current file:"+event["UID"])
    def _mklist(self,start,end,step_size=1):
        #TODO:historical function created before knowing the range function, to be removed
#        result_list = []
#        while start <= end:
#            list.append(start)
#            start +=step_size
        result_list = range(start,end+1,step_size)
        return result_list

    def parse_loaded(self):
        """ parse loaded ical from file to array of typed data: self.events"""
        VCALENDAR_Components = {"VEVENT","VTIMEZONE","VTODO","VFREEBUSY","VJOURNAL"}
        Component_Name = ""
        self._log("\t\tentering loader",[])
        if self.ical_loaded == 0:
            self._log("error ",[RFC5545_SCM["3"]])
            self.Validator("3", level=1) #("VCALENDAR VALIDATOR","no vCALENDAR loaded")
            self.ical_error = 1
#            return 0
        elif self.ical_loaded == 1:
            #TODO: add here increments over the calendars
            self._log("ical loaded", [self.ical_loaded,self.sVCALENDAR],0)
            line_count = 0
            for line in self.sVCALENDAR:
                self._log("line is ", [line], 0)
                line_count +=1
                #first load the given event
#                pos = line.find("BEGIN:")
                if (line.find("BEGIN:")>=0):
                    self._log("new component?: LN / line / name",[line_count,line])
                    new_Component_Name= self._propval_line_split(line.replace("\n",""),line_count)[2] # ":".join(line.split(":")[1:]).replace("\n","")
                    if new_Component_Name in VCALENDAR_Components:
                        self._log("found new component: LN / line / name",[line_count,line,new_Component_Name])
                        Component_Name = new_Component_Name 
                        if (self.invevent == 0):
                            self.invevent = 1
                            self.lVEVENT =[]
                            LineCountBE = line_count
                        else:
                            self.Validator("3.6.1_1", line_count = line_count, line = line, level = 1) #raise Exception("VCALENDAR VALIDATOR","encountered BEGIN:%s before END:VEVENT @line: %s"%(Component_Name,str(line_count)))
                            self.ical_error = 1
                    else:
                        #FIXME: if we have a IANA or X-COMP
                        pass
#                pos = line.find("END:")
                elif (line.find("END:")>=0):
                    self._log("new end?: LN / line ",[line_count,line])
                    #if we have a event closing tag
                    closing_Component = self._propval_line_split(line.replace("\n",""),line_count)[2]#":".join(line.split(":")[1:]).replace("\n","") 
                    self._log("found end component: LN / line / name",[line_count,line,closing_Component ])
                    if closing_Component == Component_Name :
                        if self.invevent ==1:
                            #if we were already adding an event - stop adding
                            self.invevent = 0
#                            self.lVEVENT = self.lVEVENT+ [line.replace("\n","")]
                            self._log("event is", self.lVEVENT,2)
#                            print "l439",self.lVEVENT
                            if Component_Name == "VEVENT":
                                self._addEvent(self.lVEVENT,LineCountBE)
                            elif Component_Name == "VTIMEZONE":
                                #FIXME: add the function pointer here
                                pass
                    elif closing_Component in VCALENDAR_Components:
                        self.ical_error = 1
                        self.Validator("3.6.1_1", line_count = line_count, line = line, level = 1,show=True) #raise Exception("VCALENDAR VALIDATOR","encountered END:%s instead of END:%s @line: %s"%(closing_Component,Component_Name,str(line_count)))
                    else:
                        #FIXME: add code here for handling IANA and X-COMP
                        pass
#                if (self.invevent ==1):
#                    pass
##                    if line[0]==" ":
##                        #line unfolding
##                        self.lVEVENT = self.lVEVENT[:-1]+[self.lVEVENT[-1]+line[1:].replace("\n","")]
##                    else:
##                        self.lVEVENT = self.lVEVENT + [line.replace("\n","")]
#                elif line.find("BEGIN:VCALENDAR")>=0:
#                    pass
#                elif line.find("END:VCALENDAR")>=0:
#                    pass
                else:
                    if (self.invevent ==1):
                        self.lVEVENT = self.lVEVENT + [line]
                    else:
                        #here adding the calendar  properties
                        [prop,param, val] = self._propval_line_split(line,line_count)
                        self.dVCALENDAR[prop]={"param":param,"val":val}
#            print self.dVCALENDAR
            
            if Component_Name == "":
                self.Validator("3.6_3", 1, show=True)
            if "PRODID" not in self.dVCALENDAR:
                self.Validator("3.6_1", 1, show=True)
            if "VERSION" not in self.dVCALENDAR:
                self.Validator("3.6_2", 1, show=True)
            self._log("END Loader",[],0)
            
        if self.conformance:
            self._validate()
#        return 1
    def _addEvent(self,lVEVENT,EventFirstLine = 0):
        """
        loads self.event which is a string into 
        self.events which is an array of python types
        """
        self._log("\t\tentering event_load",[])
#        dtstart = ""
#        dtend = ""
#        sDuration = ""
#        duration = ""
#        uid = ""
#        rdates = []
#        exdates = []
        dVevent = {}
        self.vevent = vevent()
        vevent_load = { "TEXT": self.vevent.string_load,
                   "DATE-TIME-LIST": self.vevent.datelist_load,
                   "DATE-TIME": self.vevent.date_load,
                   "DURATION":self.vevent.duration_load,
                   "RECUR":self.vevent.rrule_load}
#        print "l514",lVEVENT
        line_count = EventFirstLine
        for line in lVEVENT:
            line_count +=1
#            print "line 480",line
            if line.find(":")>0:
                [prop,param,values]=self._propval_line_split(line,line_count)    #[line.split(":")[0],":".join(line.split(":")[1:])]
                try:
                    #here parse the value as per its type into python type
                    res = vevent_load[RFC5545_Properties[prop]](values,param,LineNumber = line_count)
                except KeyError:
                    res = values
            else:
                self.Validator("3.1_2", line_count = line_count, line = line)#raise Exception("VEVENT VALIDATOR","mandatory property not set on line"+line)
#            print dVevent, prop, res
            if prop in dVevent:
                #FIXME: need to support multiple RRULE lines
#                print lVEVENT
                if prop in ["dtstamp" , "uid ", "dtstart ","class","created"," description ", "geo","last-mod","location","organizer","priority","seq","status","summary","transp","url","recurid","dtend","duration"]:
                    self.Validator("3.6.1_2", line_count = line_count, line = line, level = 0)#raise Exception("VEVENT VALIDATOR", "property duplicated: "+prop)
                else:
                    #FIXME: need to add code for handling when multiple RRULE are available
                    dVevent[prop]= [dVevent[prop],{"param":param,"val":res}]
                    print "line 684",dVevent[prop]
            else:
                dVevent[prop] = {"param":param,"val":res}
#                dVevent[prop] = res

        self.vevent.validate_event(dVevent)

        if "DTSTART" not in dVevent:
            if "RRULE" in dVevent: 
                self.Validator('3.8.2.4_1', line_count = line_count, line = line, level = 0) #raise Exception("VEVENT VALIDATOR", RFC5545_SCM['3.8.2.4_1'])
            elif "METHOD" not in self.dVCALENDAR:
                self.Validator('3.8.2.4_2', line_count = line_count, line = line, level = 0)#raise Exception("VEVENT VALIDATOR", RFC5545_SCM['3.8.2.4_2'])
            elif 'DTEND' in dVevent and 'DURATION' in dVevent:
                #FIXME : add code here
                pass
            else:
                if "UID" in dVevent:
                    uid = dVevent["UID"]
                else:
                    uid = "not available"
                self.Validator("3.6.1_0", "event UID is:"+uid,level=1)
                pass
            
        self.events.append(dVevent)
#        self.event = []
        return dVevent
    def _pythonindex_to_icalindex(self,indexes,isDOW=False):
        """ used by generator to make iCalendar lists """
        ret_val = ""
        for index in indexes:
            ret_val += str(index)+","
        if ret_val[-1]==",":
            ret_val=ret_val[:-1]
        return ret_val
    def _flatten(self):
        """ goes over self.events and compute list of their instances"""
        self._log("******************\t\t\t entering _flatten",[])
        self.events_instances = []
        for event in self.events:
            tmp_event = event
            tmp_event["DTSTART"]=tmp_event["DTSTART"]["val"]
            self._log("event being _flatten is:",tmp_event)
            
            if "SUMMARY" in tmp_event:
                tmp_event["SUMMARY"]=tmp_event["SUMMARY"]["val"]
            else:
                tmp_event["SUMMARY"] = ""
            
            summary = tmp_event["SUMMARY"]
            
            """
            For cases where a "VEVENT" calendar component
            specifies a "DTSTART" property with a DATE value type but no
            "DTEND" nor "DURATION" property, the event's duration is taken to
            be one day.  For cases where a "VEVENT" calendar component
            specifies a "DTSTART" property with a DATE-TIME value type but no
            "DTEND" property, the event ends on the same calendar date and
            time of day specified by the "DTSTART" property.
            """
            if "DTEND" not in tmp_event:
                if "DURATION" not in tmp_event:
                    tmp_event["DTEND"] = tmp_event["DTSTART"]
                else:
                    tmp_event["DTEND"] = tmp_event["DTSTART"]+tmp_event["DURATION"]["val"][2]
                    #FIXME: add here the code for handling the DTEND+DURATION (years and months) - need to make
                    #the code either "instances accurate" or "date accurate"
                    #call: event["DTEND"] = add_year_months(event["DTEND"], event["DURATION"][1], event["DURATION"][0])
            else:
                tmp_event["DTEND"] = tmp_event["DTEND"]["val"]
            
            #FIXME: add here the multiple RRULE / EXRULE unfolding
            #event = #        [dtstart,dtend,rules, summary,uid,rdates,exdates] = event

#            t_res = self._flatten_rrule(event)
            if "RRULE" in tmp_event:
                tmp_event["RRULE"]=tmp_event["RRULE"]["val"]
            else:
                tmp_event["RRULE"]=[]
            t_res = self._flatten_rrule(tmp_event)
                
            if "RDATE" in tmp_event:
                rdates = tmp_event ["RDATE"]["val"]
            else:
                rdates = []
            if "EXDATE" in tmp_event:
                exdates = tmp_event["EXDATE"]["val"]
            else:
                exdates = []
            if len(rdates)>0:
                #here make sure that duplication of rrule and rdate do not result in 2 instances !
                t_res = t_res + [val for val in rdates if val not in t_res and val>=tmp_event["DTSTART"] and  val>=self.OccurencesWindowStartDate and val<=self.OccurencesWindowEndDate]
                self._log("319 days rdate", [rdates])
            if len(exdates)>0:
                #remove from lisst_dates any date in exdates
                t_res = [val for val in t_res if val not in exdates]

            self._log("*****************dates returned from _flatten",[t_res])
            
            for t_date in t_res:
                if len(self.events_instances)==0:
                    #if events_instances is empty
                    self.events_instances=[[t_date,summary,tmp_event["UID"]["val"]]]
                else:
                    #if already instances in the list
                    self.events_instances.append([t_date,summary,tmp_event["UID"]["val"]])
    def _flatten_rrule(self,event):
        """ where the actual algorithm for unrolling the rrule lies  
        
        also compute day instances when dtend>dtstart"""
        #@param event:the event with python data type to be processed
        #@param start:the first date from which this event should be displayed (note the greater of calendar start and event start will be used
        #@param end: optionnal parameter to decide until when the event should be displayed (note the earlier from this and calendar end will be used   
        #@param dates: list of days i.e. [datetime, datetime,...] of days where this event will occur 
        #@param list_dates: list of days i.e. [datetime, datetime, ...] of days where this event will occur
        #TODO: add handling of bycal=GREG, LUN-CHIN, ORTH
        #TODO: add handling of byeasterday = +/- integer
#        [dtstart,dtend,rules, summary,uid,rdates,exdates] = event
        dtstart = event["DTSTART"]
        dtend = event["DTEND"]
        if "RRULE" in event:
            rules = event["RRULE"]
        else:
            rules = []
        if "SUMMARY" in event:
            summary = event["SUMMARY"]
        else:
            summary = ""
        
        self._log("flatten rule, dtstart is:",[dtstart],0)
#        print "line 800 dtstart:",dtstart
        increment = "NONE"
        check_dow = False
        check_week = False
        check_doy = False
        check_setpos = False
        make_dow_list = False
        make_dom = False
        make_week = False
        dow ={'MO': [0],'TU': [0],"WE":[0],"TH":[0],"FR":[0],"SA":[0],"SU":[0]}
        setposlist = []
        list_dates = []
        dates = []
        dom_index = []
        tmp_dates = []
        count = 0
        MaxCount = 0
        days_step_size = 1
        weeks_step_size = 1 
        month_step_size = 1
        year_step_size = 1
        event_start = dtstart
        event_end = self.OccurencesWindowEndDate
        #here we generate the list of dates for all loaded cals
        self._log("227 rules are:",[rules])
        
        years = [event_start.year]
        months = [event_start.month]
        weeks = [self._isoCW(event_start.year, event_start.month, event_start.day)]
        days = [event_start.day]
        wkst = "MO"
        step_size = 1

        first_dom = 1
        last_dom = 31
        
        month_start = 1
        month_end = 12

        if len(rules)<=0:
            if dtstart not in list_dates:
                list_dates.append(dtstart)
            t_date = dtstart
            delta = datetime.timedelta(days = 1)
            t_date +=delta
                        
            while t_date <= dtend:
                list_dates.append(t_date)
                t_date +=delta
                self._log("from dtstart to dtend",[dtstart,dtend,t_date,list_dates],0)
        else:
            #switch between absolute computing and relative computing
            #if absolute: generate list
            #if relative
            #if len(years)>1:
            #    months = self._mklist(1, 12)
            #else:
            #    months = self._mklist(dtstart.month,dtend.month)
            #
            if "FREQ" in rules:
                if "INTERVAL" in rules:
                    step_size = int(rules["INTERVAL"])
                if rules["FREQ"] == "YEARLY":
                    increment = "YEAR"
                    year_step_size = step_size
                if rules["FREQ"] == "MONTHLY":
                    increment = "MONTH"
                    month_start = event_start.month
                    month_step_size = step_size
                if rules["FREQ"] == "WEEKLY":
                    make_week = True
                    make_dom = True
                    check_week = True
                    increment = "WEEK"
                    first_dom = event_start.day
                    month_start = event_start.month
                    weeks_step_size = step_size
                if rules["FREQ"] == "DAILY":
                    increment = "DAY"
                    first_dom = event_start.day
                    month_start = event_start.month
                    make_dom = True
                    self._log("277 make dom",[make_dom])
                    days_step_size = step_size
                if "COUNT" in rules:
                    MaxCount = rules["COUNT"]
                if "BYMONTH" in rules:
                    months = rules["BYMONTH"]
                if "BYWEEKNO" in rules:
                    weeks = rules["BYWEEKNO"]
                    check_week = True
                if "BYMONTHDAY" in rules:
                    dom_index = rules["BYMONTHDAY"]
                    make_dom = True
                if "BYDAY" in rules:
                    dow = rules["BYDAY"]
                    make_dow_list = True
                    check_dow = True
                    if increment == "YEAR" and ("BYMONTH" not in rules):
                        months = self._mklist(1, 12)
                if "BYYEARDAY" in rules:
                    doy = rules["BYYEARDAY"]
                    increment = "DAY"
                    make_dom = True
                    check_doy = True
                if "BYSETPOS" in rules:
                    check_setpos = True
                    make_dow_list = True
                    setposlist = rules["BYSETPOS"]
                if "WKST" in rules:
                    wkst = rules["WKST"]
            if "UNTIL" in rules:
                event_end = rules["UNTIL"]
            if make_dow_list == True:
                days = self._mklist(1, 31)
            #@param lday:  is the list of days matching dow before filtering by indexes
            
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |          |SECONDLY|MINUTELY|HOURLY |DAILY  |WEEKLY|MONTHLY|YEARLY|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYMONTH   |Limit   |Limit   |Limit  |Limit  |Limit |Limit  |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYWEEKNO  |N/A     |N/A     |N/A    |N/A    |N/A   |N/A    |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYYEARDAY |Limit   |Limit   |Limit  |N/A    |N/A   |N/A    |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYMONTHDAY|Limit   |Limit   |Limit  |Limit  |N/A   |Expand |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYDAY     |Limit   |Limit   |Limit  |Limit  |Expand|Note 1 |Note 2|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYHOUR    |Limit   |Limit   |Limit  |Expand |Expand|Expand |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYMINUTE  |Limit   |Limit   |Expand |Expand |Expand|Expand |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYSECOND  |Limit   |Expand  |Expand |Expand |Expand|Expand |Expand|
#   +----------+--------+--------+-------+-------+------+-------+------+
#   |BYSETPOS  |Limit   |Limit   |Limit  |Limit  |Limit |Limit  |Limit |
#   +----------+--------+--------+-------+-------+------+-------+------+
#      Note 1:  Limit if BYMONTHDAY is present; otherwise, special expand
#               for MONTHLY.
#
#      Note 2:  Limit if BYYEARDAY or BYMONTHDAY is present; otherwise,
#               special expand for WEEKLY if BYWEEKNO present; otherwise,
#               special expand for MONTHLY if BYMONTH present; otherwise,
#               special expand for YEARLY.
            
            #******** END OF CONFIGURATION, NOW RUNNING
            
            lday = {}
            self._log("years months weeks days",[years,months,weeks,days,event_start,event_end])
            self._log("checks are: dow, week,doy,setpos",[check_dow,check_week,check_doy,check_setpos])
            if month_step_size > 12:
                years = self._mklist(event_start.year, event_end.year,month_step_size/12+1)
            else:
                years = self._mklist(event_start.year, event_end.year,year_step_size)
            self._log("years months weeks days",[years,months,weeks,days,event_start,event_end])

            for year in years:
                if (increment == "MONTH" or increment == "DAY" or increment == "WEEK") and not ("BYMONTH" in rules):
                    months = self._mklist(month_start, month_end, month_step_size)
                    self._log("months updated:",[months])
                if make_week == True:
                    #make here list of week numbers which are to be used
                    week0_num = self._isoCW(year,month_start,first_dom,wkst)
                    weeks = self._mklist(week0_num, 53, weeks_step_size)
                    self._log("weeks updated:",[weeks])
                    if not ("BYDAY" in rules):
                        #if BYDAY not specified add the DOW from DTSTART
                        dow = {}
                        t_dow = self._icalDOW(datetime.date(year, month_start, first_dom))
                        dow[t_dow] = [0]
                        self._log("379 make week list:\tyear,month_start,first_dom,wkst,weeks\n",[year,month_start,first_dom,wkst,weeks,dow],1)
                for month in months:
                    if make_dom == True:
                        last_dom = self._last_dom(year, month)
#                        print "tmp log", first_dom,year, month
                        tmp_days = self._mklist(first_dom, last_dom,days_step_size)
                        days = []
                        if len(dom_index)>0:
                            #we enter here if dom_index has some content i.e. if the bymonthday was set in the rule
                            for index in dom_index:
                                if index>0:
                                    index = index -1
                                self._log("line 823 days, tmp_days, index",[days,tmp_days,index])
                                if index<len(tmp_days):
                                    #case where DOM is > length of month
                                    days.append(tmp_days[index])
                        else:
                            #else by default all day of month are considered
                            days = tmp_days
                    days0 = days[0]
                    cw = self._isoCW(year, month, days0, wkst)
                    lcw = cw
                    self._log("305 days month year",[days,month,year])
                    for day in days:
                        #HERE we start ploding through the days of the month and checking for all of them
                        #if they exist (feb 29th), then if they are in the good week number, then if they have the right DOW (monday, ...)
                        dateExist = True
                        good_date = True
                        try:
                            t_date = datetime.datetime(year,month,days0)
                            delta = datetime.timedelta(days = day-days0)
                            t_date +=delta
                        except ValueError:
                            #this is in case days0 is not a valid date of month for the given year/month
                            dateExist = False                        
                        if (dateExist == True) and (t_date.month==month):
                            if check_week == True:
                                cw = self._isoCW(year,month,day,wkst)
                                self._log("cw , y m d,wkst",[cw,year,month,day,wkst])
                                if (cw not in weeks) and (cw>=lcw):
                                    #check if cw is a good week number
                                    #if cw is not in the list need to make sure we havn't gone round the week number back to 1 while still same year
                                    good_date = False
                                    self._log("381 good date is false because cw not in weeks (last cw)",[cw,weeks,lcw])
                                elif lcw>cw:
                                #    #here is the case where the week numbering is back to 1 but we are still at the end of year
                                    if 53 in weeks:
                                        good_date = True
                                    else:
                                        good_date = False
                                    self._log("460 corner case week number:good_date, cw, lcw,weeks",[good_date,cw, lcw, weeks])
                            #if check_dow==True:
                            tdate_dow = self._icalDOW(t_date)
                            if tdate_dow not in dow:
                                good_date = False
                                self._log("387 good date false because of dow",[t_date,tdate_dow,dow])
                            if check_doy==True:
                                if t_date.timetuple().tm_yday in doy:
                                    good_date = True
                                    self._log ("424 good date false because of doy",[t_date,check_doy,t_date.timetuple().tm_yday,doy])
                                else:
                                    good_date = False
                                    self._log ("424 good date false because of doy",[t_date,check_doy,t_date.timetuple().tm_yday,doy])
                            if good_date == True:
                                lcw = cw
                                #last good date is used for computing next starting date when rolling over
                                last_good_date = t_date
                                if tdate_dow in lday:
                                    lday[tdate_dow].append(t_date)
                                else:
                                    lday[tdate_dow] = [t_date]
                                self._log("396 append date:",[t_date,lday])
                        if increment == "DAY":
                            self._log("552 - about to enter _sublist filtering on DAY increment: last_good_date, days_step_size",[last_good_date, days_step_size])
                            list_dates = self._sublist(lday,dates,summary,dow,check_setpos,setposlist,list_dates)
                            dates = []
                            lday = {}
                            t_date = last_good_date +datetime.timedelta(days = days_step_size)
                            if t_date.month>month:
                                first_dom = t_date.day
                                self._log("380 - next first dom",[first_dom,month,year])
                            elif t_date.year>year:
                                first_dom = t_date.day
                                month_start = t_date.month    
                                self._log("441: roll-out year on daily freq first_dom, month_start",[first_dom, month_start, t_date.year])                            
                    if increment == "WEEK":
                        first_dom = 1
                    if increment == "MONTH":
                        #enter here to empty the lday list and fill the list_dates
                        self._log("about to enter _sublist filtering on MONTH increment:\t lday,dates,dow,check_setpos_setposlit,list_dates\n",[lday,dates,summary,dow,check_setpos,setposlist,list_dates])
                        list_dates = self._sublist(lday,dates,summary,dow,check_setpos,setposlist,list_dates)
                        month_start = (months[-1]+month_step_size) % 12
                        dates = []
                        lday = {}
                if increment == "YEAR" or increment == "WEEK":
                    self._log("about to enter _sublist filtering on YEAR increment:\t lday,dates,dow,check_setpos_setposlit,list_dates\n",[lday,dates,summary,dow,check_setpos,setposlist,list_dates])
                    list_dates = self._sublist(lday,dates,summary,dow,check_setpos,setposlist,list_dates)
                    dates = []
                    lday = {}
                    if increment == "WEEK":
                        self._log("584: next first dom last_good_date, weeks_step_size",[last_good_date ,weeks_step_size])
                        #0.72b fixed
                        #before:
                        t_date = last_good_date +datetime.timedelta(weeks = weeks_step_size)
                        #after:
                        #need to compute last day of week - first day of week days ofset
                        
                        maxDOW = 0
                        minDOW = 7
                        for dw in dow:
                            dwi = self._weekday_map[dw]
                            if dwi<minDOW:
                                minDOW = dwi
                            if dwi>maxDOW:
                                maxDOW = dwi
#                            print "dw, dwi, min, max", dw, dwi, min, max
                        daysgap = 7-(maxDOW-minDOW)
                        t_date = last_good_date +datetime.timedelta(weeks = weeks_step_size-1)+datetime.timedelta(days = daysgap)
                        #end 0.72b->0.72c fix
                        if t_date.year>year:
                            first_dom = t_date.day
                            month_start = t_date.month
                            self._log("584: next first dom",[first_dom,month_start,t_date.year])
                #month_start = 1
        self._log("list of dates before the validation: list_dates and tmp_dates \n",[list_dates,tmp_dates])
        self._log("interval dates: event_start,event_end,self.OccurencesWindowStartDate,self.OccurencesWindowEndDate \n",[event_start,event_end,self.OccurencesWindowStartDate,self.OccurencesWindowEndDate])
        for t_date in list_dates:
            if t_date>=event_start and  t_date>=self.OccurencesWindowStartDate and t_date<=self.OccurencesWindowEndDate and t_date<=event_end:
                self._log("Maxcount",[MaxCount, t_date])
                if MaxCount >0:
                    #if we count the number of recurrencies then only add dates as long as below max number
                    count = count+1
                    if count<= MaxCount:
                        self._log("count, MaxCount",[count,MaxCount, t_date])
                        tmp_dates.append(t_date)
                else:
                    #if we are not counting the number of reccurencies then just keep it
                    tmp_dates.append(t_date)
        list_dates = tmp_dates
        
        return list_dates
    def add_year_months(self,date,years,months,InstanceAccurate = True):
        """"will add nMonths to the date, if not 100% accurate it will either compromise the date (like 31 jan +1 mo = 28 fev InstanceAccurate
        2012/2/29 + 1 year = "Na" for DateAccurate
        """
        months = months % 12
        years = years + months / 12
        
        year = date.year
        month = date.month
        new_date = None
        try:
            new_date= date(year+years,month+months)
        except:
            pass
        
        return new_date
    def _propval_line_split(self,LineContent,LineNumber =0):
        """ takes a line and splits in property, parameters and value
        
        will also secure that the property is a valid property
        """
        self._log("line loader", [LineContent], 0)
        if LineContent.find(":")>0:
            [propnparam,value]=[LineContent.split(":")[0], ":".join(LineContent.split(":")[1:])]
            if propnparam.find(";")>0:
                [prop,param]=[propnparam.split(";")[0],propnparam.split(";")[1:]]
            else:
                [prop,param]=[propnparam,[]]
        else:
            if LineNumber ==0:
                LineNumber = ""
            else:
                LineNumber = str(LineNumber)           
            self.Validator("3.1_2", line_count = LineNumber, line = LineContent, level = 0)#raise Exception("VCALENDAR WARNING","Expected a semi-column ':' %s : %s"%(LineNumber,LineContent))
        self._log("line loaded", [prop,param,value], 0)
        if prop not in RFC5545_Properties:
            if not prop.find("X-") == 0:
                self.Validator("8.3.2_1", line_count = LineNumber, line = LineContent, level = 0)
        return [prop,param,value]
    def _last_dom(self,year,month):
        day = datetime.datetime(year,month,1)
        for i in range(1,32):
            delta = datetime.timedelta(days = i)
            new = day + delta
            if new.month != day.month:
                return i
    def _icalDOW(self,date):
        "returns DOW ical way from date (MO, TU, ..."
        return date.strftime("%a")[-3:-1].upper()
    def _isoCW(self,year, month,day,wkst="MO",iso=True):
        """returns the iso week number of the passed date, 0 if invalid date
        
        CW is week number of year/month/day
        CW is set to iso week number (ISO8601
        wkst is currenlty used start of week
        index is index of day within week (first value irrelevant, just needs to remain consistant)
        if day.index > wkst.index 
         if day is after wkst but before monday (monday as we use iso8601 calendar)
         and day is before monday
         then CW -=1
        
        examples:
        2008,dec,29, with wkst="MO" the weeknumber is 1 (day is monday and 4 days ,
        
        Dec29    |    Dec30    |    Dec31    |    Jan1    |    Jan2    |    Jan3    |    Jan4
        Mo            Tuesday        wednesday    Thursday    Friday        Saturday    Sunday
        ISOWK=1        ISOWK=1        ISOWK=1    ISOWK=1        ISOWK=1    ISOWK=1        ISOWK=1
        >=    Y        Y


       [2009,1,5,"MO",2,0],
       [2012,1,18,"TH",3,3]]
        
        """
        
        #2005-01-01 is 2004-W53-6
        CW = 0
        dow = ["TU","WE","TH","FR","SA","SU","MO"]
        try:
            CW= datetime.datetime(year,month,day).isocalendar()[1]
            #if dow is between wkst and monday then CW-=1 else keep CW, "MO" was put end of list so if wkst = MO then no change
            if (dow.index(self._icalDOW(datetime.date(year,month,day)))-dow.index(wkst)>=0) and (dow.index(wkst)<dow.index("MO")) and (dow.index(self._icalDOW(datetime.date(year,month,day))) < dow.index("MO")):
                    CW -= 1
        except ValueError:
            #this is in case days0 is not a valid date of month for the given year/month
            CW = 0
        return CW
    def _sublist(self,lday,dates,summary,dow,check_setpos,setposlist,list_dates):
        """ used in flatten rrule to accelerate by only looking at some dates within a list"""
        self._log("347 list_Dates",[list_dates])
        self._log("348 lday",[lday])
        self._log("349 setposlist",[setposlist])
        self._log("350 dow",[dow])
        #same as above for the year
        for dowi in lday:
            if 0 in dow[dowi]:
                for date in lday[dowi]:
                    dates.append(date)
            else:
                for dow_index in dow[dowi]:
                    if dow_index>0:
                        dow_index -=1
                    if len(dates)==0:
                        dates = [lday[dowi][dow_index]]
                    else:
                        dates.append(lday[dowi][dow_index])
        self._log("356 dates before check_setpos",[dates])
        dates = sorted(dates)
        if check_setpos == True:
            dates_pos = []
            self._log("363 dates sorted", [dates])
            for setpos in setposlist:
                if setpos>0:
                    setpos = setpos-1
                dates_pos.append(dates[setpos])
            dates = dates_pos
        if len(list_dates)==0:
            list_dates = dates
        else:
            for date in dates:
                list_dates.append(date)
        self._log("413: list_dates at end of _sublist",[list_dates])
        return list_dates
    def get_event_instances(self,start=datetime.datetime.today().strftime("%Y%m%d"),end=datetime.datetime.today().strftime("%Y%m%d"),count=-1):
        """Returns an array of events with dates, uid, and summary
        
        The function returns the array of events within a given date window (defined by start and end),
        should only a certain number of events be needed either from a start date or to an end date the
        missing date should be set to Null
        """
        self.OccurencesWindowStartDate = datetime.datetime.strptime(start,"%Y%m%d")
        self.OccurencesWindowEndDate = datetime.datetime.strptime(end,"%Y%m%d")
        self.parse_loaded()
        self._flatten()
        self.events_instances = sorted(self.events_instances)
        return self.events_instances
    def Gen_iCalendar(self):
        """ takes the self.dVCALENDAR and generates an icalendar string """
        
        self.vevent = vevent()
        vevent_write = {
                        "TEXT": self.vevent.string_write,
                        "DATE-TIME": self.vevent.date_write,
                        "DURATION":self.vevent.duration_write,
                        "RECUR":self.vevent.rrule_write
                        }
        
        sCalendar = "BEGIN:VCALENDAR"+CRLF
        if not "VERSION" in self.dVCALENDAR:
            self.dVCALENDAR["VERSION"]="2.0"
        if not "PRODID" in self.dVCALENDAR:
            self.dVCALENDAR["PRODID"]="1-annum.com_sponsors_pyICSParser"
        for Prop in self.dVCALENDAR:
            #here add calendar properties
#            print "1235: prop, dVCALENDAR",Prop,self.dVCALENDAR[Prop]
            param = ""
            print self.dVCALENDAR[Prop]
            if "param" in self.dVCALENDAR[Prop]:
                for p in self.dVCALENDAR[Prop]["param"]:
                    param +=p+";"
            else:
                param = ""
            if not "val" in self.dVCALENDAR[Prop]:
                propvalue = self.dVCALENDAR[Prop]
            else:
                propvalue = self.dVCALENDAR[Prop]["val"]
            sCalendar+=Prop+param+":"+propvalue+CRLF
        for event in self.events:
            if "UID" not in event:
                event["UID"]="FIXMEUID"
            if "DTSTAMP" not in event:
                event["DTSTAMP"]={"param":"","val":datetime.datetime.now()}
            sCalendar += "BEGIN:VEVENT"+CRLF
            for Prop in event:
                print Prop
                if not "val" in event[Prop]:
                    propvalue = event[Prop]
                else:   
                    propvalue = event[Prop]["val"]
                print Prop,propvalue
#                newline = Prop+":"+vevent_write[Prop](propvalue)+CRLF
                #RFC5545_Properties[Prop] will give the relevant type
                #vevent_write["TEXT"] will call self.vevent.string_write(_
                newline = Prop+":"+vevent_write[RFC5545_Properties[Prop]](propvalue)+CRLF
                sCalendar+= self.vevent.line_wrap(newline)
            sCalendar += "END:VEVENT"+CRLF
            
        sCalendar += "END:VCALENDAR"+CRLF
        return sCalendar