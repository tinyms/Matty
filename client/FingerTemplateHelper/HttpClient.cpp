// HttpClient.cpp : 实现文件
//

#include "stdafx.h"
#include "HttpClient.h"


// CHttpClient
#define  BUFFER_SIZE       1024

#define  NORMAL_CONNECT             INTERNET_FLAG_KEEP_CONNECTION
#define  SECURE_CONNECT                NORMAL_CONNECT | INTERNET_FLAG_SECURE
#define  NORMAL_REQUEST             INTERNET_FLAG_RELOAD | INTERNET_FLAG_DONT_CACHE 
#define  SECURE_REQUEST             NORMAL_REQUEST | INTERNET_FLAG_SECURE | INTERNET_FLAG_IGNORE_CERT_CN_INVALID


CHttpClient::CHttpClient(LPCTSTR strAgent)
{
	m_pSession = new CInternetSession(strAgent);
    m_pConnection = NULL;
    m_pFile = NULL;
}

CHttpClient::~CHttpClient()
{
	Clear();
    if(NULL != m_pSession)
    {
        m_pSession->Close();
        delete m_pSession;
        m_pSession = NULL;
    }
}


// CHttpClient 成员函数
void CHttpClient::Clear()
{
    if(NULL != m_pFile)
    {
        m_pFile->Close();
        delete m_pFile;
        m_pFile = NULL;
    }

    if(NULL != m_pConnection)
    {
        m_pConnection->Close();
        delete m_pConnection;
        m_pConnection = NULL;
    }
}

int CHttpClient::ExecuteRequest(LPCTSTR strMethod, LPCTSTR strUrl, LPCTSTR strPostData, string &strResponse)
{
    CString strServer;
    CString strObject;
    DWORD dwServiceType;
    INTERNET_PORT nPort;
    strResponse = "";

    AfxParseURL(strUrl, dwServiceType, strServer, strObject, nPort);

    if(AFX_INET_SERVICE_HTTP != dwServiceType && AFX_INET_SERVICE_HTTPS != dwServiceType)
    {
        return FAILURE;
    }

    try
    {
        m_pConnection = m_pSession->GetHttpConnection(strServer,
            dwServiceType == AFX_INET_SERVICE_HTTP ? NORMAL_CONNECT : SECURE_CONNECT,
            nPort);
        m_pFile = m_pConnection->OpenRequest(strMethod, strObject, 
            NULL, 1, NULL, NULL, 
            (dwServiceType == AFX_INET_SERVICE_HTTP ? NORMAL_REQUEST : SECURE_REQUEST));

        //DWORD dwFlags;
        //m_pFile->QueryOption(INTERNET_OPTION_SECURITY_FLAGS, dwFlags);
        //dwFlags |= SECURITY_FLAG_IGNORE_UNKNOWN_CA;
        ////set web server option
        //m_pFile->SetOption(INTERNET_OPTION_SECURITY_FLAGS, dwFlags);

        m_pFile->AddRequestHeaders(_T("Accept: *,*/*"));
        m_pFile->AddRequestHeaders(_T("Accept-Language: zh-cn"));
        m_pFile->AddRequestHeaders(_T("Content-Type: application/x-www-form-urlencoded"));
        m_pFile->AddRequestHeaders(_T("Accept-Encoding: gzip, deflate"));

        m_pFile->SendRequest(NULL, 0, (LPVOID)(LPCTSTR)strPostData, strPostData == NULL ? 0 : _tcslen(strPostData));

        char szChars[BUFFER_SIZE + 1] = {0};
        string strRawResponse = "";
        UINT nReaded = 0;
        while ((nReaded = m_pFile->Read((void*)szChars, BUFFER_SIZE)) > 0)
        {
            szChars[nReaded] = '\0';
            strRawResponse += szChars;
            memset(szChars, 0, BUFFER_SIZE + 1);
        }

        int unicodeLen = MultiByteToWideChar(CP_UTF8, 0, strRawResponse.c_str(), -1, NULL, 0);
        WCHAR *pUnicode = new WCHAR[unicodeLen + 1];
        memset(pUnicode,0,(unicodeLen+1)*sizeof(wchar_t));

        MultiByteToWideChar(CP_UTF8,0,strRawResponse.c_str(),-1, pUnicode,unicodeLen);
        CString cs(pUnicode);
        delete []pUnicode; 
        pUnicode = NULL;

		std::string STDStr(CW2A(cs.GetString(), CP_UTF8));
		strResponse = STDStr;

        Clear();
    }
    catch (CInternetException* e)
    {
        Clear();
        DWORD dwErrorCode = e->m_dwError;
        e->Delete();

        DWORD dwError = GetLastError();

        if (ERROR_INTERNET_TIMEOUT == dwErrorCode)
        {
            return OUTTIME;
        }
        else
        {
            return FAILURE;
        }
    }
    return SUCCESS;
}

int CHttpClient::HttpGet(LPCTSTR strUrl, LPCTSTR strPostData, string &strResponse)
{
    return ExecuteRequest(_T("GET"), strUrl, strPostData, strResponse);
}

int CHttpClient::HttpPost(LPCTSTR strUrl, LPCTSTR strPostData, string &strResponse)
{
	return ExecuteRequest(_T("POST"), strUrl, strPostData, strResponse);
}