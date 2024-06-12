import { useEffect } from 'react'
// import { useDispatch } from 'react-redux'
// import { setPageTitle } from '../../features/common/headerSlice'
// import Dashboard from '../../features/dashboard/index'

function Dashboard(){

  return (
    <>

    <div className="grid lg:grid-cols-4 mt-2 md:grid-cols-2 grid-cols-1 gap-6">
      <p>Dashboard </p>
    </div>

    </>
  )
}

function InternalPage(){
    // const dispatch = useDispatch()

    // useEffect(() => {
    //     // dispatch(setPageTitle({ title : "Dashboard"}))
    //   }, [])


    return(
        <Dashboard />
    )
}

export default InternalPage
