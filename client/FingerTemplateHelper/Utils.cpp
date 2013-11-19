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

void Utils::TextRead(const CString file, CString& text)
{
	CFile f;
	f.Open(file,CFile::modeRead);
	f.Read(text.GetBuffer(f.GetLength()),f.GetLength());
	f.Close();
}
