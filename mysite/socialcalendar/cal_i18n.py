# -*- coding: utf-8 -*-
"""
Created on Dec 18, 2012

@author: Oberron
@version: 0.1
@see: iCalendar spec RFC5545
@change: 0.1- creation for first 10 economic powers
"""
#top 10 economic powers
#USA China Japan Germany France Brazil UK Italy India Russia
#source: http://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)

version = "0.1"
null = 0

cal_i18n = { 
"fr" :
{
"name": "fr-FR",
"Name": "Français (France)",
"language": "fr",
"firstDay": 1,
"dow": {
        "names": ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"],
        "namesAbbr": ["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"],
        "namesShort": ["L","M","M","J","V","S","D"]
    },
    "months": {
        "names": ["Janvier","Fevrier","Mars","Avril","Mai","Juin","Juillet","Aout","Septembre","Octobre","Novembre","Decembre"],
        "namesAbbr": ["Jan","Fev","Mar","Avr","Mai","Jun","Jul","Aug","Sep","Oct","Nov","Dec",""]
    },
	"AM": null,
    "PM": null,
    "eras": [{"name":"apr. J.-C.","start":null,"offset":0}],
    "patterns": {
        "d": "dd.MM.yyyy",
        "D": "dddd, d. MMMM yyyy",
        "t": "HH:mm",
        "T": "HH:mm:ss",
        "f": "dddd, d. MMMM yyyy HH:mm",
        "F": "dddd, d. MMMM yyyy HH:mm:ss",
        "M": "dd MMMM",
        "Y": "MMMM yyyy"
    }
},
"en": { 
"name": "en-EN",
"Name": "English (England)",
"language": "en",
	    "firstDay": 1,
	    "dow": {
	        "names": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
	        "namesAbbr": ["Mo","Tu","We","Th","Fr","Sa","Su"],
	        "namesShort": ["M","T","W","T","F","S","S"]
	    },
	    "months": {
	        "names": ["January","February","March","April","May","June","July","August","September","October","November","December",""],
	        "namesAbbr": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec",""]
	    },
		"AM": "AM",
	    "PM": "PM",
	    "eras": [{"name":"A.D.","start":null,"offset":0}],
	    "patterns": {
	        "d": "MM.dd.yyyy",
	        "D": "dddd, d. MMMM yyyy",
	        "t": "HH:mm",
	        "T": "HH:mm:ss",
	        "f": "dddd, d. MMMM yyyy HH:mm",
	        "F": "dddd, d. MMMM yyyy HH:mm:ss",
	        "M": "dd MMMM",
	        "Y": "MMMM yyyy"
	    }
},
"de" :
{
"name": "de-DE",
"Name": "Deutsch (Deutschland)",
"language": "de",
"firstDay": 1,
"dow": {
    "names": ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"],
    "namesAbbr": ["Mo","Di","Mi","Do","Fr","Sa","So"],
    "namesShort": ["Mo","Di","Mi","Do","Fr","Sa","So"]
},
"months": {
    "names": ["Januar","Februar","Mearz","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember",""],
    "namesAbbr": ["Jan","Feb","Mrz","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez",""]
},
"AM": null,
"PM": null,
"eras": [{"name":"n. Chr.","start":null,"offset":0}],
"patterns": {
    "d": "dd.MM.yyyy",
    "D": "dddd, d. MMMM yyyy",
    "t": "HH:mm",
    "T": "HH:mm:ss",
    "f": "dddd, d. MMMM yyyy HH:mm",
    "F": "dddd, d. MMMM yyyy HH:mm:ss",
    "M": "dd MMMM",
    "Y": "MMMM yyyy" }
},
"es":{
	"dow" : {"names":["Lunes", "Martes", "MiÃ©rcoles", "Jueves", "Viernes", "SÃ¡bado", "Domingo" ]},
	"months":{"names":["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio??", "Juli", "Agosto", "Septiembre","Octubre", "Noviembre", "Diciembre" ] }
},
"ch":{
	"dow":{"names":["星期一","星期二","星期三","星期四","星期五","星期六","星期天"]},
	"months":{"names":["一月","二月","三月","四月","五月","六五","七五","八五","九月","十月","十一","十二月"]}},
"jp": {
	"dow":{"names":["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日","日曜日"]},
	"months":{"names":["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月","10月","11月", "12月"]}},
"pt":{
	"dow":{"names":["segunda-feira", "Terça-feira", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]},
	"months":{"names":["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro","Outubro", "Novembro", "Dezembro"]}},
"it":{
	"dow":{"names":["Lunedì", "Martedì", "Mercoledì", "Giovedi", "Venerdì", "Sabato", "Domenica"]},
	"months":{"names":["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre","Ottobre", "Novembre", "Dicembre"]}},
"hi":{
	"dow":{"names":["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]},
	"months":{"names":["जनवरी", "फरवरी में", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितम्बर", "अक्तूबर", "नवंबर", "दिसम्बर"]}},
"ru":{
	"dow": { "names": ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"] },
	"months": { "names": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"] }
}
}

def test():
	print cal_i18n["hi"]["months"]["names"][11]

test()