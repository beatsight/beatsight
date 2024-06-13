import React, { lazy, useEffect } from 'react'
import './App.css';
import { BrowserRouter as Router, Route, Routes, Navigate  } from 'react-router-dom'
// import { themeChange } from 'theme-change'


// Importing pages
const Layout = lazy(() => import('./containers/Layout'))
const Login = lazy(() => import('./pages/Login'))
const ErrorPage = lazy(() => import('./pages/protected/404'))


export default function App() {
  // useEffect(() => {
  //   // 👆 daisy UI themes initialization
  //   themeChange(false)
  // }, [])
  
  return (
      <>
      <Router>
        <Routes>

          <Route path="/" element={<Navigate to="/projects" replace />} />
          <Route path="/login" element={<Login />} />

          <Route path="/*" element={<Layout />} />
          {/* <Route path="/developers/\*" element={<Layout />} /> */}

          {/* <Route path="*" element={<ErrorPage />}/> */}

        </Routes>
      </Router>
      </>
  );

}

