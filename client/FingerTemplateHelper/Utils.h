#pragma once

// Utils ����Ŀ��

class Utils : public CObject
{
public:
	Utils();
	virtual ~Utils();
public:
	static void TextRead(const CString file, CString& text);
};


