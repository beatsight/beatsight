import React from 'react'
import ReactDOM from 'react-dom/client'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

import App from './App.jsx'
import Dashboard from './components/Dashboard.jsx'
import Invoices from './components/Invoices.jsx'
import ErrorPage from './components/ErrorPage.jsx'

// import './fonts/Lusitana-Bold.ttf'
// import './fonts/Lusitana-Regular.ttf'
// import './fonts.css'

import './main.css'

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <ErrorPage />,
  },
  {
    path: "/dashboard",
    element: <Dashboard />
  },
  {
    path: "/invoices",
    element: <Invoices />
  },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)

