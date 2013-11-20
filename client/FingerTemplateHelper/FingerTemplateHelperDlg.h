// FingerTemplateHelperDlg.h : ͷ�ļ�
//

#pragma once
#include "CZKFPEngX.h"
#include "afxwin.h"
#include "Utils.h"

// CFingerTemplateHelperDlg �Ի���
class CFingerTemplateHelperDlg : public CDialog
{
// ����
public:
	CFingerTemplateHelperDlg(CWnd* pParent = NULL);	// ��׼���캯��

// �Ի�������
	enum { IDD = IDD_FINGERTEMPLATEHELPER_DIALOG };

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV ֧��


// ʵ��
protected:
	HICON m_hIcon;

	// ���ɵ���Ϣӳ�亯��
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()
public:
	CZKFPEngX m_CZKFPEngX;
	CEdit m_netkey_editor;
	CButton m_cnn_device_btn;
	CButton m_pick_btn;
public:
	afx_msg void OnBnClickedCnnDeviceBtn();
	afx_msg void OnBnClickedPickBtn();
public:
	bool m_device_cnn;
	int m_pick_count;
public:
	void EnableButtons(bool disabled);
public:
	DECLARE_EVENTSINK_MAP()
public:
	void OnEnrollZkfpengx(BOOL ActionResult, const VARIANT& ATemplate);
	void OnImageReceivedZkfpengx(BOOL* AImageValid);
public:
	afx_msg void OnClose();
public:
	afx_msg void OnEnChangeNetkeyEdit();
};
