import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

const bnt = document.getElementById('bnt')
// const con = document.getElementById('con')

const el = React.createElement(
  "button",
  {
    className: "btn",
    type: "submit",
    tabIndex: 0,
    onClick: () => console.log("Нажимается наконец-то клиик "),
  },
  "Заголовок кнопки"
);


const root = ReactDOM.createRoot(bnt);
root.render(el);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
    
  </StrictMode>,

  
)
