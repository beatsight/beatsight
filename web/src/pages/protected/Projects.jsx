import { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import { setPageTitle } from '../../features/common/headerSlice'
import Projects from '../../features/projects/index'


function InternalPage(){
    const dispatch = useDispatch()

    useEffect(() => {
        dispatch(setPageTitle({ title : "Projects"}))
      }, [])


    return(
        <Projects />
    )
}

export default InternalPage
