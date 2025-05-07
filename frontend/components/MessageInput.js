import { Button, Input } from 'antd';
import React, {useState, useEffect} from 'react';
const { TextArea } = Input;

function MessageInput({setInputValue, onSendMessage }) {
    const [message, setMessage] = useState('');
    const handleButtonClick = () => {
        if (message === '') {
            return;
        }
        setInputValue(message);
        onSendMessage(message);
        setMessage('');
    };

    return (
        <div style={{ position: 'absolute',
            left: '50%',
            transform: 'translateX(-50%)',
            WebkitTransform: 'translateX(-50%)',
            boxShadow: "2px 1px 12px 1px rgb(138 138 138 / 13%)",
            borderRadius: "8px",
            msTransform: 'translateX(-50%)', bottom: '4%', width: '90%', zIndex: 100, background: '#fff' }}>
            <TextArea
                size={'large'}
                value={message}
                autoSize={{ minRows: 1, maxRows: 6 }}
                onChange={(e) => setMessage(e.target.value)}
            />
            <Button type="primary" onClick={handleButtonClick} style={{ position: 'absolute', right: 5, bottom: 4 }}>送信</Button>
        </div>
    );
}

export default MessageInput;
