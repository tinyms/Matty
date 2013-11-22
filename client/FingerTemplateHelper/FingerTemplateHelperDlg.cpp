// FingerTemplateHelperDlg.cpp : ʵ���ļ�
//

#include "stdafx.h"
#include "FingerTemplateHelper.h"
#include "FingerTemplateHelperDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// ����Ӧ�ó��򡰹��ڡ��˵���� CAboutDlg �Ի���

class CAboutDlg : public CDialog
{
public:
	CAboutDlg();

// �Ի�������
	enum { IDD = IDD_ABOUTBOX };

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV ֧��

// ʵ��
protected:
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialog(CAboutDlg::IDD)
{
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialog)
END_MESSAGE_MAP()


// CFingerTemplateHelperDlg �Ի���


CFingerTemplateHelperDlg::CFingerTemplateHelperDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CFingerTemplateHelperDlg::IDD, pParent)
	, m_device_cnn(false)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDI_APP_ICON);
}

void CFingerTemplateHelperDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	DDX_Control(pDX, IDC_ZKFPENGX, m_CZKFPEngX);
	DDX_Control(pDX, IDC_CNN_DEVICE_BTN, m_cnn_device_btn);
	DDX_Control(pDX, IDC_PICK_BTN, m_pick_btn);
}

BEGIN_MESSAGE_MAP(CFingerTemplateHelperDlg, CDialog)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	//}}AFX_MSG_MAP
	ON_BN_CLICKED(IDC_CNN_DEVICE_BTN, &CFingerTemplateHelperDlg::OnBnClickedCnnDeviceBtn)
	ON_BN_CLICKED(IDC_PICK_BTN, &CFingerTemplateHelperDlg::OnBnClickedPickBtn)
	ON_WM_CLOSE()
END_MESSAGE_MAP()


// CFingerTemplateHelperDlg ��Ϣ�������

BOOL CFingerTemplateHelperDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// ��������...���˵�����ӵ�ϵͳ�˵��С�

	// IDM_ABOUTBOX ������ϵͳ���Χ�ڡ�
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != NULL)
	{
		CString strAboutMenu;
		strAboutMenu.LoadString(IDS_ABOUTBOX);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// ���ô˶Ի����ͼ�ꡣ��Ӧ�ó��������ڲ��ǶԻ���ʱ����ܽ��Զ�
	//  ִ�д˲���
	SetIcon(m_hIcon, TRUE);			// ���ô�ͼ��
	SetIcon(m_hIcon, FALSE);		// ����Сͼ��

	// TODO: �ڴ���Ӷ���ĳ�ʼ������
	this->m_device_cnn = FALSE;
	this->m_pick_count = 0;
	return TRUE;  // ���ǽ��������õ��ؼ������򷵻� TRUE
}

void CFingerTemplateHelperDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialog::OnSysCommand(nID, lParam);
	}
}

// �����Ի��������С����ť������Ҫ����Ĵ���
//  �����Ƹ�ͼ�ꡣ����ʹ���ĵ�/��ͼģ�͵� MFC Ӧ�ó���
//  �⽫�ɿ���Զ���ɡ�

void CFingerTemplateHelperDlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // ���ڻ��Ƶ��豸������

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// ʹͼ���ڹ��������о���
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// ����ͼ��
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialog::OnPaint();
	}
}

//���û��϶���С������ʱϵͳ���ô˺���ȡ�ù����ʾ��
//
HCURSOR CFingerTemplateHelperDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}


