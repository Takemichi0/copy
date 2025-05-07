import { List, Input } from 'antd';
const { TextArea } = Input;
function ChatList({ data }) {
    return (
        <List
            dataSource={data}
            renderItem={item => (
                <List.Item style={{
                    justifyContent: item.type === 'sent' ? 'flex-end' : 'flex-start'
                }}>
                    <TextArea
                        className="message"
                        size={'large'}
                        value={item.message}
                        autoSize={true}
                        readOnly
                        style={{
                            maxWidth: '70%',
                            borderRadius: 15,
                            background: item.type === 'sent' ? '#e6f7ff' : '#fff',
                            padding: '3px 16px',
                        }}
                    />
                </List.Item>
            )}
            style={{ overflow: 'auto', maxHeight: 'calc(100vh - 160px)' }}
        />
    );
}

export default ChatList;
