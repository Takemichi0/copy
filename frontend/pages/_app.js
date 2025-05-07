import '@/styles/globals.css'
import { ConfigProvider } from 'antd';

export default function App({ Component, pageProps }) {
  return <ConfigProvider
      theme={{
          token: {
              colorPrimary: '#00b96b',
              borderRadius: 6,
              colorBgContainer: '#ffffff',
          },
      }}
  >
      <Component {...pageProps} />
  </ConfigProvider>
}