void CFingerTemplateHelperDlg::OnBnClickedCnnDeviceBtn()
{
	if(this->m_device_cnn){
		this->m_CZKFPEngX.EndEngine();
		this->m_device_cnn = FALSE;
		SetDlgItemText(IDC_CNN_DEVICE_BTN,_T("����ָ�Ʋɼ���"));
		SetDlgItemText(IDC_PICK_BTN,CString("��ʼ�ɼ�"));
		MessageBox(_T("�ѶϿ��豸"));
	}else{
		if (this->m_CZKFPEngX.InitEngine() == 0)
		{
			this->m_CZKFPEngX.put_FPEngineVersion(_T("10"));
			this->m_device_cnn = TRUE;
			SetDlgItemText(IDC_CNN_DEVICE_BTN,_T("�Ͽ�����"));
			MessageBox(_T("�ɹ������豸"));
		} 
		else
		{
			this->m_CZKFPEngX.EndEngine();
			MessageBox(_T("δ�ҵ��豸."));
		}
	}
}

void CFingerTemplateHelperDlg::OnBnClickedPickBtn()
{
	if(!this->m_device_cnn){
		MessageBox(_T("���������豸."));
		return;
	}
	this->m_CZKFPEngX.CancelEnroll();
	this->m_CZKFPEngX.put_EnrollCount(3);
	this->m_CZKFPEngX.BeginEnroll();
	this->EnableButtons(FALSE);
	SetDlgItemText(IDC_PICK_BTN,_T("�ɼ���."));
}

void CFingerTemplateHelperDlg::EnableButtons(bool disabled)
{
	GetDlgItem(IDC_CNN_DEVICE_BTN)->EnableWindow(disabled);
	GetDlgItem(IDC_PICK_BTN)->EnableWindow(disabled);
}
BEGIN_EVENTSINK_MAP(CFingerTemplateHelperDlg, CDialog)
	ON_EVENT(CFingerTemplateHelperDlg, IDC_ZKFPENGX, 9, CFingerTemplateHelperDlg::OnEnrollZkfpengx, VTS_BOOL VTS_VARIANT)
	ON_EVENT(CFingerTemplateHelperDlg, IDC_ZKFPENGX, 8, CFingerTemplateHelperDlg::OnImageReceivedZkfpengx, VTS_PBOOL)
END_EVENTSINK_MAP()

void CFingerTemplateHelperDlg::OnEnrollZkfpengx(BOOL ActionResult, const VARIANT& ATemplate)
{
	CString sTmp("");
	if(ActionResult){
		sTmp = this->m_CZKFPEngX.GetTemplateAsStringEx(_T("10"));
		//���͵�����������
		
		if(!Utils::FileExist(_T("ip.txt"))){
			Utils::TextWrite(_T("ip.txt"),_T("127.0.0.1"));
		}
		CString ip = _T("");
		Utils::TextRead(_T("ip.txt"),ip);
		CString ukey;
		Utils::TextRead(_T("temp.key"),ukey);
		CString postUrl = _T("");
		postUrl.Format(_T("http://%s/api/tinyms.validwork.finger.template/sign?ukey=%s"),ip,ukey);
		Utils::PostFingerTemplate(postUrl,sTmp);
		//�����ɼ�
		this->m_CZKFPEngX.CancelEnroll();
		this->m_CZKFPEngX.put_EnrollCount(3);
		this->m_CZKFPEngX.BeginEnroll();
		//this->EnableButtons(TRUE);
		SetDlgItemText(IDC_TIP_STATIC,_T("�ɼ��ɹ�,��һ����ָ����һ����"));
		this->m_pick_count = 0;
	}
}

void CFingerTemplateHelperDlg::OnImageReceivedZkfpengx(BOOL* AImageValid)
{
	this->m_pick_count++;
	CString tip;
	tip.Format(_T("�ɼ�ָ��%d��(��3�μ���)"),this->m_pick_count);
	SetDlgItemText(IDC_TIP_STATIC,tip);
	HDC hdc;
	hdc = this->GetDC()->m_hDC;
	this->m_CZKFPEngX.PrintImageAt(long(hdc), 20, 25, this->m_CZKFPEngX.get_ImageWidth()+70, this->m_CZKFPEngX.get_ImageHeight()-100);
}

void CFingerTemplateHelperDlg::OnClose()
{
	if(this->m_device_cnn){
		this->m_CZKFPEngX.EndEngine();
	}
	CDialog::OnClose();
}
