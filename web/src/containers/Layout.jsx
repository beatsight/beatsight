import PageContent from "./PageContent"
import LeftSidebar from "./LeftSidebar"

function Layout(){
  // const dispatch = useDispatch()
  // const {newNotificationMessage, newNotificationStatus} = useSelector(state => state.header)


  // useEffect(() => {
  //     if(newNotificationMessage !== ""){
  //         if(newNotificationStatus === 1)NotificationManager.success(newNotificationMessage, 'Success')
  //         if(newNotificationStatus === 0)NotificationManager.error( newNotificationMessage, 'Error')
  //         dispatch(removeNotificationMessage())
  //     }
  // }, [newNotificationMessage])

    return(
      <>
        { /* Left drawer - containing page content and side bar (always open) */ }
        <div className="drawer  lg:drawer-open">
            <input id="left-sidebar-drawer" type="checkbox" className="drawer-toggle" />
            <PageContent/>
            <LeftSidebar />
        </div>

        {/* { /\* Right drawer - containing secondary content like notifications list etc.. *\/ } */}
        {/* <RightSidebar /> */}


        {/* {/\** Notification layout container *\/} */}
        {/* <NotificationContainer /> */}

      {/* {/\* Modal layout container *\/} */}
      {/*   <ModalLayout /> */}

      </>
    )
}

export default Layout
