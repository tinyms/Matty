// Utils.cpp : 实现文件
//

#include "stdafx.h"
#include "FingerTemplateHelper.h"
#include "Utils.h"


// Utils

Utils::Utils()
{
}

Utils::~Utils()
{
}


// Utils 成员函数

void Utils::PostFingerTemplate(CString url, CString tpl){
	CURL* curl = 0;
	CURLcode errCode = CURLE_OK;
	curl = curl_easy_init();
	curl_easy_setopt(curl, CURLOPT_HTTPPOST, 1);
	curl_easy_setopt(curl, CURLOPT_URL, (LPCSTR)url);
	
	curl_easy_setopt(curl, CURLOPT_POSTFIELDS, (LPCSTR)tpl);
	errCode = curl_easy_perform(curl);
	if(errCode != CURLE_OK)  
       fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(errCode));

	curl_easy_cleanup(curl);
}

void Utils::TextRead(const CString file, CString& text)
{
	CStdioFile f;
	BOOL b = f.Open(file,CFile::modeRead);
	if(b){
		f.ReadString(text);
		f.Close();
	}
}

void Utils::TextWrite(const CString file, CString text){
	CStdioFile f;
	BOOL b = f.Open(file,CFile::modeCreate|CFile::modeWrite);
	if(b){
		f.WriteString(text);
		f.Close();
	}
}

BOOL Utils::FileExist(CString FileName){
	CFileFind fFind;
    return fFind.FindFile(FileName); 
}

void Utils::DelFile(const CString path){
	CFile tmp;
	tmp.Remove(path);
}
