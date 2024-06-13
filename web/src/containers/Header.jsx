// import { themeChange } from 'theme-change'
import React, {  useEffect, useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import BellIcon  from '@heroicons/react/24/outline/BellIcon'
import Bars3Icon  from '@heroicons/react/24/outline/Bars3Icon'
import MoonIcon from '@heroicons/react/24/outline/MoonIcon'
import SunIcon from '@heroicons/react/24/outline/SunIcon'
// import { openRightDrawer } from '../features/common/rightDrawerSlice';
// import { RIGHT_DRAWER_TYPES } from '../utils/globalConstantUtil'

import { NavLink,  Routes, Link , useLocation} from 'react-router-dom'

function Header(){

    // const dispatch = useDispatch()
    const {noOfNotifications, pageTitle} = useSelector(state => state.header)
    // const [currentTheme, setCurrentTheme] = useState(localStorage.getItem("theme"))

    // useEffect(() => {
    //     themeChange(false)
    //     if(currentTheme === null){
    //         if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ) {
    //             setCurrentTheme("dark")
    //         }else{
    //             setCurrentTheme("light")
    //         }
    //     }
    //     // 👆 false parameter is required for react project
    //   }, [])


    // // Opening right sidebar for notification
    // const openNotification = () => {
    //     dispatch(openRightDrawer({header : "Notifications", bodyType : RIGHT_DRAWER_TYPES.NOTIFICATION}))
    // }


    // function logoutUser(){
    //     localStorage.clear();
    //     window.location.href = '/'
    // }

    return(
        // navbar fixed  flex-none justify-between bg-base-300  z-10 shadow-md
        
        <>
            <div className="navbar sticky top-0 bg-base-100  z-10 shadow-md ">


                {/* Menu toogle for mobile view or small screen */}
                <div className="flex-1">
                    <label htmlFor="left-sidebar-drawer" className="btn btn-primary drawer-button lg:hidden">
                    <Bars3Icon className="h-5 inline-block w-5"/></label>
                    <h1 className="text-2xl font-semibold ml-2">{pageTitle}</h1>
                </div>

                

            </div>

        </>
    )
}

export default Header
