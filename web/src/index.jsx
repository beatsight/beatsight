import React,  { Suspense } from 'react';
import ReactDOM from 'react-dom/client'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import './index.css'

import SuspenseContent from './containers/SuspenseContent';
import App from './App.jsx'

import store from './app/store'
import { Provider } from 'react-redux'

// import Dashboard from './components/Dashboard.jsx'
// import Invoices from './components/Invoices.jsx'
// import ErrorPage from './components/ErrorPage.jsx'

// import './fonts/Lusitana-Bold.ttf'
// import './fonts/Lusitana-Regular.ttf'
// import './fonts.css'



// const router = createBrowserRouter([
//   {
//     path: "/",
//     element: <App />,
//     errorElement: <ErrorPage />,
//   },
//   {
//     path: "/dashboard",
//     element: <Dashboard />
//   },
//   {
//     path: "/invoices",
//     element: <Invoices />
//   },
// ]);

const root = ReactDOM.createRoot(document.getElementById('root'))
root.render(
    <Suspense fallback={<SuspenseContent />}>
        <Provider store={store}>
            <App />
        </Provider>
    </Suspense>
)

