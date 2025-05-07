import React, {useEffect, useState} from 'react';
import {Layout, theme} from 'antd';
import Sidebar from '../components/Sidebar';
import ChatList from '../components/ChatList';
import MessageInput from '../components/MessageInput';
import AppHeader from '../components/AppHeader';
import {getAuth, GoogleAuthProvider, onAuthStateChanged, signInWithPopup} from "firebase/auth";
import axios from 'axios';
import {initializeApp} from "firebase/app";

const provider = new GoogleAuthProvider();
const dummyChatData = [];

const firebaseConfig = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_PUBLIC_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
const auth = getAuth(app);


function auth_check(setIsLogined, setToken) {
    return signInWithPopup(auth, provider)
        .then((result) => {
            const credential = GoogleAuthProvider.credentialFromResult(result);
            const token = credential.accessToken;
            const user = result.user;
            user.getIdToken().then(function (idToken) {
                    setToken(idToken);
                    setIsLogined(true);
                });
        }).catch((error) => {
            const errorCode = error.code;
            const errorMessage = error.message;
            const credential = GoogleAuthProvider.credentialFromError(error);
            console.log(error);
            // ...
        });
}

function extractAndValidateArxivId(url) {
    const re = /^https?:\/\/arxiv\.org\/abs\/((\d{4}\.\d{5})|(hep-th\/\d{7}))$/;
    const match = url.match(re);

    if (match) {
        const id = match[1].replace('hep-th/', '');
        return {
            valid: true,
            arxivId: id
        };
    } else {
        return {
            valid: false,
            arxivId: null
        };
    }
}

const props = {
    // name: 'file',
    // multiple: false,
    // action: 'https://localhost:8000/upload',
    // onChange(info) {
    //     const { status } = info.file;
    //     if (status !== 'uploading') {
    //         console.log(info.file, info.fileList);
    //     }
    //     if (status === 'done') {
    //         message.success(`${info.file.name} file uploaded successfully.`);
    //     } else if (status === 'error') {
    //         message.error(`${info.file.name} file upload failed.`);
    //     }
    // },
    // onDrop(e) {
    //     console.log('Dropped files', e.dataTransfer.files);
    // },
};


export default function Home() {
    const {Content} = Layout;
    const [collapsed, setCollapsed] = useState(false);
    const [chatData, setChatData] = useState(dummyChatData);
    const [inputValue, setInputValue] = useState("");
    const [searchInput, setSearchInput] = useState("");
    const [menuItems, setMenuItems] = useState([]);
    const [threadId, setThreadId] = useState(null);
    const [islogined, setIsLogined] = useState(false);
    const [token, setToken] = useState("");
    const {
        token: {colorBgContainer},
    } = theme.useToken();
    const siderClass = collapsed ? 'hidden' : '';

    const handleSendMessage = () => {
        setChatData(prevData => [...prevData, {message: inputValue, type: 'sent'}]);
        setInputValue('');
    };

    function islogined_func() {
        return onAuthStateChanged(auth, (user) => {
            if (user) {
                user.getIdToken().then(function (idToken) {
                    setToken(idToken);
                    setIsLogined(true);
                });
            }
        })
    }

    useEffect(() => {
        islogined_func();
    }, [setIsLogined])

    const handleSearchSubmit = (searchedValue) => {
        try {
            if (searchedValue === "") {
                return;
            }
            if (extractAndValidateArxivId(searchedValue).valid === false) {
                alert("mistake format");
                return;
            }
            alert("Waiting backend server");
            axios.put('https://arxiv-questions-zscn3dmucq-an.a.run.app/process_pdf/', {url: searchedValue}, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            }).then(() => {
                let thread_id = extractAndValidateArxivId(searchedValue).arxivId
                setMenuItems([...menuItems, thread_id]);
                setThreadId(thread_id);
            })
        } catch (error) {
            console.error("Error during search submit:", error);
        }
    };

    const handleMenuItemClick = async (inputText) => {
        try {
            const response = await axios.put('https://arxiv-questions-zscn3dmucq-an.a.run.app/ask_question/', {
                arxiv_id: threadId,
                question_text: inputText
            }, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            setChatData(prevData => [...prevData, {message: response.data.answer, type: 'received'}]);
        } catch (error) {
            console.error("Error during menu item click:", error);
        }
    };

    useEffect(() => {
        if (inputValue !== "") {
            handleSendMessage();
        }
    }, [inputValue]);


    const beginAuth = async () => {
        try {
            const response = await axios.get('http://localhost:8000/begin_auth');
            // response.dataにはHTMLが含まれるため、適切な方法で表示する必要があります。
            console.log(response.data);
            const elementWithClass = document.querySelector('.add_to_slack');
            if (elementWithClass) {
                elementWithClass.innerHTML += response.data;
            }
        } catch (error) {
            console.error('Error during begin_auth:', error);
        }
    };


    return (
        <Layout>
            {islogined === false ? <button id="auth_button" onClick={(event) => {
                event.preventDefault();
                auth_check(setIsLogined, setToken);
            }}>ログイン</button> : (
                <Layout>
                    <Sidebar className={siderClass} draggerProps={props} isSiderCollapsed={collapsed}
                             onSearchSubmit={handleSearchSubmit}
                             setSearchInput={setSearchInput} menuItems={menuItems}
                             onMenuItemClick={() => console.log("search submit")}
                             beginAuth={() => {beginAuth()}}
                             />
                    <Layout>
                        <AppHeader
                            title="Algo Summarization"
                            collapsed={collapsed}
                            onToggleSidebar={() => {
                                setCollapsed(!collapsed);
                            }}
                        />
                        <Content className="content-wrapper">
                            <ChatList data={chatData}/>
                            <div>
                                <MessageInput setInputValue={setInputValue}
                                              onSendMessage={(message) => {
                                                  handleMenuItemClick(message);
                                              }}/>
                            </div>
                        </Content>
                    </Layout>
                </Layout>
            )}
        </Layout>
    );
};
