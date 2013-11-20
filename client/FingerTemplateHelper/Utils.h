#pragma once

// Utils ÃüÁîÄ¿±ê
#include <curl/curl.h>

class Utils : public CObject
{
public:
	Utils();
	virtual ~Utils();
public:
	static void TextRead(const CString file, CString& text);
	static void TextWrite(const CString file, CString text = _T(""));
	static BOOL FileExist(CString FileName);
	static void DelFile(const CString path);
	static void PostFingerTemplate(CString url, CString tpl);
};


