// FingerTemplateHelper.h : PROJECT_NAME Ӧ�ó������ͷ�ļ�
//

#pragma once

#ifndef __AFXWIN_H__
	#error "�ڰ������ļ�֮ǰ������stdafx.h�������� PCH �ļ�"
#endif

#include "resource.h"		// ������


// CFingerTemplateHelperApp:
// �йش����ʵ�֣������ FingerTemplateHelper.cpp
//

class CFingerTemplateHelperApp : public CWinApp
{
public:
	CFingerTemplateHelperApp();

// ��д
	public:
	virtual BOOL InitInstance();

// ʵ��

	DECLARE_MESSAGE_MAP()
};

extern CFingerTemplateHelperApp theApp;