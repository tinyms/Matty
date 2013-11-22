// FingerTemplateHelperDlg.cpp : 实现文件
//

#include "stdafx.h"
#include "FingerTemplateHelper.h"
#include "FingerTemplateHelperDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// 用于应用程序“关于”菜单项的 CAboutDlg 对话框

class CAboutDlg : public CDialog
{
public:
	CAboutDlg();

// 对话框数据
	enum { IDD = IDD_ABOUTBOX };

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV 支持

// 实现
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


// CFingerTemplateHelperDlg 对话框


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


// CFingerTemplateHelperDlg 消息处理程序

BOOL CFingerTemplateHelperDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// 将“关于...”菜单项添加到系统菜单中。

	// IDM_ABOUTBOX 必须在系统命令范围内。
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

	// 设置此对话框的图标。当应用程序主窗口不是对话框时，框架将自动
	//  执行此操作
	SetIcon(m_hIcon, TRUE);			// 设置大图标
	SetIcon(m_hIcon, FALSE);		// 设置小图标

	// TODO: 在此添加额外的初始化代码
	this->m_device_cnn = FALSE;
	this->m_pick_count = 0;
	return TRUE;  // 除非将焦点设置到控件，否则返回 TRUE
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

// 如果向对话框添加最小化按钮，则需要下面的代码
//  来绘制该图标。对于使用文档/视图模型的 MFC 应用程序，
//  这将由框架自动完成。

void CFingerTemplateHelperDlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // 用于绘制的设备上下文

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// 使图标在工作矩形中居中
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// 绘制图标
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialog::OnPaint();
	}
}

//当用户拖动最小化窗口时系统调用此函数取得光标显示。
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
		SetDlgItemText(IDC_CNN_DEVICE_BTN,_T("连接指纹采集仪"));
		SetDlgItemText(IDC_PICK_BTN,CString("开始采集"));
		MessageBox(_T("已断开设备"));
	}else{
		if (this->m_CZKFPEngX.InitEngine() == 0)
		{
			this->m_CZKFPEngX.put_FPEngineVersion(_T("10"));
			this->m_device_cnn = TRUE;
			SetDlgItemText(IDC_CNN_DEVICE_BTN,_T("断开连接"));
			MessageBox(_T("成功连接设备"));
		} 
		else
		{
			this->m_CZKFPEngX.EndEngine();
			MessageBox(_T("未找到设备."));
		}
	}
}

void CFingerTemplateHelperDlg::OnBnClickedPickBtn()
{
	if(!this->m_device_cnn){
		MessageBox(_T("请先连接设备."));
		return;
	}
	this->m_CZKFPEngX.CancelEnroll();
	this->m_CZKFPEngX.put_EnrollCount(3);
	this->m_CZKFPEngX.BeginEnroll();
	this->EnableButtons(FALSE);
	SetDlgItemText(IDC_PICK_BTN,_T("采集中."));
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
		//发送到服务器保存
		
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
		//继续采集
		this->m_CZKFPEngX.CancelEnroll();
		this->m_CZKFPEngX.put_EnrollCount(3);
		this->m_CZKFPEngX.BeginEnroll();
		//this->EnableButtons(TRUE);
		SetDlgItemText(IDC_TIP_STATIC,_T("采集成功,下一个手指或下一个人"));
		this->m_pick_count = 0;
	}
}

void CFingerTemplateHelperDlg::OnImageReceivedZkfpengx(BOOL* AImageValid)
{
	this->m_pick_count++;
	CString tip;
	tip.Format(_T("采集指纹%d次(按3次即可)"),this->m_pick_count);
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
