import React from 'react';
import { MenuUnfoldOutlined, MenuFoldOutlined } from '@ant-design/icons';

export default function AppHeader({ collapsed, onToggleSidebar, title }) {
    return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 16px', background: '#656565' }}>
            <div onClick={onToggleSidebar} style={{ cursor: 'pointer' }}>
                {collapsed ? <MenuUnfoldOutlined style={{ color: '#fff', fontSize: '20px' }} /> : <MenuFoldOutlined style={{ color: '#fff', fontSize: '20px' }} />}
            </div>
            <span style={{ color: '#fff', fontSize: '20px', padding: '20px' }}>{title}</span>
            <div></div>
        </div>
    );
}
