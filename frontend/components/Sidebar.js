import { Upload } from 'antd';
const { Dragger } = Upload;
import { InboxOutlined } from '@ant-design/icons';
import { Menu, Input, Layout } from 'antd';
import { Button } from 'antd';
const { Search } = Input;

export default function Sidebar({ className, draggerProps, isSiderCollapsed, onSearchSubmit, setSearchInput, menuItems, onMenuItemClick, beginAuth}) {
    const { Sider } = Layout;
    return (
        <div>
        <Sider
            className={className}
            collapsed={isSiderCollapsed}
            collapsedWidth="0"
            onBreakpoint={(broken) => {
                console.log(broken);
            }}
            onCollapse={(collapsed, type) => {
                console.log(collapsed, type);
            }}
        >
            <div className="upload-functions">
                <Dragger {...draggerProps}>
                    <p className="ant-upload-drag-icon">
                        <InboxOutlined />
                    </p>
                    <p className="ant-upload-text-inside-bar">PDFをドラッグ</p>
                </Dragger>
            </div>
            <div className="search_box">
                <Input.Search
                    size="large"
                    placeholder="arxivのURL"
                    allowClear
                    onSearch={value => {
                        setSearchInput(value);
                        onSearchSubmit(value);
                    }}
                />
            </div>
            <div className="mt-1 pr-1">
                <Menu mode="inline">
                    {menuItems.map((item, index) => (
                        <Menu.Item key={index} onClick={() => onMenuItemClick(item)}>
                            {item}
                        </Menu.Item>
                    ))}
                </Menu>
            </div>
            <div className="add_to_slack">
                <Button onClick={() => beginAuth()}>add to slack</Button>
            </div>
        </Sider>
        </div>
    );
}

